from flask import Flask
from werkzeug.exceptions import HTTPException

from src.features.exceptions import CheckedException
from src.features.logging_supplier import get_logger
from src.flaskr.unified_item import unified_item_blueprint
from src.flaskr.ftp import ftp_blueprint
from src.utils.flask_utils import create_failure_response


def create_app():
    app = Flask(__name__)
    logger = get_logger("flask")

    @app.route("/")
    def home():
        return "Hello, World!"

    @app.errorhandler(Exception)
    def handle_exception(exception: Exception):
        if isinstance(exception, CheckedException):
            return create_failure_response(exception.message, exception.status_code)
        if isinstance(exception, HTTPException):
            logger.exception("http error: %s", exception)
            return create_failure_response(exception.description, exception.code)
        logger.exception("server exception: %s", exception)
        return create_failure_response("server error", 500)

    app.register_blueprint(ftp_blueprint)
    app.register_blueprint(unified_item_blueprint)
    return app
