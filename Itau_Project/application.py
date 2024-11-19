import logging
import os
from io import BytesIO
from flask_apscheduler import APScheduler
import PyPDF2
import requests
from flask import Response, abort, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
from src.capcobot_question_manager import create_app, get_config

from src.capcobot_question_manager.api.questions.generate_answer_GPT import (
    GenerateAnswerGPT,
)
from src.capcobot_question_manager.utils.file_utils import (
    delete_file,
    list_files_in_s3,
    start_process,
    upload_file_to_s3,
    start_exclusion_process,
)
from src.capcobot_question_manager.utils.language_utils import (
    get_default_language,
    get_language,
    get_language_from_text,
    get_available_languages,
)


WORKDIR = get_config().WORKDIR
DATA_FOLDER = get_config().DATA_FOLDER
DATA_PATH = f"{WORKDIR}{DATA_FOLDER}"

application = create_app()

CORS(application)

logger = logging.getLogger("CapcoBot")


def api_key_check(key: str) -> bool:
    return key == os.environ.get("CAPCOBOT_API_KEY")


@application.errorhandler(400)
def bad_request(e):
    logger.warn(str(e))
    return jsonify(error=str(e)), 400


@application.errorhandler(401)
def unauthorized(e):
    logger.warn(str(e))
    return jsonify(error=str(e)), 401


@application.errorhandler(405)
def method_not_allowed(e):
    logger.warn(str(e))
    return jsonify(error=str(e)), 405


@application.errorhandler(415)
def unsupported_media_type(e):
    logger.warn(str(e))
    return jsonify(error=str(e)), 415


@application.errorhandler(500)
def internal_server_error(e):
    logger.warn(str(e))
    return jsonify(error=str(e)), 500


def post_check(request, required_params: list):
    if request.method != "POST":
        abort(405, description=f"request method {request.method} is not allowed")

    content_type = request.headers.get("Content-Type")
    if "application/json" not in content_type:
        abort(415, description=f"Media Type {content_type} is unsupported")

    has_param = True
    json_content = request.get_json()
    for required_param in required_params:
        has_param = has_param and (required_param in json_content)
    if "key" in json_content and has_param:
        has_content = True
        for required_param in required_params:
            has_content = has_content and (len(json_content[required_param]) > 0)
        if has_content:
            if api_key_check(json_content["key"]):
                return True
            else:
                abort(401, description="Key sent is wrong")

        else:
            logger.warn(f"Required params: {str(required_params)}")
            abort(400, description="Required parameters not found")

    else:
        logger.warn(f"Json keys: {str(json_content.keys())}")
        abort(400, description="Required parameters not found")


@application.route("/")
def index():
    resp = requests.get(f"{get_config().SITE_NAME}")
    excluded_headers = [
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    ]
    headers = [
        (name, value)
        for (name, value) in resp.raw.headers.items()
        if name.lower() not in excluded_headers
    ]
    response = Response(resp.content, resp.status_code, headers)
    return response


@application.route("/get_available_files", methods=["GET", "POST"])
def get_available_files():
    required_params = []
    if post_check(request, required_params):
        language = get_language(request.get_json().get("language"))["language"]
        response = list_files_in_s3(
            path=f"{DATA_PATH}/{language}/processed", extensions="pdf"
        )
        return response


@application.route("/get_available_files_v2", methods=["GET", "POST"])
def get_available_files_v2():
    required_params = []
    if post_check(request, required_params):
        requested_language = request.get_json().get("language")
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
        data = {
            "status": "success",
            "message": "Files in bucket 'data' successfully listed",
            "content": response_list,
        }
        return data, 200


@application.route("/<path:filename>")
def get_js(filename):
    if request.path == "/generate_answer":
        return generate_answer()
    else:
        resp = requests.get(
            url=f"{get_config().SITE_NAME}{request.path}",
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
        )

        excluded_headers = [
            "content-encoding",
            "content-length",
            "transfer-encoding",
            "connection",
        ]
        headers = [
            (name, value)
            for (name, value) in resp.raw.headers.items()
            if name.lower() not in excluded_headers
        ]
        response = Response(resp.content, resp.status_code, headers)
        return response


@application.route("/generate_answer", methods=["GET", "POST"])
def generate_answer():
    # required_params = ["question", "file", "role"]
    required_params = ["question"]
    if post_check(request, required_params):
        question = request.get_json()["question"]
        if len(question.split()) < 3:
            response = get_default_language().get("short_question")
        else:
            language = get_language_from_text(question)
            files = request.get_json().get("files")
            logger.warning("files: " + str(files))
            role = (
                request.get_json()["role"]
                if "role" in request.get_json()
                else "Executive"
            )

            response = GenerateAnswerGPT().generate_answer_GPT(
                question, language.get("language"), role, files
            )

        return response


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ["pdf"]


@application.route("/upload_file", methods=["GET", "POST"])
def upload_file():
    if request.method != "POST":
        abort(405, description=f"request method {request.method} is not allowed")

    content_type = request.headers.get("Content-Type")
    if "multipart/form-data" not in content_type:
        abort(415, description=f"Media Type {content_type} is unsupported")

    missing_args = []
    if "key" not in request.form:
        missing_args.append("key")
    if "file" not in request.files:
        missing_args.append("file")
    if len(missing_args) > 0:
        logger.warn(f"Required params not found: {str(missing_args)}.")
        abort(400, description="Required parameters not found")

    elif api_key_check(request.form["key"]):
        file = request.files["file"]
        if not allowed_file(file.filename):
            logger.warn(f"file_name: {file.filename}")
            abort(415, description="File type is unsupported")
        try:
            text = BytesIO(file.read())
            pdf_reader = PyPDF2.PdfReader(text)
            middle_page = int(len(pdf_reader.pages) / 2)
            page_text = pdf_reader.pages[middle_page].extract_text()
            language = get_language_from_text(page_text)["language"]
            file.seek(0)

            file.filename = secure_filename(file.filename)
            pre, ext = os.path.splitext(file.filename)
            upload_file_to_s3(file=file, path=f"{DATA_PATH}/{language}/pending")
            start_process()
            data = {
                "status": "success",
                "message": "File uploaded successfully",
            }

            return data, 200
        except Exception as e:
            logger.error("Erro ao enviar o arquivo.")
            logger.error("Mensagem: " + str(e))
            abort(500, description="error sending file")

    else:
        abort(401, description="Key sent is wrong")


@application.route("/delete_file", methods=["GET", "POST"])
def delete_file_from_s3():
    required_params = ["filename", "language"]
    if post_check(request, required_params):
        params = request.get_json()
        language = get_language(params.get("language"))["language"]
        try:
            response = delete_file(params.get("filename"), f"{DATA_PATH}/{language}")
            data = {
                "status": "success",
                "message": (
                    f"File {params.get('filename')} in folder"
                    f" data/{language} successfully deleted"
                ),
                "content": response,
            }
            return data, 200
        except Exception as e:
            print(e)
            abort(400, description=f"File not found: {e}")


scheduler = APScheduler()
scheduler.add_job(
    trigger="cron",
    id="Scheduled Task",
    func=start_exclusion_process,
    hour=20,
    minute=00,
)
scheduler.start()

if __name__ == "__main__":
    logger.setLevel(logging.getLevelName(os.environ.get("LOGLEVEL", "INFO")))
    application.debug = True
    application.run(port=443)
