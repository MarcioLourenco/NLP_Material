import logging
import os
from io import BytesIO
import shutil

from src.capcobot_question_manager import get_config

logger = logging.getLogger("CapcoBot")

BUCKET = get_config().BUCKET
WORKDIR = get_config().WORKDIR
DATA_FOLDER = get_config().DATA_FOLDER
DATA_PATH = f"{WORKDIR}{DATA_FOLDER}"
LOCAL_STORAGE = True


def send_file(file_object, filename: str, path: str):
    filename = os.path.join(os.path.expanduser("~"), BUCKET, path, filename)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    if isinstance(file_object, str):
        with open(os.path.join(filename), "w") as f:
            f.write(file_object)
    else:
        with open(os.path.join(filename), "wb") as f:
            f.write(file_object.read())


def get_file(filename: str, folder: str):
    _, file_extension = os.path.splitext(filename)
    file_path = os.path.join(
        os.path.expanduser("~"), BUCKET, folder, os.path.basename(filename)
    )
    if file_extension in [".csv", ".json", ".txt"]:
        with open(file_path, "r") as f:
            binary_data = f.read()
        binary_data = bytes(binary_data, encoding="utf-8")
    else:
        with open(
            os.path.join(
                os.path.expanduser("~"), BUCKET, folder, os.path.basename(filename)
            ),
            "rb",
        ) as f:
            binary_data = f.read()
    return BytesIO(binary_data)


def list_files(path: str, extensions: str = None) -> list:
    files_list = []
    if os.path.isdir(os.path.join(os.path.expanduser("~"), BUCKET, path)):
        files = os.listdir(os.path.join(os.path.expanduser("~"), BUCKET, path))
        for file in files:
            if file.endswith(extensions):
                files_list.append(file)

    return files_list


def upload_file(file, language: str = None, name: str = None, path: str = None):
    filename = os.path.join(os.path.expanduser("~"), BUCKET, path)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    file.save(filename)
    return "Arquivo enviado com sucesso"


def delete_file(filename: str, path: str):
    filename = os.path.join(os.path.expanduser("~"), BUCKET, path, filename)
    try:
        os.remove(filename)
    except Exception as e:
        logger.error(f"Não foi possível excluir o arquivo {filename} na pasta {path}")
        logger.error(f"Detalhes do erro: {e}")
        raise ValueError(
            f"Não foi possível excluir o arquivo {filename} na pasta {path}"
        )


def move_file(
    filename: str,
    origin_path: str,
    target_path: str,
    sufix: str = None,
    new_name: str = None,
):
    origin_path = os.path.join(os.path.expanduser("~"), BUCKET, origin_path, filename)
    target_path = os.path.join(os.path.expanduser("~"), BUCKET, target_path, filename)

    if new_name:
        target_path = os.path.join(os.path.dirname(target_path), new_name)
    if sufix:
        file_path, file_extension = os.path.splitext(target_path)
        target_path = file_path + sufix + file_extension

    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    shutil.copyfile(
        origin_path,
        target_path,
    )
