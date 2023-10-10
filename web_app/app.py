import flask 
from flask import render_template
from flask_mysqldb import MySQL

app=Flask(__name__)

app.config['MYSQL_HOST'] = 'elvis.rowan.edu'
app.config['MYSQL_USER'] = 'essiga27'
app.config['MYSQL_PASSWORD'] = '1Happygnome!'
app.config['MYSQL_DB'] = 'essiga27'

db = MySQL(app)

@app.route('/avail')
def print_resources():
    try:
        cursor = db.connection.cursor()
        
        # sample query
        cursor.execute("select * from network")
        # get array of tuples
        table = cursor.fetchall()
        
        cursor.close()
        
        # render the new template (html file)
        # pass in the table as data to q_results
        # make the table look pretty in q_results 
        # file with js, css
        return render_template('q_results.html', data=table)
    except Exception as e:
        return render_template('q_error.html', 
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
