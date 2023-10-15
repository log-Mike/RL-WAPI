from flask import Flask, render_template, request
from flask_mysqldb import MySQL

app=Flask(__name__)

app.config['MYSQL_HOST'] = 'elvis.rowan.edu'
app.config['MYSQL_USER'] = 'essiga27'
app.config['MYSQL_PASSWORD'] = '1Happygnome!'
app.config['MYSQL_DB'] = 'essiga27'

db = MySQL(app)

@app.route('/allocate', methods=['POST'])
def process_form():
    # can now use in backend like 
    # validating
    var1 = request.form.get('ui1')
    var2 = request.form.get('ui2')
    
    return "You entered " + str(var1) + " & " + str(var2)
    
@app.route('/avail')
def print_resources():
    try:
        table_to_query = "user"
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
