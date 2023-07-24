import json

import flask
from flask import Blueprint

from src.data.cipher_info import CipherInfo
from src.module import cipher_info_dao
from src.utils.flask_utils import create_success_response

cipher_info_blueprint = Blueprint(
    "cipher_info", __name__, url_prefix="/flask/cipher_info"
)


@cipher_info_blueprint.route("/get_cipher_info_by_identifier", methods=["GET"])
def get_cipher_info_by_identifier():
    cipher_identifier = flask.request.json.get("cipher_identifier", "")
    source = flask.request.json.get("source", "")
    return create_success_response(
        cipher_infos=cipher_info_dao.query_by_identifier(source, cipher_identifier)
    )


@cipher_info_blueprint.route("/insert_or_replace", methods=["POST"])
def insert_or_replace():
    cipher_infos = [
        CipherInfo(**each) for each in flask.request.json.get("cipher_infos", "[]")
    ]
    cipher_info_dao.insert_or_replace(cipher_infos)
    return create_success_response()


@cipher_info_blueprint.route("/delete_by_identifier_and_names", methods=["DELETE"])
def delete():
    cipher_identifier = flask.request.json.get("cipher_identifier", "")
    source = flask.request.json.get("source", "")
    names = flask.request.json.get("names", None)
    cipher_info_dao.delete_by_identifier_and_names(source, cipher_identifier, names)
    return create_success_response()
