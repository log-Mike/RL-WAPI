# need (some of) these later
# from flask import Flask, redirect, url_for, render_template, request

from flask import Flask, render_template
from flask_mysqldb import MySQL

app=Flask(__name__)

app.config['MYSQL_HOST'] = 'elvis.rowan.edu'
app.config['MYSQL_USER'] = 'essiga27'
app.config['MYSQL_PASSWORD'] = '1Happygnome!'
app.config['MYSQL_DB'] = 'essiga27'

db = MySQL(app)

@app.route('/123abc')
def tryDB():
    try:
        cursor = db.connection.cursor()

        cursor.execute("select * from network")

        # 2d array
        data = cursor.fetchall()

        cursor.close()

        # returned string is put into an empty <body>
        # return in html table instead of newlines
        # so it's pretty :-)
        result = "<table>"
        for row in data:
            result += "<tr>"
            for value in row:
                result += "<td>" + str(value) + "</td>"
            result += "</tr>"
        result += "</table>"
        return result

    except Exception as e:
        error_message = "An error occurred: " + str(e)
        return error_message


@app.route('/')
def start():
    return render_template('index.html')
    

# for development run it on local in debug mode
# waitress could be a could option for later
# apparently waitress has a command line interface too,
# not sure if that can be used for our CLI as well
if __name__=='__main__':
    # almost certain we will need this later
    with app.app_context():
        app.run(debug=True)
