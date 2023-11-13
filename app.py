from flask import Flask,jsonify,redirect,render_template,request,url_for
from flask_mysqldb import MySQL

try:
    import config
except ImportError as e:
    print('''Error with configuration file
        should be a python file: config.py with variables:
        MYSQL_HOST = "sql_db_host"
        MYSQL_USER = "sql_db_user"
        MYSQL_PASSWORD = "sql_db_pwd"
        MYSQL_DB = "sql_db_name"
        MYSQL_PORT = "sql_db_port"
        API_KEY = "single_api_key"
        SECRET_KEY = "secret_key"
        ''')
    raise SystemExit(e)

app=Flask(__name__)

app.config['SECRET_KEY'] = config.SECRET_KEY

app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
app.config['MYSQL_PORT'] = int(config.MYSQL_PORT)

app.config['API_KEY'] = config.API_KEY

# get_tables_and_columns
app.config['NO_USER_MSG'] = 'User not assigned'

db = MySQL(app)

def auth_key(given_key):
    return given_key == app.config['API_KEY']
    
def get_table_and_columns(cur):
    try:
        cur.execute('''SELECT name, COALESCE(user, 'User not assigned') AS assigned_user,
                CASE
                    WHEN TIMESTAMPDIFF(SECOND, date_updated, NOW()) < 60 THEN
                        CONCAT(TIMESTAMPDIFF(SECOND, date_updated, NOW()), ' seconds ago')
                    WHEN TIMESTAMPDIFF(MINUTE, date_updated, NOW()) < 60 THEN
                        CONCAT(TIMESTAMPDIFF(MINUTE, date_updated, NOW()), ' minutes ago')
                    WHEN TIMESTAMPDIFF(HOUR, date_updated, NOW()) < 24 THEN
                        CONCAT(
                            TIMESTAMPDIFF(HOUR, date_updated, NOW()),
                            ' hours ',
                            TIMESTAMPDIFF(MINUTE, date_updated, NOW()) % 60,
                            ' minutes ago'
                        )
                    ELSE DATE_FORMAT(date_updated, '%m/%d/%y %h:%i %p')
                END AS last_modified
            FROM network
            ORDER BY 1''')

        return cur.fetchall(), [col[0] for col in cur.description]


    except Exception as e:
        raise e

    
# result is currently just want happened. need to 
# change result(return value) to actual output for client
@app.route('/api/<string:action>')
def handle_request(action):
    
    api_key = request.headers.get('API-KEY')

    if not auth_key(api_key):
        return 'bad api key'
   
    result = 'an error occured.'

    try:
        input = request.args.get('input')
        try:
            with db.connection.cursor() as cursor:
                
                # set any free network to given user
                # should this have some sort of distribution?
                # should it be completely random ?
                # assumes a user has to be in user table
                # to be assigned to a network
                if action == 'lock':
                
                    # verifying existance
                    cur.execute('select 0 from userInfo '
                    + 'where username="' + input + '"')
                    
                    found = cur.rowcount
                    
                    if found == 0:
                        result = 'No matching user'
                    elif found != 1:
                        result = 'More than one matching'
                        + 'user record found'
                    else:
                        cur.execute('''select name
                        from network
                        where user is NULL
                        limit 1''')
                         
                        # found no networks with a null user
                        if cur.rowcount == 0:
                            result = 'No free networks'
                        else:
                            picked = cur.fetchone()[0]                
                            cur.execute('''update network
                            set user ="''' + input
                            + '" where name ="' + picked + '"')
                            
                            found = cur.rowcount
                            
                            if found != 1:
                                result = 'problem updating db'
                            else:                
                                result = '%s locked to %s' \
                                % (input, picked)

                                db.connection.commit()                         
                    
                # return status of a given network
                elif action == 'checklock':
                    cur.execute('''select user
                    from network
                    where name ="''' + input + '"')
                    
                    found = cur.rowcount
                    
                    if found == 0:
                        result = 'No matching row found'
                    elif found != 1:
                        result = 'More than one record found '
                        + 'in db matching the network name'
                    else:
                        assigned_user = cur.fetchone()[0]
                        result = input + ' is '
                        
                        if assigned_user is None:
                            result += 'unlocked'
                        else:
                            result += 'locked by %s' %(assigned_user)
                            
                # set given network's user to null
                elif action == 'unlock':
                    cur.execute('update network set user = NULL'
                    + ' where name = "' + input + '"')
                    
                    found = cur.rowcount
                    
                    if found == 0:
                        result = 'No matching network found'
                    elif found != 1:
                        result = 'More than one matching network '
                        + 'found, update transaction rollbacked'
                    else:
                        result = input + ' unlocked'
                        db.connection.commit()
                else:
                    result = 'that action does nothing'

        except Exception as e:
            return str(e)
    except Exception as e:
        return str(e)
        
    return result
    
@app.route('/')
def start():
    return render_template('index.html')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #if already logged in:
        #    return redirect{dashboard}
        user = request.form.get('username')
        password = request.form.get('pswrd')

        '''
        validate password through ldap
        '''
        
        try:
            with db.connection.cursor() as cur:
                cur.execute('''select access_permission
                from userInfo
                where username=%s''',(user,))
                permission = cur.fetchone()[0]
        except Exception as e:
            return render_template('error.html', 
                    msg='An error occurred: ' + str(e)) 
            
        return redirect(url_for('select_page_admin' if 
        permission == 'admin' else 'select_page_user'))
    else:
        return render_template('login.html')
    
@app.route('/allocate', methods=['GET', 'PATCH'])
def select_page_admin():
    if request.method == 'PATCH':
        user = request.form.get('user')
        network = request.form.get('network')
        
        try:
            with db.connection.cursor() as cur:                
                if user == 'del_user':
                    set_to = 'NULL'
                    update_to = app.config['NO_USER_MSG']
                else:
                    set_to = '"' + user + '"'
                    update_to = user
                
                cur.execute('update network set user = ' + set_to 
                + ' where name = "' + network + '"')
                 
                
                num_updated = cur.rowcount
                
                if num_updated == 1:
                    db.connection.commit()

                return jsonify({
                    'num_updated' : num_updated,
                    'network': network,
                    'user': update_to
                })
        except Exception as e:
            return jsonify({
                'error': 'An error occurred: ' + str(e)
            }) 
    else:        
        #try:
        with db.connection.cursor() as cur:

            # for dropdowns
            cur.execute('''select username
                from userInfo
                order by 1''')
            avail_users = cur.fetchall()
                
            cur.execute('select name from network order by 1')
            avail_networks = cur.fetchall()
                
            table, cols = get_table_and_columns(cur)

            return render_template('select.html', 
                column1_values=avail_users, 
                column2_values=avail_networks, 
                data=table,
                columns=cols)

        #except Exception as e:
        #    return render_template('error.html', 
         #   msg='An error occurred: ' + str(e))

@app.route('/view')
def select_page_user():
    try:
        with db.connection.cursor() as cur:        
            table, cols = get_table_and_columns(cur)

            return render_template('view.html',
            data=table,
            columns=cols)

    except Exception as e:
        return render_template('error.html',
        msg='An error occurred: ' + str(e))

# for development run it on local in debug mode
if __name__=='__main__':
    app.run(debug=True)