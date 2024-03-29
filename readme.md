**Resource Lock Web API** is a program that performs automatic distribution of resources and is integrated into Lockheed Martin’s team’s CI/CD pipeline. In addition, a web application that is used to view resource availability, and manually free and assign resources.

# To run
- Set  up an [LDAP](#ldap-authentication) implementation
    
 - Set up the configuration file

     `config.py`
   
       
          
          MYSQL_HOST = "sql_db_host"
          MYSQL_USER = "sql_db_user"
          MYSQL_PASSWORD = "sql_db_pwd"
          MYSQL_DB = "sql_db_name"
          # Integer
          MYSQL_PORT = {port_number}
        
          # gen_keys.py can generate these for you
          API_KEY = "single_api_key"
          SECRET_KEY = "secret_key"   

          LDAP_HOST = "example.local.com"
          LDAP_USERS_PATH = "cn=users,cn=accounts,dc=local,dc=com"
          LDAP_ADMINS_PATH = 'cn=admins,cn=groups,cn=accounts,dc=local,dc=com'

          # might need admin depending on ldap config
          LDAP_USER = "ldap_sign_in"
          LDAP_PASSWORD = "ldap_password"


- Run the app

	`flask run`

You should now be able to access the web app at http://localhost:5000 , defaulted to 5000

# To access the API through client shell

- Set the API key

	`$env:API_KEY = "api_key"`

    or

	`export API_KEY="api_key"`

- Execute the script
	
	`./client.sh lock user_id`
	`./client.sh unlocklock network_id`
	`./client.sh checklock network_id`

# LDAP Authentication
- Authenticates web app user via LDAP

- FreeIPA is an open source implementation of LDAP

- Launch an OS capable of hosting FreeIPA (such as [the lastest Fedora release](https://fedoraproject.org/workstation/download))

- Resolve download issues, for a simple with default installtion client:

`sudo dnf install freeipa-client`

`sudo ipa-client-install
`

- Press enter for all except the question ending in "config from these settings?", type yes
