import os
import shutil
from urllib.parse import unquote

import flask
from flask import Blueprint, send_file

from src.data.exceptions import CheckedException
from src.module import ftp_supplier
from src.utils.flask_utils import create_failure_response, create_success_response

ftp_blueprint = Blueprint("ftp", __name__, url_prefix="/flask/ftp")


@ftp_blueprint.route("/list_dir", methods=["GET"])
def list_dir():
    return create_success_response(
        dirs=ftp_supplier.list_dir(flask.request.args.get("dir_path", "."))
    )


@ftp_blueprint.route("/download", methods=["GET"])
def download():
    file_path = unquote(flask.request.args.get("file_path", "."))
    password = flask.request.args.get("password", None)
    if password:
        result = ftp_supplier.decrypt_file(file_path, password)
        file_data = result.pop("file_data")
        return send_file(file_data, **result, as_attachment=True), 200

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
    path = str(flask.request.json["path"])
    if path is None:
        raise CheckedException("path is required")
    path, abs_path = ftp_supplier.get_abs_path(path, check_exists=True)
    if os.path.islink(abs_path):
        os.unlink(abs_path)
        return create_success_response()
    if os.path.isfile(abs_path):
        os.remove(abs_path)
        return create_success_response()
    if os.path.isdir(abs_path):
        shutil.rmtree(abs_path)
        return create_success_response()
    return create_failure_response("unknown file type")


@ftp_blueprint.route("/create_folder", methods=["POST"])
def create_folder():
    dir_path = str(flask.request.json["dir_path"])
    if dir_path is None:
        raise CheckedException("dir_path is required")
    dir_path, abs_path = ftp_supplier.get_abs_path(dir_path, check_not_exists=True)
    os.makedirs(abs_path)
    return create_success_response()


@ftp_blueprint.route("/upload", methods=["POST"])
def upload():
    override = flask.request.form.get("override", "False").lower() == "true"
    file_path = flask.request.form["file_path"]
    if file_path is None:
        raise CheckedException("file_path is required")
    file_path, abs_path = ftp_supplier.get_abs_path(file_path)
    if os.path.isdir(abs_path):
        raise CheckedException("cannot override a directory")
    if os.path.exists(abs_path) and not override:
        raise CheckedException("file already exists")
    file = flask.request.files["file"]
    if not file:
        raise CheckedException("file is required")
    file.save(abs_path)
    return create_success_response()
