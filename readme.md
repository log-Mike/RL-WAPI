


# Resource Lock Web API
Made during/for Rowan University Software Engineering Fall 2023 class. Developed using the agile framework: Scrum.

**Resource Lock Web API** is a program that will perform automatic distribution of resources and can be integrated into Lockheed Martin’s team’s CI/CD pipeline. In addition, a web application that will be used to view resource availability, and manually free and assign resources.

# Team makeup:


Russell Bamberger - Product Owner 

Phoenix Poitras - Scrum Master

Michael Loughrin - Developer
**<br/>**


Victoria Bostick - Developer

Alexander Essig - Developer

Shauna Hurley - Developer

# To run the current version
- Clone the git repo
- Navigate into the directory

	`cd CG-RLWAPI`
    
- Make a virtual environment using `venv` like such:

	`python -m venv virt`

- Activate the virtual environment using activate located in `virt\Scripts` or `virt/bin` like such:

	`virt\Scripts\activate`

	`virt\Scripts\Activate.ps1`
    
    or

	`source virt/bin/activate`

- Install the required packages into the virtual environment:

	`pip install -r requirements.txt`
    
- Set up the configuration file

   `config.py`
   
        should be a python file: config.py with variables:
        MYSQL_HOST = "sql_db_host"
        MYSQL_USER = "sql_db_user"
        MYSQL_PASSWORD = "sql_db_pwd"
        MYSQL_DB = "sql_db_name"
        MYSQL_PORT = {port_number}
        
        # These can be generated using gen_key.py
        API_KEY = "single_api_key"
        SECRET_KEY = "secret_key"   

- Run the app

	`flask run`

You should now be able to access the web app at http://localhost:5000 , defaulted to 5000

# To access the API through client shell

- Set the API key

	`$env:API_KEY = "api_key"`

    or

	`export API_KEY="api_key"`

- Execute the script
	
	`./client.sh lock network`

# LDAP Server
- Current version conects to a LDAP server that is hosted on a local FreeIPA.

- To test locally, launch an OS capable of hosting FreeIPA (such as [the lastest Fedora release](https://fedoraproject.org/workstation/download))

- Current version is hard set to a host name "giantest.local.com" mapped to the local IP (mapping is located in /etc/hosts)
  
- Resolve download issues, set up the server or client using:

`sudo dnf install free-ipa client`

`sudo ipa-client install`

- For default installation, press enter for all except the question ending in "config from these settings?", type yes

# Exit codes for client.sh

    0 -  Successful

    1 - Problem with API Key

    2 - Bad parameters

    3 - Not an action (checklock/lock/unlock)

    4 - Couldn't find given input (network/user)

    5 - Multiple records found matching given input (network/user)

    6 - No free networks available

    7 - Problem unlocking, a free network was found but when went to lock, was not free

