from flask import request, jsonify, make_response
from flask_restful import Resource
from pydantic import ValidationError

from ..models import TaskCreateUpdateModel, TaskResponseModel

# DB for quick tests
tasks = [{"id": 1, "title": "First Task", "description": "Test"}]

# Task Resource
class TaskResource(Resource):
    def get(self):
        return jsonify({"tasks": [task for task in tasks]})

    def post(self):
        try:
            data = TaskCreateUpdateModel(**request.json)
            task = {"id": len(tasks) + 1, **data.model_dump()}
            tasks.append(task)
            return jsonify({"task": task})
        except ValidationError as e:
            return make_response(jsonify({"error": e.errors()}), 400)


class TaskDetailResource(Resource):
    def get(self, task_id):
        task = next((t for t in tasks if t["id"] == task_id), None)

        if task:
            return jsonify({"task": TaskResponseModel(**task).model_dump()})

        return make_response(jsonify({"error": "Task not found"}), 404)

    def put(self, task_id):
        task = next((t for t in tasks if t["id"] == task_id), None)
        if task:
            try:
                data = TaskCreateUpdateModel(**request.json)
            except ValidationError as e:
                return make_response(jsonify({"error": e.errors()}), 400)
            else:
                task.update(data.model_dump())
                return jsonify({"task": task})

        return make_response(jsonify({"error": "Task not found"}), 404)

    def delete(self, task_id):
        global tasks
        task = next((t for t in tasks if t["id"] == task_id), None)
        if not task:
            return make_response(jsonify({"error": "Task not found"}), 404)

        tasks = [t for t in tasks if t["id"] != task_id]
        return make_response(jsonify({"message": "Task deleted successfully"}))