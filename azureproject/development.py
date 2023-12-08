import os

DATABASE_URI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
    dbuser=os.environ.get('DBUSER', "postgres"),
    dbpass=os.environ.get('DBPASS', "postgres"),
    dbhost=os.environ.get('DBHOST', "localhost:5432"),
    dbname=os.environ.get('DBNAME', "flask_task")
)