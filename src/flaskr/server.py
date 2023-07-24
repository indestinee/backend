from flask import Flask, jsonify
from werkzeug.exceptions import NotFound, HTTPException

from src.features.exceptions import CheckedException
from src.features.logging_supplier import get_logger
from src.flaskr.ftp import ftp_blueprint


def create_app():
    app = Flask(__name__)
    logger = get_logger("flask")

    @app.route("/")
    def home():
        return "Hello, World!"

    @app.errorhandler(Exception)
    def handle_exception(e: Exception):
        if isinstance(e, CheckedException):
            return jsonify({"success": False, "message": e.message}), e.status_code
        elif isinstance(e, HTTPException):
            return jsonify({"success": False, "message": e.description}), e.code
        logger.exception(f"server exception {e}")
        return jsonify({"success": False, "message": "server exception"}), 500

    app.register_blueprint(ftp_blueprint)
    return app
