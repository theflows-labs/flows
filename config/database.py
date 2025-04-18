"""
Database connection settings for theflows.
"""
import os

# Database connection settings
# DB_USER = os.getenv('DB_USER', 'postgress')
# DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgress')
# DB_HOST = os.getenv('DB_HOST', 'localhost')
# DB_PORT = os.getenv('DB_PORT', '5433')
# DB_NAME = os.getenv('DB_NAME', 'postgress')

DB_USER =  'postgress'
DB_PASSWORD = 'postgress'
DB_HOST =  'localhost'
DB_PORT =  '5433'
DB_NAME = 'postgress'

# SQLAlchemy connection string
SQLALCHEMY_CONN = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Database schema
DB_SCHEMA = os.getenv('DB_SCHEMA', 'theflows') 