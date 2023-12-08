from flask import Flask
from flask_restful import Api

from .endpoints.tasks import TaskResource, TaskDetailResource

app = Flask(__name__)
api = Api(app)


# Add resources to the API
api.add_resource(TaskResource, "/tasks")
api.add_resource(TaskDetailResource, "/tasks/<int:task_id>")

if __name__ == "__main__":
    app.run(debug=True)
