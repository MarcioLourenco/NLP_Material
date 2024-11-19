"""API endpoint definitions for /files namespace."""
from http import HTTPStatus

from flask_restx import Namespace, Resource

from src.capcobot_question_manager.api.files.dto import (
    create_file_reqparser,
    list_file_reqparser,
    delete_file_reqparser,
)
from src.capcobot_question_manager.api.files.file import (
    upload_file,
    get_available_files,
    delete_file_from_cloud,
)

file_ns = Namespace(name="files", validate=True)


@file_ns.route("", endpoint="file_list")
@file_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
@file_ns.response(int(HTTPStatus.UNAUTHORIZED), "Unauthorized.")
@file_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
class fileList(Resource):
    """Handles HTTP requests to URL: /files."""

    @file_ns.doc(security="Bearer")
    @file_ns.expect(create_file_reqparser)
    def post(self):
        """Create a file."""
        file_dict = create_file_reqparser.parse_args()
        return upload_file(file_dict)

    @file_ns.doc(security="Bearer")
    @file_ns.expect(list_file_reqparser)
    def get(self):
        """list files."""
        file_dict = list_file_reqparser.parse_args()
        return get_available_files(file_dict)

    @file_ns.doc(security="Bearer")
    @file_ns.expect(delete_file_reqparser)
    def delete(self):
        """delete a file."""
        file_dict = delete_file_reqparser.parse_args()
        return delete_file_from_cloud(file_dict)
