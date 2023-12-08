from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api
from pydantic import ValidationError

from flask_tasks.models import TaskCreateUpdateModel, TaskResponseModel

app = Flask(__name__)
api = Api(app)

# DB for quick tests
tasks = [{"id": 1, "title": "First Task", "description": "Test"}]
task_id_counter = 1

# Task Resource
class TaskResource(Resource):
    def get(self):
        return jsonify({'tasks': [task for task in tasks]})

    def post(self):
        try:
            data = TaskCreateUpdateModel(**request.json)
            task = {'id': len(tasks)+1, **data.model_dump()}
            tasks.append(task)
            return jsonify({'task': task})
        except ValidationError as e:
            return make_response(jsonify({'error': e.errors()}), 400)

class TaskDetailResource(Resource):
    def get(self, task_id):
        task = next((t for t in tasks if t['id'] == task_id), None)

        if task:
            return jsonify({'task': TaskResponseModel(**task).model_dump()})

        return make_response(jsonify({'error': 'Task not found'}), 404)

    def put(self, task_id):
        task = next((t for t in tasks if t['id'] == task_id), None)
        if task:
            try:
                data = TaskCreateUpdateModel(**request.json)
            except ValidationError as e:
                return make_response(jsonify({'error': e.errors()}), 400)
            else:
                task.update(data.model_dump())
                return jsonify({'task': task})

        return make_response(jsonify({'error': 'Task not found'}), 404)

# Add resources to the API
api.add_resource(TaskResource, '/tasks')
api.add_resource(TaskDetailResource, '/tasks/<int:task_id>')

if __name__ == '__main__':
    app.run(debug=True)
