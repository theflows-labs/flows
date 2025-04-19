from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

import os
import sys
from pathlib import Path

# Add the plugin directory to the Python path
plugin_dir = Path(__file__).parent.parent.parent  # Go up one more level to reach airflow_plugin
sys.path.insert(0, str(plugin_dir))

# Set environment variables for database connection
os.environ['DB_USER'] = 'postgress'
os.environ['DB_PASSWORD'] = 'postgress'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '5433'
os.environ['DB_NAME'] = 'postgress'

# Import database constants
from config.database import SQLALCHEMY_CONN

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = None

# Override sqlalchemy.url with the centralized connection string
print(f"Using database connection: {SQLALCHEMY_CONN}")
config.set_main_option("sqlalchemy.url", SQLALCHEMY_CONN)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        print("Creating tables in offline mode...")
        context.run_migrations()
        print("Tables created successfully!")


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Override sqlalchemy.url again to ensure it's using our connection string
    config.set_main_option("sqlalchemy.url", SQLALCHEMY_CONN)
    
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            print("Creating tables in online mode...")
            context.run_migrations()
            print("Tables created successfully!")


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 