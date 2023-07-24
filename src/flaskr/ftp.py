import os
import shutil

import flask
from flask import Blueprint, jsonify

from src.features.exceptions import CheckedException
from src.module import ftp_supplier
from src.utils.flask_utils import create_failure_response, create_success_response

ftp_blueprint = Blueprint("ftp", __name__, url_prefix="/flask/ftp")


@ftp_blueprint.route("/list_dir", methods=["GET"])
def list_dir():
    return create_success_response(
        dirs=ftp_supplier.list_dir(flask.request.json.get("dir_path", "."))
    )


@ftp_blueprint.route("/download", methods=["GET"])
def download():
    file_path = flask.request.json.get("file_path", ".")
    file_path, abs_path = ftp_supplier.get_abs_path(file_path, check_is_file=True)
    return (
        flask.send_from_directory(
            os.path.dirname(abs_path),
            os.path.basename(file_path),
            as_attachment=True,
        ),
        200,
    )


@ftp_blueprint.route("/delete", methods=["DELETE"])
def delete():
    path = flask.request.json.get("path", None)
    if path is None:
        raise CheckedException("path is required")
    path, abs_path = ftp_supplier.get_abs_path(path, check_exists=True)
    if os.path.islink(abs_path):
        os.unlink(abs_path)
        return create_success_response()
    elif os.path.isfile(abs_path):
        os.remove(abs_path)
        return create_success_response()
    elif os.path.isdir(abs_path):
        shutil.rmtree(abs_path)
        return create_success_response()
    return create_failure_response("unknown file type")


@ftp_blueprint.route("/create_folder", methods=["POST"])
def create_folder():
    dir_path = flask.request.json.get("dir_path", None)
    if dir_path is None:
        raise CheckedException("dir_path is required")
    dir_path, abs_path = ftp_supplier.get_abs_path(dir_path, check_not_exists=True)
    os.makedirs(abs_path)
    return create_success_response()


@ftp_blueprint.route("/upload", methods=["POST"])
def upload():
    override = flask.request.form.get("override", False)
    file_path = flask.request.form.get("file_path", None)
    if file_path is None:
        raise CheckedException("file_path is required")
    file_path, abs_path = ftp_supplier.get_abs_path(file_path)
    if os.path.isdir(abs_path):
        raise CheckedException("cannot override a directory")
    if os.path.exists(abs_path) and not override:
        raise CheckedException("file already exists")
    file = flask.request.files.get("file", None)
    if file is None:
        raise CheckedException("file is required")
    file.save(abs_path)
    return create_success_response()
