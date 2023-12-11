import os
from functools import wraps

from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from flask import request, jsonify, make_response
from flask_restful import Resource, reqparse
from flasgger import Swagger, swag_from
from flask_httpauth import HTTPTokenAuth
from dotenv import load_dotenv

from sqlalchemy import text
from sqlalchemy.sql import func
from sqlalchemy.orm import Session

app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')
swagger = Swagger(app,
      template={
        "swagger": "2.0",
        "info": {
            "title": "Flask Task API",
            "version": "1.0",
        },
        "consumes": [
            "application/json",
        ],
        "produces": [
            "application/json",
        ],
        "headers": []
    }
)
api = Api(app)

# WEBSITE_HOSTNAME exists only in production environment
if app.testing:
    print("Loading config.testing and running tests")
    # local
    app.config.from_object('configs.testing')
elif 'WEBSITE_HOSTNAME' not in os.environ:
    print("Loading config.development and environment variables from .env file.")
    # local
    app.config.from_object('configs.development')
else:
    # production
    print("Loading config.production.")
    load_dotenv(".env")
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
    # Let database handle setting the correct timestamp
    created_at = db.Column(db.DateTime(), server_default=func.now())

    __table_args__ = {'schema': app.config.get('SCHEMA_NAME')}
    
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
    # db.init_app(app)
    db.create_all()

# Add basic authentication tokens
tokens = {
    app.config.get("USER_TOKEN"): "user_account",
    app.config.get("ADMIN_TOKEN"): "admin_account",
}

# Add roles matching the above account names
roles = {
    "user_account": "user",
    "admin_account": "admin"
}

@auth.verify_token
def verify_token(token: str) -> str:
    """Verify that a token send in the header exists.
    """
    if token in tokens:
        return tokens[token]

@auth.get_user_roles
def get_user_roles(username: str) -> str:
    """Get the role matching a username.
    Will return None if none matches
    """
    return roles.get(username)

# Task Resource
class TaskResource(Resource):
    """Endpoint for getting and creating tasks."""

    def __init__(self):
        """Parser for the arguments in the endpoints."""
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
              title:
                type: string
              description:
                type: string
        responses:
          200:
            description: A list of all tasks in the database
            schema:
                $ref: '#/definitions/TaskList' 
          '5XX':
            description: Unexpected error.

        """
        return jsonify({"tasks": [task.to_dict() for task in db.session.query(Task).all()]})

    @auth.login_required(role='user')
    def post(self):
        """Create a new Task in the database.
        Requires User level access

        ---
        tags:
          - tasks
        security:
          - Bearer
        parameters:
          - name: Authorization
            in: header
            type: string
            required: true
            description: Add "Bearer " in front of token
          - name: task
            in: body
            schema: 
                $ref: '#/definitions/Task' 
        responses:
          201:
            description: A new Task has been created
            schema:
                $ref: '#/definitions/Task' 
          400:
            description: Bad request, title and description must be filled
          401:
              description: Unauthorized
          403:
              description: Forbidden
          '5XX':
            description: Unexpected error.
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
        """Parser for the arguments in the endpoints."""
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
          '5XX':
            description: Unexpected error.
        """
        task = db.session.get(Task, task_id)

        if task:
            return jsonify({"task": task.to_dict()})

        return make_response(jsonify({"error": "Task not found"}), 404)

    @auth.login_required(role='user')
    def put(self, task_id: int):
        """Update a single Task in the database.
        Requires User level access

        ---
        tags:
          - tasks
        security:
          - Bearer
        parameters:
          - name: Authorization
            in: header
            type: string
            required: true
            description: Add "Bearer " in front of token
          - name: task_id
            in: path
            type: integer
            required: true
          - name: task
            in: body
            schema: 
                $ref: '#/definitions/Task' 
        responses:
          200:
            description: A single Task
            schema:
                $ref: '#/definitions/Task' 
          400:
              description: Bad request, title and description must be filled
          401:
              description: Unauthorized
          403:
              description: Forbidden
          404:
              description: Task with specified ID was not found
          '5XX':
            description: Unexpected error.
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

    @auth.login_required(role='admin')
    def delete(self, task_id: int):
        """Update an existing Task in the database.
        Requires Admin level access

        ---
        tags:
          - tasks
        security:
          - Bearer
        parameters:
          - name: Authorization
            in: header
            type: string
            required: true
            description: Add "Bearer " in front of token
          - name: task_id
            in: path
            type: integer
            required: true
        responses:
          204:
            description: Task deleted
          401:
            description: Unauthenticated. Use the Bearer token
          403:
            description: Unauthorized. Use a token with admin access
          404:
            description: Task with specified ID was not found
          '5XX':
            description: Unexpected error.
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
    app.run()
