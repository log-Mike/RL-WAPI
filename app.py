from flask import Flask, g, jsonify, redirect, render_template, request, url_for
from flask_mysqldb import MySQL

try:
    import config
except ImportError as e:
    print('''Error with config file, should be a python (.py) file in format of:
        MYSQL_HOST = "sql_db_host"
        MYSQL_USER = "sql_db_user"
        MYSQL_PASSWORD = "sql_db_pwd"
        MYSQL_DB = "sql_db_name"
        MYSQL_PORT = "sql_db_port"''')
    raise SystemExit(e)

app=Flask(__name__)

app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
app.config['MYSQL_PORT'] = int(config.MYSQL_PORT)

app.config['API_KEY'] = config.API_KEY

db = MySQL(app)

@app.teardown_appcontext
def close_mysql(exception):
    # if connection isn't closed
    # on app being closed, close it
    if getattr(g, '_mysql_db', None) is not None:
        db.close()

def get_table_data_and_columns(cur):
    try:
        # for showing table
        cur.execute('show columns from network')
        cols = cur.fetchall()[1:]

        cur.execute('select name, coalesce(user, "User not assigned") as user from network order by 1')
        table = cur.fetchall()

        return table, cols

    except Exception as e:
        raise e

def authenticate_api(given_key):
    return given_key == app.config['API_KEY']

 
@app.route('/process-table-update', methods=['POST'])
def select_done():
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
        
        # start transaction
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
    
@app.route('/api/<string:action>')
def handle_request(action):
    api_key = request.headers.get('API-KEY')

    if not authenticate_api(api_key):
        return str(-1)
        
    network = request.args.get('network')
    
    try:
        cur = db.connection.cursor()
        if action == 'lock':
            # start transaction
            cur.execute('update network set user = NULL'
            + ' where name = "' + network + '"')
                
            num_updated = cur.rowcount

            db.connection.commit() 
            return 'Locking network'

        elif action == 'checklock':
            # Handle checklock action
            return f'Checking lock for network: {network}, Additional parameters: {additional_parameters}'

        elif action == 'unlock':
            # Handle unlock action
            return f'Unlocking network: {network}, Additional parameters: {additional_parameters}'
        else:
            return "this does nothing!"
            
        num_updated = cur.rowcount

        db.connection.commit()        
        
        return str(num_updated)
    except Exception as e:
        return str(-1)
    finally:
        cur.close()


@app.route('/')
def start():
    return render_template('index.html')
    
@app.route('/process-login-request', methods=['POST'])
def login():
    # can now use in backend like 
    # validating
    user = request.form.get('username')
    password = request.form.get('pswrd')

    '''
    validate password through ldap
    
    
    
    
    
    
    
    '''
    
    try:
        cur = db.connection.cursor()
        cur.execute('select access_permission from userInfo where username=%s', (user,))
        permission = cur.fetchone()[0]
    except Exception as e:
        return render_template('error.html', 
                msg='An error occurred: ' + str(e)) 
    finally:
        cur.close()
        
    return redirect(url_for('select_page_admin' if 
    permission == 'admin' else 'select_page_user'))
  

  
@app.route('/allocate')
def select_page_admin():
    try:
        cur = db.connection.cursor()

        # for dropdowns
        cur.execute('select username from userInfo order by 1')
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

        return render_template('view.html', data=table, columns=cols)

    except Exception as e:
        return render_template('error.html', msg='An error occurred: ' + str(e))

    finally:
        cur.close()
    

# for development run it on local in debug mode

# waitress could be a could option for later
# waitress has a command line interface too,
# not sure if that can be used for our CLI as well
if __name__=='__main__':
    app.run(debug=True)