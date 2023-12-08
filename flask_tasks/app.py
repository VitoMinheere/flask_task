import os

from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from flask import request, jsonify, make_response
from flask_restful import Resource, reqparse

# from .endpoints.tasks import TaskResource, TaskDetailResource
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text

app = Flask(__name__)
api = Api(app)

# WEBSITE_HOSTNAME exists only in production environment
if 'WEBSITE_HOSTNAME' not in os.environ:
    # local development, where we'll use environment variables
    print("Loading config.development and environment variables from .env file.")
    app.config.from_object('azureproject.development')
else:
    # production
    print("Loading config.production.")
    app.config.from_object('azureproject.production')

app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# Initialize the database connection
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=text("uuid_generate_v4()"))
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.DateTime())

    def __repr__(self):
        return self.title

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description
        }


# DB for quick tests
tasks = [{"id": 1, "title": "First Task", "description": "Test"}]

# Task Resource
class TaskResource(Resource):
    """Endpoint for getting and creating tasks."""

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type = str, required = True, help = 'No task title provided')
        self.reqparse.add_argument('description', type = str, required=True, location = 'json')
        super(TaskResource, self).__init__()

    def get(self):
        """Return all tasks found in database."""
        return jsonify({"tasks": [task for task in tasks]})

    def post(self):
        try:
            d = {}
            args = self.reqparse.parse_args()
            print(args)
            for k, v in args.items():
                if v != None:
                    d[k] = v

            data = Task(**d)
            task = {"id": len(tasks) + 1, **data.to_dict()}
            tasks.append(task)
            return jsonify({"task": task})
        except TypeError as e:
            return make_response(jsonify({"error": str(e)}), 400)


class TaskDetailResource(Resource):
    """Endpoint for getting, updating and deleting a single task."""

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type = str, location = 'json')
        self.reqparse.add_argument('description', type = str, location = 'json')
        super(TaskDetailResource, self).__init__()
    

    def get(self, task_id: int):
        task = next((t for t in tasks if t["id"] == task_id), None)

        if task:
            return jsonify({"task": Task(**task).to_dict()})

        return make_response(jsonify({"error": "Task not found"}), 404)

    def put(self, task_id: int):
        task = next((t for t in tasks if t["id"] == task_id), None)
        if task:
            try:
                # data = Task(**request.json) 
                data = {}
                args = self.reqparse.parse_args()
                for k, v in args.items():
                    if v != None:
                        data[k] = v
            except TypeError as e:
                return make_response(jsonify({"error": e.errors()}), 400)
            else:
                task.update(data)
                return jsonify({"task": task})

        return make_response(jsonify({"error": "Task not found"}), 404)

    def delete(self, task_id: int):
        global tasks
        task = next((t for t in tasks if t["id"] == task_id), None)
        if not task:
            return make_response(jsonify({"error": "Task not found"}), 404)

        tasks = [t for t in tasks if t["id"] != task_id]
        return make_response(jsonify({"message": "Task deleted successfully"}))

VERSION = "v1.0"
BASE_URL = f"/flask_task/api/{VERSION}"
# Add resources to the API
api.add_resource(TaskResource, f"{BASE_URL}/tasks")
api.add_resource(TaskDetailResource, f"{BASE_URL}/tasks/<int:task_id>")

if __name__ == "__main__":
    app.run(debug=True)
