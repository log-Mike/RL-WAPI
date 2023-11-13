

# Resource Lock Web API
Made during/for Rowan University Software Engineering Fall 2023 class. Developed using the agile framework: Scrum.

**Resource Lock Web API** is a program that will perform automatic distribution of resources and can be integrated into Lockheed Martin’s team’s CI/CD pipeline. In addition, a web application that will be used to view resource availability, and manually free and assign resources.

# Team makeup:


Russell Bamberger - Product Owner 

Phoenix Poitras - Scrum Master

Michael Loughrin - Developer
**<br/>**
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
        MYSQL_PORT = "sql_db_port"
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
