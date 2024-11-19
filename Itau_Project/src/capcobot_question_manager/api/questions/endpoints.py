"""API endpoint definitions for /questions namespace."""
from http import HTTPStatus

from flask_restx import Namespace, Resource

from src.capcobot_question_manager.api.questions.dto import (
    create_question_reqparser,
)
from src.capcobot_question_manager.api.questions.question import (
    generate_answer,
)

question_ns = Namespace(name="questions", validate=True)


@question_ns.route("", endpoint="question_list")
@question_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
@question_ns.response(int(HTTPStatus.UNAUTHORIZED), "Unauthorized.")
@question_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
class questionList(Resource):
    """Handles HTTP requests to URL: /questions."""

    @question_ns.doc(security="Bearer")
    @question_ns.expect(create_question_reqparser)
    def post(self):
        """Create a question."""
        question_dict = create_question_reqparser.parse_args()
        return generate_answer(question_dict)
