""""Configuration for running the application in a production environment.

This must be a cloud environment. Defaults are None to the app will fail if this is not set.
"""
import os

TABLE_NAME = 'task'
SCHEMA_NAME = 'flask_task'
DB_NAME = os.environ.get('DBNAME', None)

DATABASE_URI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
    dbuser=os.environ.get('DBUSER', None),
    dbpass=os.environ.get('DBPASS', None),
    dbhost=os.environ.get('DBHOST', None),
    dbname=DB_NAME
)