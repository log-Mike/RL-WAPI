from flask import Flask, g, jsonify, redirect, render_template, request, url_for
from flask_mysqldb import MySQL

import config

app=Flask(__name__)

app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
app.config['MYSQL_PORT'] = int(config.MYSQL_PORT)

db = MySQL(app)

@app.teardown_appcontext
def close_mysql(exception):
    # if connection isn't closed
    # on app being closed, close it
    if getattr(g, '_mysql_db', None) is not None:
        db.close()
   
@app.route('/allocate/f', methods=['POST'])
def select_done():
    user = request.form.get('user')
    network = request.form.get('network')
    
    try:
        cur = db.connection.cursor()
        
        # start transaction
        cur.execute("update network set user = '" + user 
        + "' where name = '" + network + "'")
            
        num_updated = cur.rowcount

        db.connection.commit()
        
        return jsonify({
            'num_updated' : num_updated,
            'network': network,
            'user': user
        })
    except Exception as e:
        return jsonify({
            'error': 'An error occurred: ' + str(e)
        })
    finally:
        cur.close()
    
@app.route('/allocate')
def select_page_admin():
    try:
        # for showing table
        cur = db.connection.cursor()
        
        cur.execute('show columns from network')
        cols = cur.fetchall()[1:]
        
        cur.execute('select name, user from network order by 1')
        table = cur.fetchall()


        # for dropdowns
        cur.execute('select username from userInfo order by 1')
        avail_users = cur.fetchall()
        
        cur.execute('select name from network order by 1')
        avail_networks = cur.fetchall()
        
        return render_template('select.html', column1_values=avail_users, 
        column2_values=avail_networks, data=table, columns=cols)

    except Exception as e:
        return render_template('error.html', 
                msg='An error occurred: ' + str(e)) 
    finally:
        cur.close()

@app.route('/view')
def select_page_user():
    try:
        # for showing table
        cur = db.connection.cursor()
        
        cur.execute('show columns from network')
        cols = cur.fetchall()[1:]
        
        cur.execute('select name, user from network order by 1')
        table = cur.fetchall()

        return render_template('view.html', data=table, columns=cols)

    except Exception as e:
        return render_template('error.html', 
                msg='An error occurred: ' + str(e)) 
    finally:
        cur.close()

@app.route('/home', methods=['POST'])
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
    
    if permission == 'admin':
        result_route = 'select_page_admin'
    else: 
        result_route = 'select_page_user'
        
    return redirect(url_for(result_route))
  
@app.route('/')
def start():
    return render_template('index.html')
    

# for development run it on local in debug mode

# waitress could be a could option for later
# waitress has a command line interface too,
# not sure if that can be used for our CLI as well
if __name__=='__main__':
    app.run(debug=True)