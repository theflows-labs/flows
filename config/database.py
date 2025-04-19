"""
Database connection settings for theflows.
"""
import os
from typing import Optional

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
DB_SCHEMA = 'theflows'

# SQLAlchemy configuration
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'max_overflow': 20,
    'pool_timeout': 30,
} 