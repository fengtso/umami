umami
=====

Reading List App

## SQLite Viewer
No need to install SQLite on Mac. However, it will be useful to have a SQLite viewer to see the table data
http://sqlitestudio.pl/
The database file path is `umami/flask-restful/db/umami.db`

## Install Python packages
1. `pip install -r requirements.txt`

## Setup local server
1. `python server.py`

## Push a new task
1. `python client.py --push --url=<url> --tag=<tag>`

## Complete a task
1. `python client.py --complete --url=<url>`

## Delete a task
1. `python client.py --delete --url=<url>`

## Get pushed tasks
1. `http://localhost:5000/getPushedTasks`

## Get required tasks
1. `http://localhost:5000/getRequiredTasks`

## Get pending tasks
1. `http://localhost:5000/getPendingTasks`
