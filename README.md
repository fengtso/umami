umami
=====

Reading List App

## Install Python packages
1. `pip install -r requirements.txt`

## Setup local server
1. `python server.py`

## Push a new task
1. `python client.py --push --url=<url> --tag=<tag>`

## Complete a task
1. `python client.py --complete --url=<url>`

## Get pushed tasks
1. `http://localhost:5000/getPushedTasks`

## Get required tasks
1. `http://localhost:5000/getRequiredTasks`
