"""Business logic for /widgets API endpoints."""
import logging
import os
from http import HTTPStatus
from io import BytesIO

import PyPDF2
from flask import jsonify
from flask_restx import abort
from werkzeug.utils import secure_filename

from src.capcobot_question_manager import get_config
from src.capcobot_question_manager.utils.file_utils import (
    list_files_in_s3,
    start_process,
    upload_file_to_s3,
    move_file,
)
from src.capcobot_question_manager.utils.language_utils import (
    get_available_languages,
    get_language,
    get_language_from_text,
)

logger = logging.getLogger("CapcoBot")

FILES_FORMAT = get_config().FILES_FORMAT
WORKDIR = get_config().WORKDIR
DATA_FOLDER = get_config().DATA_FOLDER
DATA_PATH = f"{WORKDIR}{DATA_FOLDER}"


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in FILES_FORMAT


def upload_file(file_dict):
    file = file_dict["files"]
    if not allowed_file(file.filename):
        logger.warn(f"api.file - file_name: {file.filename}")
        abort(415, description="File type is unsupported")
    try:
        text = BytesIO(file.read())
        pdf_reader = PyPDF2.PdfReader(text)
        middle_page = int(len(pdf_reader.pages) / 2)
        page_text = pdf_reader.pages[middle_page].extract_text()
        language = get_language_from_text(page_text)["language"]
        file.seek(0)

        file.filename = secure_filename(file.filename)
        upload_file_to_s3(file=file, path=f"{DATA_PATH}/{language}/pending")
        if get_config().ENVIRONMENT == "production":
            start_process()

        response = jsonify(status="success", message=str("File uploaded successfully"))
        response.status_code = HTTPStatus.CREATED
        return response

    except Exception as e:
        logger.error("Erro ao enviar o arquivo.")
        logger.error("Mensagem: " + str(e))
        abort(500, description="error sending file")


def get_available_files(file_dict):
    requested_language = file_dict["language"]
    if str.upper(requested_language) == "ALL":
        languages = get_available_languages()
    else:
        languages = [get_language(requested_language)["language"]]
    response_list = list()
    for language in languages:
        response = list_files_in_s3(
            path=f"{DATA_PATH}/{language}/processed", extensions="pdf"
        )
        for iten in response:
            response_list.append({"name": iten, "language": language})

    response = jsonify(
        status="success",
        message=str(f"Files in path {DATA_PATH} successfully listed"),
        content=response_list,
    )
    response.status_code = HTTPStatus.OK
    return response


def delete_file_from_cloud(file_dict):
    requested_language = file_dict["language"]
    requested_file = file_dict["name"]

    language = get_language(requested_language)["language"]

    try:
        move_file(
            filename=os.path.basename(requested_file),
            origin_path=f"{DATA_PATH}/{requested_language}/processed",
            target_path=f"{DATA_PATH}/{requested_language}/delete",
            copy=True,
        )
        response = jsonify(
            status="success",
            message=str(
                f"File {requested_file} in folder data/{language} successfully marked"
                " to be deleted"
            ),
        )
        response.status_code = HTTPStatus.OK
        return response
    except Exception as e:
        print(e)
        abort(400, description=f"File not found: {e}")
