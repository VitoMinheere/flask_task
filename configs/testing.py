""""Configuration for running the unittest suite with an actual (local) database.

DB, Schema and table names differ from the other to prevent accidental deletion.
"""

TABLE_NAME = 'task_test'
SCHEMA_NAME = 'test'
DB_NAME = 'test'
DATABASE_URI = 'sqlite:////workspace/tests/test.sqlite'