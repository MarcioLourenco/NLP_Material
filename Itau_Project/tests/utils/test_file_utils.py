import json
import os
from tempfile import NamedTemporaryFile

import pytest

from src.capcobot_question_manager import get_config
from src.capcobot_question_manager.utils import file_utils

WORKDIR = get_config().WORKDIR
DATA_FOLDER = get_config().DATA_FOLDER
DATA_PATH = f"{WORKDIR}{DATA_FOLDER}"


@pytest.fixture
def bucket_name(app):
    return app.BUCKET


@pytest.fixture
def s3_test(s3_client, bucket_name):
    s3_client.create_bucket(Bucket=bucket_name)
    yield


def test_send_file(s3_resource, bucket_name, s3_test):
    file_text = "test"
    folder = "data/IT"
    with NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        with open(tmp.name, "w", encoding="UTF-8") as f:
            f.write(file_text)
        file_utils.send_file(tmp, filename="file.txt", path=folder)

    assert s3_resource.Bucket(bucket_name).objects.filter(Prefix=folder)


def test_send_json_file(s3_resource, bucket_name, s3_test):
    folder = "data/IT"
    file_utils.send_file(
        json.dumps({"content": "json test"}),
        filename="file.json",
        path=folder,
    )

    files = s3_resource.Bucket(bucket_name).objects.filter(Prefix=folder)
    founded = False
    for file in files:
        if "file.json" in file.key:
            founded = founded or True
    assert founded


def test_send_bad_json_file(s3_resource, bucket_name, s3_test):
    with pytest.raises(Exception):
        folder = "data/IT"
        file_utils.send_file(
            "'content': 'json test'", filename="file.json", path=folder
        )

    files = s3_resource.Bucket(bucket_name).objects.filter(Prefix=folder)
    founded = False
    for file in files:
        if "file.json" in file.key:
            founded = founded or True
    assert not founded


def test_list_files_in_s3(s3_client, bucket_name, s3_test):
    file_text = "test"
    with NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        with open(tmp.name, "w", encoding="UTF-8") as f:
            f.write(file_text)

        s3_client.upload_file(tmp.name, bucket_name, "data/IT/file12.pdf")
        s3_client.upload_file(tmp.name, bucket_name, "data/IT/file22.json")

    objects = file_utils.list_files_in_s3(path="data/IT")
    assert objects == ["file12.pdf", "file22.json"]


def test_move_file(s3_client, bucket_name, s3_test):
    file_text = "test"
    with NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        with open(tmp.name, "w", encoding="UTF-8") as f:
            f.write(file_text)

        s3_client.upload_file(tmp.name, bucket_name, "data/IT/old_path/file12.pdf")

    file_utils.move_file(
        filename="file12.pdf",
        origin_path="data/IT/old_path",
        target_path="data/IT/new_path",
    )

    origin_folder_content = file_utils.list_files_in_s3(path="data/IT/old_path")
    target_folder_content = file_utils.list_files_in_s3(path="data/IT/new_path")
    assert "file12.pdf" in target_folder_content
    assert "file12.pdf" not in origin_folder_content


def test_move_file_with_copy(s3_client, bucket_name, s3_test):
    file_text = "test"
    with NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        with open(tmp.name, "w", encoding="UTF-8") as f:
            f.write(file_text)

        s3_client.upload_file(tmp.name, bucket_name, "data/IT/old_path/file12.pdf")

    file_utils.move_file(
        filename="file12.pdf",
        origin_path="data/IT/old_path",
        target_path="data/IT/new_path",
        copy=True,
    )

    origin_folder_content = file_utils.list_files_in_s3(path="data/IT/old_path")
    target_folder_content = file_utils.list_files_in_s3(path="data/IT/new_path")
    assert "file12.pdf" in target_folder_content
    assert "file12.pdf" in origin_folder_content


def test_move_file_with_suffix(s3_client, bucket_name, s3_test):
    file_text = "test"
    with NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        with open(tmp.name, "w", encoding="UTF-8") as f:
            f.write(file_text)

        s3_client.upload_file(tmp.name, bucket_name, "data/IT/old_path/file12.pdf")

    file_utils.move_file(
        filename="file12.pdf",
        origin_path="data/IT/old_path",
        target_path="data/IT/new_path",
        sufix="_test",
    )

    origin_folder_content = file_utils.list_files_in_s3(path="data/IT/old_path")
    target_folder_content = file_utils.list_files_in_s3(path="data/IT/new_path")
    assert "file12_test.pdf" in target_folder_content
    assert "file12.pdf" not in origin_folder_content


def test_move_file_with_new_name(s3_client, bucket_name, s3_test):
    file_text = "test"
    with NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        with open(tmp.name, "w", encoding="UTF-8") as f:
            f.write(file_text)

        s3_client.upload_file(tmp.name, bucket_name, "data/IT/old_path/file12.pdf")

    file_utils.move_file(
        filename="file12.pdf",
        origin_path="data/IT/old_path",
        target_path="data/IT/new_path",
        new_name="teste.pdf",
    )

    origin_folder_content = file_utils.list_files_in_s3(path="data/IT/old_path")
    target_folder_content = file_utils.list_files_in_s3(path="data/IT/new_path")
    assert "teste.pdf" in target_folder_content
    assert "file12.pdf" not in origin_folder_content


def test_move_file_with_all_params(s3_client, bucket_name, s3_test):
    file_text = "test"
    with NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        with open(tmp.name, "w", encoding="UTF-8") as f:
            f.write(file_text)

        s3_client.upload_file(tmp.name, bucket_name, "data/IT/old_path/file12.pdf")

    file_utils.move_file(
        filename="file12.pdf",
        origin_path="data/IT/old_path",
        target_path="data/IT/new_path",
        copy=True,
        sufix="_tst",
        new_name="teste.pdf",
    )

    origin_folder_content = file_utils.list_files_in_s3(path="data/IT/old_path")
    target_folder_content = file_utils.list_files_in_s3(path="data/IT/new_path")
    assert "teste_tst.pdf" in target_folder_content
    assert "file12.pdf" in origin_folder_content


def test_upload_file_to_s3(s3_client, bucket_name, s3_test):
    file_text = "test"
    file_name = ""
    with NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        file_name = os.path.basename(tmp.name)
        with open(tmp.name, "w", encoding="UTF-8") as f:
            f.write(file_text)
        file_utils.upload_file_to_s3(file=tmp.file, name=file_name, language="PT")

    assert file_name in file_utils.list_files_in_s3(path=f"{DATA_PATH}/PT")


def test_upload_file_to_s3_with_path(s3_client, bucket_name, s3_test):
    file_text = "test"
    file_name = ""
    with NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        file_name = os.path.basename(tmp.name)
        with open(tmp.name, "w", encoding="UTF-8") as f:
            f.write(file_text)
        file_utils.upload_file_to_s3(
            file=tmp.file, name=file_name, path=f"{DATA_PATH}/PT/test/"
        )
    assert file_name in file_utils.list_files_in_s3(path=f"{DATA_PATH}/PT/test/")
