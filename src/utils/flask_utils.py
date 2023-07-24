from flask import jsonify


def create_response(success: bool, status_code: int = 200, **kwargs):
    return jsonify({"success": success, **kwargs}), status_code


def create_success_response(status_code: int = 200, **kwargs):
    return create_response(True, status_code, **kwargs)


def create_failure_response(message: str, status_code: int = 200):
    return create_response(False, status_code, message=message)
