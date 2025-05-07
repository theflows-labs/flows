"""
Database connection settings for theflows.
"""
import os
from typing import Optional

# Database connection settings
DB_USER = os.getenv('POSTGRES_USER', 'flows')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'flows123')
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost') # 'postgres' for docker
DB_PORT = os.getenv('POSTGRES_PORT', '5432')
DB_NAME = os.getenv('POSTGRES_DB', 'flows_db')

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