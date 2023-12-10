""""Configuration for running the application in a production environment.

This must be a cloud environment. Defaults are None to the app will fail if this is not set.
"""
import os

TABLE_NAME = 'task'
SCHEMA_NAME = 'flask_task'
DB_NAME = 'tasks'
USER_TOKEN = os.environ.get('USER_TOKEN')
ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN')

conn_str = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
conn_str_params = {pair.split('=')[0]: pair.split('=')[1] for pair in conn_str.split(' ')}

DATABASE_URI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
    dbuser=conn_str_params['user'],
    dbpass=conn_str_params['password'],
    dbhost=conn_str_params['host'],
    dbname=conn_str_params['dbname']
)
# DATABASE_URI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
#     dbuser=os.environ.get('DBUSER'),
#     dbpass=os.environ.get('DBPASS'),
#     dbhost=os.environ.get('DBHOST'),
#     dbname=DB_NAME
# )