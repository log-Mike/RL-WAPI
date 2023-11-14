from flask import Flask,jsonify,redirect,render_template,request,url_for
from flask_mysqldb import MySQL

app=Flask(__name__)

try:
    app.config.from_pyfile('config.py')
except FileNotFoundError as e:
    raise SystemExit('''No config file found
        should be a python file: /config.py with variables:
        
        MYSQL_HOST = "sql_db_host"
        MYSQL_USER = "sql_db_user"
        MYSQL_PASSWORD = "sql_db_pwd"
        MYSQL_DB = "sql_db_name"
        MYSQL_PORT = {port_number}
        
        API_KEY = "single_api_key"
        SECRET_KEY = "secret_key"
        
        An API & a Secret key can be 
        generated with
        python gen_key.py secret
        python gen_key.py api
        ''')



#app.config.from_object(config)


# get_tables_and_columns
app.config['NO_USER_MSG'] = 'User not assigned'

db = MySQL(app)

def auth_key(given_key):
    return given_key == app.config['API_KEY']
    
def get_table_and_columns(cur):
    try:
        cur.execute('''select name, coalesce(user, 'User not assigned'),
                case
                    when timestampdiff(second, date_updated, now()) < 60 then
                        concat(timestampdiff(second, date_updated, now()), ' seconds ago')
                    when timestampdiff(minute, date_updated, now()) < 60 then
                        concat(timestampdiff(minute, date_updated, now()), ' minutes ago')
                    when timestampdiff(hour, date_updated, now()) < 24 then
                        concat(
                            timestampdiff(hour, date_updated, now()),
                            ' hours ',
                            timestampdiff(minute, date_updated, now()) % 60,
                            ' minutes ago'
                        )
                    else date_format(date_updated, '%m/%d/%y %h:%i %p')
                end
            from network
            order by 1''')

        return cur.fetchall(), ('Network', 'Assigned User', 'Last updated')


    except Exception as e:
        raise e

# set any free network to given user
# should this have some sort of distribution?
# assumes a user has to be in user table
# else says bad input
# to be assigned to a network
def lock(cur, user):
                    
    # verifying existance
    cur.execute('select 0 from userInfo '
    + 'where username="' + user + '"')
                    
    found = cur.rowcount
                    
    if found == 0:
        result = 'No matching user'
    elif found != 1:
        result = 'More than one matching user record found'
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
                            set user ="''' + user
                            + '" where name ="' + picked + '"')
                            
            found = cur.rowcount
                            
            if found != 1:
                result = 'problem updating db'
            else:                
                result = '%s locked to %s' % (user, picked)
                db.connection.commit()
                
    return result

# set given network's user to null
def unlock(cur, network):
    cur.execute('update network set user = NULL'
    + ' where name = "' + network + '"')
                    
    found = cur.rowcount
                    
    if found == 0:
        result = 'No matching network found'
    elif found != 1:
        result = 'More than one matching network '
        + 'found, update transaction rollbacked'
    else:
        result = network + ' unlocked'
        db.connection.commit()
        
    return result
                                                
# return status of a given network
def checklock(cur, network):
    cur.execute('''select user
                    from network
                    where name ="''' + network + '"')
                    
    found = cur.rowcount
                    
    if found == 0:
        result = 'No matching row found'
    elif found != 1:
        result = 'More than one record found in db matching the network name'
    else:
        assigned_user = cur.fetchone()[0]
        result = network + ' is '
        if assigned_user is None:
            result += 'unlocked'
        else:
            result += 'locked by %s' % (assigned_user)
            
    return result
    
# result is currently just want happened. need to 
# change result(return value) to actual output for client
@app.route('/api/<string:action>', methods=['GET', 'PATCH'])
def handle_request(action):
    
    api_key = request.headers.get('API-KEY')

    if not auth_key(api_key):
        return 'bad api key'
   
    result = 'an error occured!'

    try:
        input = request.args.get('input')
        try:
            with db.connection.cursor() as cur:
                method = request.method
                err_msg = 'request and action not recgonized'
                
                if method == 'PATCH':
                    if action == 'lock':
                        result = lock(cur, input)
                    elif action == 'unlock':
                        result = unlock(cur, input)
                    else:
                        result = err_msg
                elif method == 'GET' and action == 'checklock':
                    result = checklock(cur, input)
                else:
                    result = err_msg

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
        try:
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

        except Exception as e:
            return render_template('error.html', 
            msg='An error occurred: ' + str(e))

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