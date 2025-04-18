from flask import Flask
from flask_cors import CORS
from .config.db import engine
from .models.base import Base
from .models import dag, task  # This import ensures models are registered with Base
from .routes import dag_bp, task_bp, execution_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Initialize database
    Base.metadata.create_all(bind=engine)

    # Register blueprints
    app.register_blueprint(dag_bp, url_prefix='/api/dags')
    app.register_blueprint(task_bp, url_prefix='/api/tasks')
    app.register_blueprint(execution_bp, url_prefix='/api/executions')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000) 