from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_mysqldb import MySQL
from ldap3 import Connection
from ldap3.core.exceptions import LDAPBindError, LDAPPasswordIsMandatoryError, LDAPSocketOpenError
from ldap3.utils.conv import escape_filter_chars

from user import User

app = Flask(__name__)

try:
    app.config.from_pyfile('config.py')
except FileNotFoundError as e:
    raise SystemExit('''No config file found
        should be a python file: /config.py with variables:
        
        MYSQL_HOST = "sql_db_host"
        MYSQL_USER = "sql_db_user"
        MYSQL_PASSWORD = "sql_db_pwd"
        MYSQL_DB = "sql_db_name"

        # integer
        MYSQL_PORT = {port_number}
        
        API_KEY = "single_api_key"
        SECRET_KEY = "secret_key"
        

        LDAP_HOST = "example.local.com"
        LDAP_USERS_PATH = "cn=users,cn=accounts,dc=local,dc=com"
        LDAP_ADMINS_PATH = 'cn=admins,cn=groups,cn=accounts,dc=local,dc=com'

        # This might need to be admin depending on the setup
        LDAP_USER = "ldap_sign_in"
        LDAP_PASSWORD = "ldap_password"


        An API & a Secret key can be 
        generated with
        python gen_key.py secret
        python gen_key.py api
        ''')

app.config['NO_USER_MSG'] = 'User not assigned'
app.config['NO_RECORDS_MSG'] = '5 - No matching records found'
app.config['MULTI_RECORD_MSG'] = '6 - Multiple records found'

db = MySQL(app)

login_manager = LoginManager(app)
login_manager.session_protection = 'strong'


# set any free network to given user
# should this have some sort of distribution?
# assumes a user has to be in user table
# else says bad input
# to be assigned to a network
def lock(cur, user):
    # verifying existence
    found = cur.execute('''select 0
                            from userInfo
                            where username = %s
                            for update''', (user,))

    # continue even if identical multiple users are found
    if found == 0:
        result = app.config['NO_RECORDS_MSG']
    else:
        found = cur.execute('''select name
                                from network
                                where user is NULL
                                limit 1''')

        # found no networks with a null user
        if found == 0:
            result = '7 - No free networks'
        else:
            picked = cur.fetchone()[0]
            found = cur.execute('''update network
                                    set user = %s
                                    where name = %s ''', (user, picked))
            if found != 1:
                result = '8 - problem updating db, found a free network but when went to lock, was not free'
            else:
                result = f'0 - {picked}'
                db.connection.commit()

    return result


# set given network's user to null
def unlock(cur, network):
    found = cur.execute('''select 0
                            from network
                            where name = %s
                            for update''', (network,))
    if found == 0:
        result = app.config['NO_RECORDS_MSG']
    elif found != 1:
        result = app.config['MULTI_RECORD_MSG']
    else:

        found = cur.execute('''update network
                                set user = NULL
                                where name = %s''', (network,))

        if found == 0:
            result = '9 - network already unlocked'
        else:
            result = '0 - unlocked'
            db.connection.commit()

    return result


# return status of a given network
def checklock(cur, network):
    found = cur.execute('''select user
                            from network
                            where name = %s''', (network,))

    if found == 0:
        result = app.config['NO_RECORDS_MSG']
    elif found != 1:
        result = app.config['MULTI_RECORD_MSG']
    else:
        assigned_user = cur.fetchone()[0]

        result = '0 - ' + ('unlocked' if assigned_user is None else assigned_user)

    return result


# result is currently just want happened. need to
# change result(return value) to actual output for client
@app.route('/api/<string:action>', methods=['GET', 'PATCH'])
def handle_request(action):
    api_key = request.headers.get('API-KEY')

    if not api_key == app.config['API_KEY']:
        return '1 - Wrong API key'

    param = request.args.get('input')

    with db.connection.cursor() as cur:
        method = request.method
        err_msg = '4 - action/method not recognized'

        if method == 'PATCH':
            if action == 'lock':
                result = lock(cur, param)
            elif action == 'unlock':
                result = unlock(cur, param)
            else:
                result = err_msg
        elif method == 'GET' and action == 'checklock':
            result = checklock(cur, param)
        else:
            result = err_msg
    return result


@app.patch('/handle-update')
@login_required
def handle_update():
    if current_user.is_admin and request.method == 'PATCH':
        user = request.form.get('user')
        network = request.form.get('network')

        with db.connection.cursor() as cur:
            if user == 'DEL_USER':
                set_to = None
                update_to = app.config['NO_USER_MSG']
            else:
                set_to = user
                update_to = user

            num_updated = cur.execute('''update network
                                            set user=%s
                                            where name=%s''', (set_to, network))

            if num_updated == 1:
                db.connection.commit()

            return jsonify({
                'num_updated': num_updated,
                'network': network,
                'user': update_to
            })


@app.get('/home')
@login_required
def build_home():
    with db.connection.cursor() as cur:
        # for dropdowns
        cur.callproc('get_network_data', [app.config['NO_USER_MSG']])

        table = cur.fetchall()
        cols = [column[0] for column in cur.description]

        avail_users, avail_networks = None, None
        # only get columns for an admin
        if current_user.is_admin:
            cur.execute('''select username
                                from userInfo
                                order by 1''')
            avail_users = cur.fetchall()

            cur.execute('''select name
                                from network
                                order by 1''')
            avail_networks = cur.fetchall()

        return render_template('home.html',
                               column1_values=avail_users,
                               column2_values=avail_networks,
                               data=table,
                               columns=cols,
                               is_admin=current_user.is_admin)


# takes either 'uid' & a user_id(loughr95)
# or 'uidNumber' & a uidNumber (0888205)
# returns User object for login functionality
def get_user_info(search_on, search_input):
    if search_on == "uid":
        search_request = "uidNumber"
        on_key = False
    elif search_on == "uidNumber":
        search_request = "uid"
        on_key = True
    else:
        return None

    with Connection(app.config['LDAP_HOST'],
                    user=f'uid={app.config["LDAP_USER"]},{app.config["LDAP_USERS_PATH"]}',
                    password=app.config["LDAP_PASSWORD"]) as admin_connect:
        admin_connect.bind()

        search_filter = f'(&(objectclass=person)({search_on}={search_input}))'
        admin_connect.search(app.config['LDAP_USERS_PATH'], search_filter, attributes=['memberOf', search_request])

        is_admin = app.config['LDAP_ADMINS_PATH'] in admin_connect.entries[0]['memberOf']

        if on_key:
            unum = search_input
            uid = admin_connect.entries[0]['uid']
        else:
            unum = admin_connect.entries[0]['uidNumber']
            uid = search_input

    return User(str(unum), str(uid), is_admin)


@app.get('/')
def start():
    if current_user.is_authenticated:
        return redirect(url_for('build_home'))
    return render_template('login.html')


@app.post('/login')
def login():
    if not current_user.is_authenticated:
        user = escape_filter_chars(request.form.get('username'))
        password = escape_filter_chars(request.form.get('password'))

        try:
            with Connection(app.config['LDAP_HOST'],
                            user=f'uid={user},{app.config["LDAP_USERS_PATH"]}',
                            password=password) as connection:

                login_user(get_user_info("uid", user))
                return jsonify({'success': True})

        except (LDAPBindError, LDAPPasswordIsMandatoryError):
            message = 'Invalid username or password'
            return jsonify({'success': False, 'message': message})

        except LDAPSocketOpenError as err:
            message = 'fFatal response from server: {str(err)}'
            return jsonify({'success': False, 'message': message})
    else:
        return jsonify({'success': False, 'message': 'User is already authenticated'})


@app.get('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('start'))


@login_manager.user_loader
def load_user(user_id):
    return get_user_info("uidNumber", user_id)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('start'))


# for development run it on local in debug mode
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
