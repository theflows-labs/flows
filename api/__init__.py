# This file makes the api directory a Python package
from flask import Flask
from flask_cors import CORS
from .routes import flow_bp, task_bp, execution_bp, task_type_bp

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    # Register blueprints
    app.register_blueprint(flow_bp, url_prefix='/api/flows')
    app.register_blueprint(task_bp, url_prefix='/api/tasks')
    app.register_blueprint(execution_bp, url_prefix='/api/executions')
    app.register_blueprint(task_type_bp, url_prefix='/api/task-types')

    return app 