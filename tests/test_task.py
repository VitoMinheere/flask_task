import unittest
from flask import json
from flask_tasks.app import app

class TestTaskEndpoints(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_create_task(self):
        task_data = {'title': 'Test Task', 'description': 'This is a test task'}
        response = self.app.post('/tasks', json=task_data)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn('task', data)
        self.assertEqual(data['task']['title'], task_data['title'])
        self.assertEqual(data['task']['description'], task_data['description'])

    def test_create_task_invalid_data(self):
        invalid_task_data = {'description': 'This is a test task without title'}
        response = self.app.post('/tasks', json=invalid_task_data)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)

    def test_get_tasks(self):
        response = self.app.get('/tasks')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn('tasks', data)
        self.assertIsInstance(data['tasks'], list)

    def test_get_task(self):
        task_id = 1  # Assuming there's at least one task in the list
        response = self.app.get(f'/tasks/{task_id}')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn('task', data)
        self.assertEqual(data['task']['id'], task_id)

    def test_get_task_not_found(self):
        invalid_task_id = 9999  # Assuming this task ID does not exist
        response = self.app.get(f'/tasks/{invalid_task_id}')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', data)

    def test_update_task(self):
        task_id = 1  # Assuming there's at least one task in the list
        updated_data = {'title': 'Updated Task Title', 'description': 'Updated task description'}
        response = self.app.put(f'/tasks/{task_id}', json=updated_data)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn('task', data)
        self.assertEqual(data['task']['id'], task_id)
        self.assertEqual(data['task']['title'], updated_data['title'])
        self.assertEqual(data['task']['description'], updated_data['description'])

    def test_update_task_not_found(self):
        invalid_task_id = 9999  # Assuming this task ID does not exist
        response = self.app.put(f'/tasks/{invalid_task_id}', json={})
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', data)

    def test_update_task_invalid_data(self):
        task_id = 1  # Assuming there's at least one task in the list
        invalid_data = {'description': 'Updated task description without title'}
        response = self.app.put(f'/tasks/{task_id}', json=invalid_data)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)

    def test_delete_task(self):
        task_id = 1  # Assuming there's at least one task in the list
        response = self.app.delete(f'/tasks/{task_id}')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Task deleted successfully')

    def test_delete_task_not_found(self):
        invalid_task_id = 9999  # Assuming this task ID does not exist
        response = self.app.delete(f'/tasks/{invalid_task_id}')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()
