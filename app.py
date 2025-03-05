import os
from flask import Flask

from config import SECRET_KEY, logger
from routes import register_routes
from utils.database import verify_db_connection


def create_app():
    """Create and configure the Flask application."""
    flask_app = Flask(__name__)
    flask_app.secret_key = SECRET_KEY

    if not flask_app.secret_key:
        raise ValueError("FLASK_SECRET_KEY environment variable is not set")

    if not verify_db_connection():
        raise RuntimeError("Unable to connect to database")

    template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    logger.info(f"Using template folder: {template_folder}")
    logger.info(f"Flask app instance: {flask_app}")

    register_routes(flask_app)

    logger.info("Registered routes:")
    for rule in flask_app.url_map.iter_rules():
        logger.info(f"Route: {rule}, Endpoint: {rule.endpoint}")

    return flask_app


# if __name__ == "__main__":
#     try:
#         app = create_app()
#         app.run(debug=True, host="0.0.0.0", port=5000)
#     except Exception as e:
#         logger.critical(f"Application failed to start: {str(e)}", exc_info=True)

app = create_app()