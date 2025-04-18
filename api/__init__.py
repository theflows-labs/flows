# This file makes the api directory a Python package
from flask import Flask
from flask_cors import CORS
from .routes import dag_bp, task_bp, execution_bp

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    # Register blueprints
    app.register_blueprint(dag_bp, url_prefix='/api/dags')
    app.register_blueprint(task_bp, url_prefix='/api/tasks')
    app.register_blueprint(execution_bp, url_prefix='/api/executions')

    return app 