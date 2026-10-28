"""Compatibility entry point. The application uses connection.py and repositories."""
from database.connection import Database, connect_db
def initialize_database():
    Database().initialize()
if __name__ == '__main__':
    initialize_database()
