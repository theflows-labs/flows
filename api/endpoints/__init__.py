# This file makes the routes directory a Python package 

from .dag_routes import bp as dag_bp
from .task_routes import bp as task_bp
from .execution_routes import bp as execution_bp

__all__ = ['dag_bp', 'task_bp', 'execution_bp'] 