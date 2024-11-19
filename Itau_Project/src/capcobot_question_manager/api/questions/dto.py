"""Parsers and serializers for /questions API endpoints."""
from flask_restx.reqparse import RequestParser
import os


def api_token(key):
    if key != os.environ.get("CAPCOBOT_API_KEY"):
        raise ValueError("Chave inválida")
    return key


create_question_reqparser = RequestParser(bundle_errors=True)

create_question_reqparser.add_argument(
    "key",
    type=api_token,
    location="form",
    required=True,
    nullable=False,
    case_sensitive=False,
)
create_question_reqparser.add_argument(
    "question",
    type=str,
    location="form",
    required=True,
    nullable=False,
    case_sensitive=False,
)
create_question_reqparser.add_argument(
    "files",
    type=str,
    location="form",
    required=False,
    nullable=False,
    default="",
)
create_question_reqparser.add_argument(
    "role",
    type=str,
    location="form",
    required=False,
    nullable=False,
    case_sensitive=True,
    default="Default",
)
