""""Configuration for running the application in a development environment.

This can be in a decvontainer or cloud environment. env vars will default if they are not set
"""
import os

TABLE_NAME = 'tasks'
SCHEMA_NAME = 'flask_task'
DB_NAME = "tasks"
USER_TOKEN = "user_token"
ADMIN_TOKEN = "admin_token"

DATABASE_URI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
    dbuser=os.environ.get('DBUSER', "postgres"),
    dbpass=os.environ.get('DBPASS', "postgres"),
    dbhost=os.environ.get('DBHOST', "localhost:5432"),
    dbname=DB_NAME
)