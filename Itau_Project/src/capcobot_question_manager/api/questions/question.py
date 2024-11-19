"""Business logic for /widgets API endpoints."""
from http import HTTPStatus

from flask import jsonify

# from flask_restx import abort
import logging
from src.capcobot_question_manager.api.questions.generate_answer_GPT import (
    GenerateAnswerGPT,
)
from src.capcobot_question_manager.utils.language_utils import (
    get_language_from_text,
    get_default_language,
)

logger = logging.getLogger("CapcoBot")


def generate_answer(question_dict):
    question = question_dict["question"]
    files = question_dict["files"]
    role = question_dict.get("role", "Executive")
    language = get_language_from_text(question)

    if files:
        files = [file.strip() for file in files.split(",")]
    else:
        files = []

    logger.info("Arquivos enviados: " + str(files))
    logger.info("Role: " + str(role))
    logger.info("Question: " + str(question))
    logger.info("Idioma identificado: " + str(language))

    if len(question.split()) < 3:
        gpt_answer = get_default_language().get("short_question")
    else:
        gpt_answer = GenerateAnswerGPT().generate_answer_GPT(
            question, language.get("language"), role, files
        )

    response = jsonify(status="success", message=str(gpt_answer))
    response.status_code = HTTPStatus.OK
    return response
