from flask import Flask, render_template, request
from flask_mysqldb import MySQL

app=Flask(__name__)

app.config['MYSQL_HOST'] = 'elvis.rowan.edu'
app.config['MYSQL_USER'] = 'essiga27'
app.config['MYSQL_PASSWORD'] = '1Happygnome!'
app.config['MYSQL_DB'] = 'essiga27'

db = MySQL(app)


@app.route('/allocate/f', methods=['POST'])
def allocate_f():
    user = request.form.get('user')
    network = request.form.get('network')
    
    cur = db.connection.cursor()    
    # update db
       
       
    cur.close()
    
    return user + " assigned to " + network

@app.route('/allocate')
def select_page():
    cur = db.connection.cursor()
    
    cur.execute("select username from user")
    column1_values = cur.fetchall()
    
    cur.execute("select name from network")
    column2_values = cur.fetchall()
    
    cur.close()
    return render_template('select.html', column1_values=column1_values, column2_values=column2_values)


@app.route('/login', methods=['POST'])
def login():
    # can now use in backend like 
    # validating
    user = request.form.get('username')
    password = request.form.get('pswrd')
    
    return "You entered " + user + " & " + password
    
@app.route('/avail')
def print_resources():
    try:
        table_to_query = "network"
        cursor = db.connection.cursor()

        cursor.execute("select * from " + table_to_query)
        table = cursor.fetchall()

        cursor.execute("show columns from " + table_to_query)
        cols = cursor.fetchall()
        cursor.close()
        
        # render the new template (html file)
        # pass in the table as data to q_results
        # make the table look pretty in q_results 
        # file with js, css
        return render_template('avail.html', data=table, columns=cols)
    except Exception as e:
        return render_template('avail_error.html', 
            msg="An error occurred: " + str(e))



@app.route('/')
def start():
    return render_template('index.html')
    

# for development run it on local in debug mode
# waitress could be a could option for later
# apparently waitress has a command line interface too,
# not sure if that can be used for our CLI as well
if __name__=='__main__':
    # might need this later when updating db
    # with app.app_context():
    
    app.run(debug=True)
