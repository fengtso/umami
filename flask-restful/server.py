from flask import Flask
from flask import request
from flask.ext import restful
import sqlite3
import json
import datetime
import time

app = Flask(__name__)
api = restful.Api(app)


def connect_db():
    db_path = './db/umami.db'
    try:
        db_conn = sqlite3.connect(db_path)
        return db_conn
    except Exception, e:
        print e

    return None
 

def init_db():
    db_path = './db/umami.db'     
    sql_stmt = "CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, url TEXT, tag TEXT, phase TEXT, added_time TEXT, phase_one_time TEXT, completed_time TEXT)"

    db_conn = sqlite3.connect(db_path)
    if db_conn:
        try:
            db_cur = db_conn.cursor()
            db_cur.execute(sql_stmt)
            db_conn.commit()
            db_conn.close()
        except Exception, e:
            print e


class PushTaskAPI(restful.Resource):
    def push_task(self, task_info):
        db_conn = connect_db()
        db_cur = db_conn.cursor()

        # Check duplicate 
        sql_stmt = 'SELECT COUNT(*) FROM tasks WHERE url IS \"{url}\"'.format(
                    url=task_info['url']
                )
        try:
            db_cur.execute(sql_stmt)
            result = db_cur.fetchone()
            if result[0] != 0:
                db_conn.close()
                return False
        except Exception, e:
            print e

        # Insert
        now = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        sql_stmt = 'INSERT INTO tasks (url, tag, phase, added_time) VALUES (\"{url}\", \"{tag}\", \"c0\", \"{time}\")'.format(
                    url=task_info['url'],
                    tag=task_info['tag'],
                    time=now
                )
        try:
            db_cur.execute(sql_stmt)
            db_conn.commit()
            db_conn.close()
            return True
        except Exception, e:
            print e

    def post(self):
        task_data = request.get_json(force=True)
        success = self.push_task(task_data)
        return {'results': 'pushed'} if success else {'results': 'failed'}
    
    def options(self):
        pass


class GetPushedTasksAPI(restful.Resource):
    def get(self):
        pushed_tasks = []
        db_conn = connect_db()
        db_cur = db_conn.cursor()

        # c0
        sql_stmt = 'SELECT url, tag, added_time FROM tasks WHERE phase is \"c0\"'

        try:
            db_cur.execute(sql_stmt)
            results = []
            for t in db_cur.fetchall():
                pushed_tasks.append({
                    'url': t[0],
                    'tag': t[1],
                    'added_time': t[2]
                })
            return {'results': pushed_tasks}
        except Exception, e:
            print e


class GetRequiredTaskAPI(restful.Resource):
    def get(self):
        required_tasks = dict()

        db_conn = connect_db()
        db_cur = db_conn.cursor()
        now = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        date_format = '%Y-%m-%d %H:%M:%S'

        # Check each delta criteria
        phase_delta = [('c2', 1), ('c3', 4), ('c4', 9)]
        results = dict()
        for c, d in phase_delta:
            results[c] = []
            sql_stmt = 'SELECT url, tag, phase_one_time FROM tasks WHERE phase is \"c1\"'
            try:
                db_cur.execute(sql_stmt)
                for t in db_cur.fetchall():
                    delta = datetime.datetime.strptime(now, date_format) - datetime.datetime.strptime(t[2], date_format)
                    if delta.days == d:
                        results[c].append({
                            'url': t[0],
                            'tag': t[1]
                        })
            except Exception, e:
                print e

            for k, v in results.items():
                required_tasks[k] = v

        db_conn.close()
        return {'results': required_tasks}
        

class CompleteTaskAPI(restful.Resource):
    def get_next_phase(self, curr_phase):
        next_phase = 'c'
        next_phase += str(int(curr_phase[1:]) + 1)
        return next_phase

    def complete_task(self, task_data):
        db_conn = connect_db()
        db_cur = db_conn.cursor()
        now = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

        # Get current phase
        sql_stmt = 'SELECT phase FROM tasks WHERE url IS \"{url}\"'.format(
                url=task_data['url']
            )

        try:
            db_cur.execute(sql_stmt)
            result = db_cur.fetchone()

            # url doesn't exist
            if result == None:
                db_conn.close()
                return False
        except Exception, e:
            print e

        next_phase = self.get_next_phase(result[0])

        sql_stmt = ''
        if next_phase == 'c1':
            sql_stmt = 'UPDATE tasks SET phase=\"{phase}\", phase_one_time=\"{curr_time}\" WHERE url=\"{url}\"'.format(
                    phase=next_phase, 
                    curr_time=now,
                    url=task_data['url']
            )
        elif next_phase == 'c5':
            sql_stmt = 'UPDATE tasks SET phase=\"{phase}\", completed_time=\"{curr_time}\" WHERE url=\"{url}\"'.format(
                    phase=next_phase, 
                    curr_time=now,
                    url=task_data['url']
            )
        else:
            sql_stmt = 'UPDATE tasks SET phase=\"{phase}\" WHERE url=\"{url}\"'.format(
                    phase=next_phase, 
                    url=task_data['url']
            )

        try:
            db_cur.execute(sql_stmt)
            db_conn.commit()
            db_conn.close()
            return True
        except Exception, e:
            print e
            return False

    def post(self):
        task_data = request.get_json(force=True)
        success = self.complete_task(task_data)
        return {'results': 'completed'} if success else {'results': 'failed'}


class DeleteTaskAPI(restful.Resource):
    def post(self):
        task_data = request.get_json(force=True)
        success = self.delete_task(task_data)
        return {'results': 'deleted'} if success else {'results': 'failed'}

    def delete_task(self, task_data):
        db_conn = connect_db()
        db_cur = db_conn.cursor()

        # Check duplicate 
        sql_stmt = 'SELECT COUNT(*) FROM tasks WHERE url IS \"{url}\"'.format(
                    url=task_data['url']
                )
        try:
            db_cur.execute(sql_stmt)
            result = db_cur.fetchone()
            if result[0] == 0:
                db_conn.close()
                return False
        except Exception, e:
            print e

        # Delete url
        sql_stmt = 'DELETE FROM tasks WHERE url IS \"{url}\"'.format(
                url=task_data['url']
            )
        try:
            db_cur.execute(sql_stmt)
            db_conn.commit()
            db_conn.close()
            return True
        except Exception, e:
            print e
        return False


api.add_resource(PushTaskAPI, '/pushTask')
api.add_resource(GetPushedTasksAPI, '/getPushedTasks')
api.add_resource(GetRequiredTaskAPI, '/getRequiredTasks')
api.add_resource(CompleteTaskAPI, '/completeTask')
api.add_resource(DeleteTaskAPI, '/deleteTask')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
