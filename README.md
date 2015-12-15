# EBshare
CSC 322, Software Engineering, project.

Uses Django. Do pip install django if you don't have it installed already.
Some modules may need to be installed as well. In the project root folder, do pip install -r requirements.txt
There are scripts in the project root directory, mainly written for bash on a linux machine.
For a fresh start, run ./purge && ./load db
./dump will create json files inside fixture folders as well as a main db.json.
It is sugessted to avoid running this script unless the new data in valuable. ./dump was mainly for viewing the existing data.
./clear will delete the fixtures folders and any json files other than db.json.
to run the server in google chrome, ./run
./run only worked on a linux machine with google chrome installed.
Alternatively, one could run python manage.py runserver and in any browser window, navigate to localhost:8000
The admin panel is in localhost:8000

In the db.json file that is loaded by ./load db, there are registered users, and superusers. Use find to search for auth.user.
The users with is_authenticated set to true are super users. As of 12/14/15, the registered users were jean, musta, abhi, wei,
and the superuser was su. The passwords were the same as the usernames.
