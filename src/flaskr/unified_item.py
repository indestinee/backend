import flask
from flask import Blueprint

from src.data.unified_item import UnifiedItem
from src.module import unified_item_dao, unified_item_data_loader
from src.utils.flask_utils import create_success_response

unified_item_blueprint = Blueprint("item", __name__, url_prefix="/flask/item")


@unified_item_blueprint.route("/get", methods=["GET"])
def get_by_identifier():
    source = flask.request.args.get("source", "")
    cipher_identifier = flask.request.args.get("cipher_identifier", "")
    name = flask.request.args.get("name", None)
    password = flask.request.args.get("password", None)
    items = unified_item_data_loader.query_by_identifier(
        source, cipher_identifier, name, password
    )
    return create_success_response(items=items)


@unified_item_blueprint.route("/insert_or_replace", methods=["POST"])
def insert_or_replace():
    items = [
        UnifiedItem.loads(each) for each in flask.request.json.get("items", "[]")
    ]
    unified_item_dao.insert_or_replace(items)
    return create_success_response()


@unified_item_blueprint.route("/delete_by_identifier_and_name", methods=["DELETE"])
def delete():
    cipher_identifier = flask.request.json.get("cipher_identifier", "")
    source = flask.request.json.get("source", "")
    name = flask.request.json.get("name", None)
    unified_item_dao.delete_by_values(source=source, cipher_identifier=cipher_identifier, name=name)
    return create_success_response()
