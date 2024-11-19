"""API blueprint configuration."""
from flask import Blueprint
from flask_restx import Api

from src.capcobot_question_manager.api.questions.endpoints import (
    question_ns,
)
from src.capcobot_question_manager.api.files.endpoints import (
    file_ns,
)

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")
authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}

api = Api(
    api_bp,
    version="1.0",
    title="Capcobot API",
    description="Welcome to the Swagger UI documentation site!",
    doc="/ui",
)

api.add_namespace(question_ns, path="/questions")
api.add_namespace(file_ns, path="/files")
