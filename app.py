from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_mysqldb import MySQL
from ldap3 import Connection
from ldap3.utils.conv import escape_filter_chars

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
        MYSQL_PORT = {port_number}
        
        API_KEY = "single_api_key"
        SECRET_KEY = "secret_key"
        
        An API & a Secret key can be 
        generated with
        python gen_key.py secret
        python gen_key.py api
        ''')

app.config['NO_USER_MSG'] = 'User not assigned'

db = MySQL(app)


def get_table_and_columns(cur):
    try:
        cur.execute(f'''select name, coalesce(user, "{app.config["NO_USER_MSG"]}"),
                case
                    when timestampdiff(second, date_updated, now()) < 60 then
                        concat(timestampdiff(second, date_updated, now()), ' seconds ago')
                    when timestampdiff(minute, date_updated, now()) < 60 then
                        concat(timestampdiff(minute, date_updated, now()), ' minutes ago')
                    when timestampdiff(hour, date_updated, now()) < 24 then
                        concat(
                            timestampdiff(hour, date_updated, now()),
                            ' hours ',
                            timestampdiff(minute, date_updated, now()) % 60,
                            ' minutes ago'
                        )
                    else date_format(date_updated, '%m/%d/%y %h:%i %p')
                end
            from network
            order by 1''')

        return cur.fetchall(), ('Network', 'Assigned User', 'Last updated')

    except Exception as e:
        raise e


# set any free network to given user
# should this have some sort of distribution?
# assumes a user has to be in user table
# else says bad input
# to be assigned to a network
def lock(cur, user):
    # verifying existence
    # this should be from LDAP
    # & not SQL ?
    found = cur.execute('''select 0
                            from userInfo
                            where username = %s''', (user,))

    if found == 0:
        result = '4 - No matching user'
    elif found != 1:
        result = '5 - More than one matching user record found'
    else:
        found = cur.execute('''select name
                                from network
                                where user is NULL
                                limit 1''')

        # found no networks with a null user
        if found == 0:
            result = '6 - No free networks'
        else:
            picked = cur.fetchone()[0]
            found = cur.execute('''update network
                                    set user = %s
                                    where name = %s ''', (user, picked))

            if found != 1:
                result = '7 - problem updating db'
            else:
                result = f'{user} locked to {picked}'
                db.connection.commit()

    return result


# set given network's user to null
def unlock(cur, network):
    found = cur.execute('''update network
                            set user = NULL
                            where name = %s''', (network,))

    if found == 0:
        result = '8 - No matching network found'
    elif found != 1:
        result = '9 - More than one matching network found, update transaction rollbacked'
    else:
        result = f'{network} unlocked'
        db.connection.commit()

    return result


# return status of a given network
def checklock(cur, network):
    found = cur.execute('''select user
                            from network
                            where name = %s''', (network,))

    if found == 0:
        result = '10 - No matching row found'
    elif found != 1:
        result = '11 - More than one record found in db matching the network name'
    else:
        assigned_user = cur.fetchone()[0]

        result = 'unlocked' if assigned_user is None else f'locked by {assigned_user}'

    return f'{network} is {result}'


# result is currently just want happened. need to 
# change result(return value) to actual output for client
@app.route('/api/<string:action>', methods=['GET', 'PATCH'])
def handle_request(action):
    api_key = request.headers.get('API-KEY')

    if not api_key == app.config['API_KEY']:
        return 'bad api key'

    try:
        param = request.args.get('input')
        try:
            with db.connection.cursor() as cur:
                method = request.method
                err_msg = '12 - request and action not recognized'

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

        except Exception as e:
            return str(e)
    except Exception as e:
        return str(e)

    return result


@app.route('/')
def start():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # if already logged in:
        #    return redirect{dashboard}
        user = escape_filter_chars(request.form.get('username'))
        password = escape_filter_chars(request.form.get('pswrd'))

        # Bind with the user's DN and password to authenticate
        user_connection = Connection('giantest.local.com', user=f'uid={user},cn=users,cn=accounts,dc=local,dc=com',
                                     password=password)

        if user_connection.bind():
            print(f"User {user} authenticated successfully.")
            # search for users member info

            search_base = 'cn=users,cn=accounts,dc=local,dc=com'
            search_filter = f'(&(objectclass=person)(uid={user}))'
            user_connection.search(search_base, search_filter, attributes=['memberOf'])

            # Check if the user is a member of the 'admins' group
            # should set up login so that user has (base line) 1 field: is_admin
            is_admin = 'cn=admins,cn=groups,cn=accounts,dc=local,dc=com' in user_connection.entries[0].memberOf
            return redirect(url_for('select_page_admin' if
                                    is_admin else 'select_page_user'))
        else:
            # flash user saying bad auth
            return render_template('login.html')
    else:
        return render_template('login.html')


@app.route('/allocate', methods=['GET', 'PATCH'])
def select_page_admin():
    if request.method == 'PATCH':
        user = request.form.get('user')
        network = request.form.get('network')

        try:
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
        except Exception as e:
            return jsonify({
                'error': 'An error occurred: ' + str(e)
            })
    else:
        try:
            with db.connection.cursor() as cur:

                # for dropdowns
                cur.execute('''select username
                                from userInfo
                                order by 1''')
                avail_users = cur.fetchall()

                cur.execute('''select name
                                from network
                                order by 1''')
                avail_networks = cur.fetchall()

                table, cols = get_table_and_columns(cur)

                return render_template('select.html',
                                       column1_values=avail_users,
                                       column2_values=avail_networks,
                                       data=table,
                                       columns=cols)

        except Exception as e:
            return render_template('error.html',
                                   msg='An error occurred: ' + str(e))


@app.route('/view')
def select_page_user():
    try:
        with db.connection.cursor() as cur:
            table, cols = get_table_and_columns(cur)

            return render_template('view.html',
                                   data=table,
                                   columns=cols)

    except Exception as e:
        return render_template('error.html',
                               msg='An error occurred: ' + str(e))


# for development run it on local in debug mode
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
