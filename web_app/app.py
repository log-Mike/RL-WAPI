from flask import Flask, redirect, url_for, render_template, request
from flask_mysqldb import MySQL

app=Flask(__name__)

'''app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask'

'''


@app.route('/')
def start():
    return render_template('index.html')
    

# for development run it on local in debug mode
# waitress could be a could option for later
if __name__=='__main__':
    app.run(debug=True)