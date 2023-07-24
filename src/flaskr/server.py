from flask import Flask, jsonify
from werkzeug.exceptions import NotFound, HTTPException

from src.features.exceptions import CheckedException
from src.features.logging_supplier import get_logger
from src.flaskr.cipher_info import cipher_info_blueprint
from src.flaskr.ftp import ftp_blueprint
from src.utils.flask_utils import create_failure_response


def create_app():
    app = Flask(__name__)
    logger = get_logger("flask")

    @app.route("/")
    def home():
        return "Hello, World!"

    @app.errorhandler(Exception)
    def handle_exception(e: Exception):
        if isinstance(e, CheckedException):
            return create_failure_response(e.message, e.status_code)
        elif isinstance(e, HTTPException):
            return create_failure_response(e.description, e.code)
        logger.exception(f"server exception {e}")
        return create_failure_response("server error", 500)

    app.register_blueprint(ftp_blueprint)
    app.register_blueprint(cipher_info_blueprint)
    return app
