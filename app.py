from flask import Flask
from flask_restful import reqparse, abort, Api, Resource, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
api = Api(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



class TodoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200))
    note = db.Column(db.String(500))



task_post_args = reqparse.RequestParser()
task_post_args.add_argument('task', type=str, help='Task is required', required=True)
task_post_args.add_argument('note', type=str, help='Note is required', required=True)


task_put_args = reqparse.RequestParser()
task_put_args.add_argument('task', type=str)
task_put_args.add_argument('note', type=str)
 
# args = parser.parse_args()

resource_fields = {
    'id':   fields.Integer,
    'task':   fields.String,
    'note':   fields.String,
}

class TodoList(Resource):
    def get(self):
        tasks = TodoModel.query.all()
        todos = {}
        for task in tasks:
            todos[task.id] = {"task":task.task, "note": task.note}
        return todos

class Todo(Resource):

    @marshal_with(resource_fields)
    def get(self, todo_id):
        task = TodoModel.query.filter_by(id=todo_id).first()
        if not task:
            abort(404, message="Could not find task with that id....")
        return task

    @marshal_with(resource_fields)
    def post(self, todo_id):
        args = task_post_args.parse_args()
        task = TodoModel.query.filter_by(id=todo_id).first()
        if task:
            abort(409, message="Task id taken....")
        todo = TodoModel(id = todo_id, task=args['task'], note=args['note'])
        db.session.add(todo)
        db.session.commit()
        return todo, 201

    @marshal_with(resource_fields)
    def put(self, todo_id):
        args = task_put_args.parse_args()
        task = TodoModel.query.filter_by(id=todo_id).first()
        if not task:
            abort(409, mesage="Task does not exist....")
        if args['task']:
            task.task = args['task']
        if args['note']:
            task.note = args['note']
        db.session.commit()
        return task

    def delete(self, todo_id):
        task = TodoModel.query.filter_by(id=todo_id).first()
        db.session.delete(task)
        db.session.commit()
        return "Task deleted", 204
       


api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<todo_id>')


if __name__ == '__main__':
    app.run(debug=True)