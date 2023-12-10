import os

from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from flask import request, jsonify, make_response
from flask_restful import Resource, reqparse
from flasgger import Swagger, swag_from

from sqlalchemy import text, inspect
from sqlalchemy.sql import func
from sqlalchemy.orm import Session

app = Flask(__name__)
swagger = Swagger(app)
api = Api(app)

# WEBSITE_HOSTNAME exists only in production environment
if app.testing:
    print("Loading config.testing and running tests")
    # local
    app.config.from_object('configs.testing')
elif 'WEBSITE_HOSTNAME' not in os.environ:
    print("Loading config.development and environment variables from .env file.")
    # local
    app.config.from_object('configs.testing')
    # app.config.from_object('configs.development')
else:
    # production
    print("Loading config.production.")
    app.config.from_object('configs.production')

app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
db = SQLAlchemy(app)

# Create the Model
class Task(db.Model):
    """"Model which represents a Task.

    Can only be deleted upon completion
    """

    __table_name__ = app.config.get("TABLE_NAME")
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    # Let DB handle setting the correct timestamp
    created_at = db.Column(db.DateTime(), server_default=func.now())

    # __table_args__ = {'schema': app.config.get('SCHEMA_NAME')}
    

    def __repr__(self):
        return self.title

    def to_dict(self):
        """Return relevant fields as a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description
        }

# Initialize the database connection and create the DB and tables
with app.app_context():
    inspector = inspect(db.engine)
    db_name = app.config.get('DB_NAME')
    existing_dbs = inspector.get_table_names()
    print(existing_dbs)
    # existing_dbs = db.session.execute(text("SHOW DATABASES;"))
    if db_name not in existing_dbs:
        print(f"Creating database {db_name}")
        # db.session.execute(text(f"CREATE DATABASE {db_name}"))
    db.create_all()


# Task Resource
class TaskResource(Resource):
    """Endpoint for getting and creating tasks."""

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type = str, required = True, help = 'No task title provided')
        self.reqparse.add_argument('description', type = str, required=True, location = 'json')
        super(TaskResource, self).__init__()

    def get(self):
        """Get all Tasks in the database.

        ---
        tags:
          - tasks
        definitions:
          TaskList:
            type: array
            items:
              $ref: '#/definitions/Task' 
          Task:
            type: object
            properties:
              id:
                type: integer
              description:
                type: string
        responses:
          200:
            description: A list of all tasks in the database
            schema:
                $ref: '#/definitions/TaskList' 

        """
        return jsonify({"tasks": [task.to_dict() for task in db.session.query(Task).all()]})

    def post(self):
        """Create a new Task in the database.

        ---
        tags:
          - tasks
        parameters:
          - name: task_id
            in: path
            type: integer
            required: true
        responses:
          201:
            description: A new Task has been created
            schema:
                $ref: '#/definitions/Task' 
        400:
            description: Bad request, title and description must be filled
        """
        try:
            d = {}
            args = self.reqparse.parse_args()
            print(args)
            for k, v in args.items():
                if v != None:
                    d[k] = v

            task = Task(**d)
        except TypeError as e:
            return make_response(jsonify({"error": str(e)}), 400)
        else:
            db.session.add(task)
            db.session.commit()
            return jsonify({"task": task.to_dict()})


class TaskDetailResource(Resource):
    """Endpoint for getting, updating and deleting a single task."""

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type = str, location = 'json')
        self.reqparse.add_argument('description', type = str, location = 'json')
        super(TaskDetailResource, self).__init__()
    

    def get(self, task_id: int):
        """Get a single Task in the database.

        ---
        tags:
          - tasks
        parameters:
          - name: task_id
            in: path
            type: integer
            required: true
        responses:
          200:
            description: A single Task
            schema:
                $ref: '#/definitions/Task' 
          404:
            description: Task with specified ID was not found
        """
        task = db.session.get(Task, task_id)

        if task:
            return jsonify({"task": task.to_dict()})

        return make_response(jsonify({"error": "Task not found"}), 404)

    def put(self, task_id: int):
        """Update a single Task in the database.

        ---
        tags:
          - tasks
        parameters:
          - name: task_id
            in: path
            type: integer
            required: true
        responses:
          200:
            description: A single Task
            schema:
                $ref: '#/definitions/Task' 
          404:
            description: Task with specified ID was not found
        """
        task = db.session.get(Task, task_id)

        if task:
            try:
                args = self.reqparse.parse_args()
                for k, v in args.items():
                    if v != None:
                        setattr(task, k, v)
            except TypeError as e:
                print(e)
                return make_response(jsonify({"error": str(e)}), 400)
            else:
                db.session.commit
                return jsonify({"task": task.to_dict()})

        return make_response(jsonify({"error": "Task not found"}), 404)

    def delete(self, task_id: int):
        """Update an existing Task in the database.

        ---
        tags:
          - tasks
        parameters:
          - name: task_id
            in: path
            type: integer
            required: true
        responses:
          204:
            description: Task deleted
          404:
            description: Task with specified ID was not found
        """
        task = db.session.get(Task, task_id)

        if not task:
            return make_response(jsonify({"error": "Task not found"}), 404)

        db.session.delete(task)
        db.session.commit()

        return make_response(jsonify({"message": "Task deleted successfully"}))

VERSION = "v1.0"
BASE_URL = f"/flask_task/api/{VERSION}"

# Add resources to the API
api.add_resource(TaskResource, f"{BASE_URL}/tasks")
api.add_resource(TaskDetailResource, f"{BASE_URL}/tasks/<int:task_id>")

if __name__ == "__main__":
    app.run(debug=True)
