import unittest
import os

from flask import json
from app import app, db, BASE_URL

class TestTaskEndpoints(unittest.TestCase):

    def setUp(self):
        os.environ["TESTING"] = "1"
        app.config['TESTING'] = True
        self.app = app.test_client()

    def create_task(self) -> int:
        task_data = {'title': 'Test Task', 'description': 'This is a test task'}
        response = self.app.post(f'{BASE_URL}/tasks', json=task_data,  headers={"Authorization": "Bearer user_token"})
        data = json.loads(response.get_data(as_text=True))
        task_id = data["task"]["id"]
        return task_id

    def test_create_task(self):
        task_data = {'title': 'Test Task', 'description': 'This is a test task'}
        response = self.app.post(f'{BASE_URL}/tasks', json=task_data, headers={"Authorization": "Bearer user_token"})
        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertIn('task', data)
        self.assertEqual(data['task']['title'], task_data['title'])
        self.assertEqual(data['task']['description'], task_data['description'])

    def test_create_task_invalid_data(self):
        invalid_task_data = {'description': 'This is a test task without title'}
        response = self.app.post(f'{BASE_URL}/tasks', json=invalid_task_data, headers={"Authorization": "Bearer user_token"})
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 400)
        self.assertIn('title', data["message"])

    def test_get_tasks(self):
        response = self.app.get(f'{BASE_URL}/tasks', headers={"Authorization": "Bearer user_token"})
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn('tasks', data)
        self.assertIsInstance(data['tasks'], list)

    def test_get_task(self):
        task_id = 1  # Assuming there's at least one task in the list
        response = self.app.get(f'{BASE_URL}/tasks/{task_id}', headers={"Authorization": "Bearer user_token"})
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn('task', data)

    def test_get_task_not_found(self):
        invalid_task_id = 9999  # Assuming this task ID does not exist
        response = self.app.get(f'{BASE_URL}/tasks/{invalid_task_id}', headers={"Authorization": "Bearer user_token"})
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', data)

    def test_update_task(self):
        task_id = self.create_task()
        updated_data = {'title': 'Updated Task Title', 'description': 'Updated task description'}
        response = self.app.put(f'{BASE_URL}/tasks/{task_id}', json=updated_data, headers={"Authorization": "Bearer user_token"})
        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertIn('task', data)
        self.assertEqual(data['task']['id'], task_id)
        self.assertEqual(data['task']['title'], updated_data['title'])
        self.assertEqual(data['task']['description'], updated_data['description'])

    def test_update_task_not_found(self):
        invalid_task_id = 9999  # Assuming this task ID does not exist
        response = self.app.put(f'{BASE_URL}/tasks/{invalid_task_id}', json={}, headers={"Authorization": "Bearer user_token"})
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', data)

    def test_delete_task(self):
        task_id = self.create_task()
        response = self.app.delete(f'{BASE_URL}/tasks/{task_id}', headers={"Authorization": "Bearer admin_token"})
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Task deleted successfully')

    def test_delete_test_fails_if_not_admin(self):
        response = self.app.delete(f'{BASE_URL}/tasks/1', headers={"Authorization": "Bearer user_token"})
        self.assertEqual(403, response.status_code)

    def test_delete_task_not_found(self):
        invalid_task_id = 9999  # Assuming this task ID does not exist
        response = self.app.delete(f'{BASE_URL}/tasks/{invalid_task_id}', headers={"Authorization": "Bearer admin_token"})
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()
