# Resource Lock Web API
Made during/for Rowan University Software Engineering Fall 2023 class. Developed using the agile framework: Scrum.

**Resource Lock Web API** is a program that will perform automatic distribution of resources and can be integrated into Lockheed Martin’s team’s CI/CD pipeline. In addition, a web application that will be used to view resource availability, and manually free and assign resources.

# Team makeup:
Michael Loughrin - Developer

Russell Bamberger - Product Owner 

Gina Poitras - Scrum Master

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

- Run the app

	`flask run`

You should now be able to access the web app at http://localhost:5000, typically http://127.0.0.1:5000
