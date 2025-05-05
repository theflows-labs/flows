from flask import Flask
from flask_cors import CORS
from api.routes import flow_bp, task_bp, execution_bp, task_type_bp
from config.database import (
    SQLALCHEMY_CONN,
    SQLALCHEMY_TRACK_MODIFICATIONS,
    SQLALCHEMY_ENGINE_OPTIONS
)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_CONN
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = SQLALCHEMY_ENGINE_OPTIONS

    # Configure URL handling
    app.url_map.strict_slashes = False

    # Register blueprints
    app.register_blueprint(flow_bp, url_prefix='/api/flows')
    app.register_blueprint(task_bp, url_prefix='/api/tasks')
    app.register_blueprint(execution_bp, url_prefix='/api/executions')
    app.register_blueprint(task_type_bp, url_prefix='/api/task-types')

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Resource not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500

    @app.errorhandler(ValueError)
    def value_error(error):
        return {'error': str(error)}, 400

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True) 