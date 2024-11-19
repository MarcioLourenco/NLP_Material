"""Parsers and serializers for /files API endpoints."""
from flask_restx.reqparse import RequestParser
import os
import werkzeug


def api_token(key):
    if key != os.environ.get("CAPCOBOT_API_KEY"):
        raise ValueError("Chave inválida")
    return key


create_file_reqparser = RequestParser(bundle_errors=True)

create_file_reqparser.add_argument(
    "key",
    type=api_token,
    location="form",
    required=True,
    nullable=False,
    case_sensitive=False,
)
create_file_reqparser.add_argument(
    "files",
    type=werkzeug.datastructures.FileStorage,
    location="files",
    required=True,
    nullable=False,
)


list_file_reqparser = RequestParser(bundle_errors=True)

list_file_reqparser.add_argument(
    "key",
    type=api_token,
    location="form",
    required=True,
    nullable=False,
    case_sensitive=False,
)
list_file_reqparser.add_argument(
    "language", type=str, location="form", required=True, nullable=False, default="ALL"
)


delete_file_reqparser = RequestParser(bundle_errors=True)

delete_file_reqparser.add_argument(
    "key",
    type=api_token,
    location="form",
    required=True,
    nullable=False,
    case_sensitive=False,
)
delete_file_reqparser.add_argument(
    "language", type=str, location="form", required=True, nullable=False, default="ALL"
)
delete_file_reqparser.add_argument(
    "name", type=str, location="form", required=True, nullable=False
)
