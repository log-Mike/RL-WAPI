from flask import Flask, render_template, request, g
from flask_mysqldb import MySQL

app=Flask(__name__)

app.config['MYSQL_HOST'] = 'elvis.rowan.edu'
app.config['MYSQL_USER'] = 'essiga27'
app.config['MYSQL_PASSWORD'] = '1Happygnome!'
app.config['MYSQL_DB'] = 'essiga27'

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
        cur.execute("update network set user = \'" + user 
        + "\' where name = \'" + network + "\'")
        
        # commit transaction
        db.connection.commit()
        
        return render_template('finish.html', user=user, network=network,
        msg=("NOT" if cur.rowcount == 0 else "IS")+" SUCCESSFUL")
    
    except Exception as e:
        return render_template('error.html', 
                msg="An error occurred: " + str(e))
    finally:
        cur.close()
    
@app.route('/allocate')
def select_page():
    try:
        # for showing table
        cur = db.connection.cursor()
        
        cur.execute("show columns from network")
        cols = cur.fetchall()[1:]
        
        cur.execute("select name, user from network order by 1")
        table = cur.fetchall()


        # for dropdowns
        cur.execute("select username from user order by 1")
        avail_users = cur.fetchall()
        
        cur.execute("select name from network order by 1")
        avail_networks = cur.fetchall()
        
        return render_template('select.html', column1_values=avail_users, 
        column2_values=avail_networks, data=table, columns=cols)

    except Exception as e:
        return render_template('error.html', 
                msg="An error occurred: " + str(e)) 
    finally:
        cur.close()

@app.route('/home', methods=['POST'])
def login():
    # can now use in backend like 
    # validating
    user = request.form.get('username')
    password = request.form.get('pswrd')
    
    return render_template("home.html")
  

@app.route('/')
def start():
    return render_template('index.html')
    

# for development run it on local in debug mode

# waitress could be a could option for later
# waitress has a command line interface too,
# not sure if that can be used for our CLI as well
if __name__=='__main__':
    app.run(debug=True)