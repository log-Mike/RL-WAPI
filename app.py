from flask import Flask,g,jsonify,redirect,render_template,request,url_for
from flask_mysqldb import MySQL

try:
    import config
except ImportError as e:
    print('''Error with configuration file
        should be a python file: config.py in format of:
        MYSQL_HOST = "sql_db_host"
        MYSQL_USER = "sql_db_user"
        MYSQL_PASSWORD = "sql_db_pwd"
        MYSQL_DB = "sql_db_name"
        MYSQL_PORT = "sql_db_port"
        API_KEY = 'single_api_key'
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

app.config['NO_USER_MSG'] = 'User not assigned'

db = MySQL(app)

@app.teardown_appcontext
def close_mysql(exception):
    # if connection isn't closed
    # on app being closed, close it
    if getattr(g, '_mysql_db', None) is not None:
        db.close()

def get_table_data_and_columns(cur):
    try:
        cur.execute('''select name,
        coalesce(user, "User not assigned")
        as 'assigned user',
        date_updated as 'last modified'
        from network
        order by 1''')
        
        
        return cur.fetchall(),\
        [col[0] for col in cur.description]

    except Exception as e:
        raise e

def auth_key(given_key):
    return given_key == app.config['API_KEY']

    
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
        cur = db.connection.cursor()
        
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
        return result
    except Exception as e:
        return str(e)
    finally:
        cur.close()


@app.route('/')
def start():
    return render_template('index.html')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        #if already logged in:
        #    return redirect{dashboard}
        return render_template('login.html')
    else:
        user = request.form.get('username')
        password = request.form.get('pswrd')

        '''
        validate password through ldap
        '''
        
        try:
            cur = db.connection.cursor()
            cur.execute('''select access_permission
            from userInfo
            where username=%s''',(user,))
            permission = cur.fetchone()[0]
        except Exception as e:
            return render_template('error.html', 
                    msg='An error occurred: ' + str(e)) 
        finally:
            cur.close()
            
        return redirect(url_for('select_page_admin' if 
        permission == 'admin' else 'select_page_user'))
    
@app.route('/allocate', methods=['GET', 'PATCH'])
def select_page_admin():
    if request.method == 'PATCH':
        user = request.form.get('user')
        network = request.form.get('network')
        
        try:
            cur = db.connection.cursor()
            
            if user == 'del_user':
                set_to = 'NULL'
                update_to = "User not assigned"
            else:
                set_to = '"' + user + '"'
                update_to = user
            
            cur.execute('update network set user = ' + set_to 
            + ' where name = "' + network + '"')
                
            num_updated = cur.rowcount

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
        finally:
            cur.close()   
    else:        
        try:
            cur = db.connection.cursor()

            # for dropdowns
            cur.execute('''select username
            from userInfo
            order by 1''')
            avail_users = cur.fetchall()
            
            cur.execute('select name from network order by 1')
            avail_networks = cur.fetchall()
            
            table, cols = get_table_data_and_columns(cur)

            return render_template('select.html', 
            column1_values=avail_users, 
            column2_values=avail_networks, 
            data=table, 
            columns=cols)

        except Exception as e:
            return render_template('error.html', 
            msg='An error occurred: ' + str(e))

        finally:
            cur.close()

@app.route('/view')
def select_page_user():
    try:
        cur = db.connection.cursor()
        
        table, cols = get_table_data_and_columns(cur)

        return render_template('view.html',
        data=table, columns=cols)

    except Exception as e:
        return render_template('error.html',
        msg='An error occurred: ' + str(e))

    finally:
        cur.close()

# for development run it on local in debug mode
if __name__=='__main__':
    app.run(debug=True)