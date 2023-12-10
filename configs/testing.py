""""Configuration for running the unittest suite with an actual (local) database.

DB, Schema and table names differ from the other to prevent accidental deletion.
"""

TABLE_NAME = 'task_test'
SCHEMA_NAME = 'main'
DB_NAME = 'main'
USER_TOKEN = "user_token"
ADMIN_TOKEN = "admin_token"
DATABASE_URI = 'sqlite:////workspace/tests/test.sqlite'