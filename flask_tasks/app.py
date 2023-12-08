from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api
from pydantic import ValidationError

from flask_tasks.models import TaskCreateUpdateModel, TaskResponseModel

app = Flask(__name__)
api = Api(app)

# DB for quick tests
tasks = [{"title": "First Task", "description": "Test"}]
task_id_counter = 1

# Task Resource
class TaskResource(Resource):
    def get(self):
        return jsonify({'tasks': [task for task in tasks]})

# Add resources to the API
api.add_resource(TaskResource, '/tasks')

if __name__ == '__main__':
    app.run(debug=True)
