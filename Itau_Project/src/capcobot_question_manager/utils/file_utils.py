import json
import logging
import os

from src.capcobot_question_manager import get_config
from src.capcobot_question_manager.clients.s3_client import (
    s3_boto3_session,
)

if get_config().STORAGE == "LOCAL":
    from src.capcobot_question_manager.utils.file_utils_libs import (
        local_file_utils as file_utils,
    )
elif get_config().STORAGE == "S3":
    from src.capcobot_question_manager.utils.file_utils_libs import (
        s3_file_utils as file_utils,
    )

logger = logging.getLogger("CapcoBot")


BUCKET = get_config().BUCKET
WORKDIR = get_config().WORKDIR
DATA_FOLDER = get_config().DATA_FOLDER
DATA_PATH = f"{WORKDIR}{DATA_FOLDER}"
STORAGE = get_config().STORAGE


def __json_validator(json_object: json):
    try:
        json.loads(json_object)
    except ValueError as e:
        logger.error("Json invalido")
        raise e
    return True


def send_file(file_object, filename: str, path: str):
    _, file_extension = os.path.splitext(filename)
    if "json" in file_extension:
        __json_validator(file_object)

    return file_utils.send_file(file_object=file_object, filename=filename, path=path)


def get_file_from_s3(filename: str, folder: str):
    return file_utils.get_file(filename=filename, folder=folder)


def file_exists(filename: str, path: str, language: str = None):
    path = f"{path}/{language}" if language else path
    files = list_files_in_s3(path=path)
    return filename in files


def list_files_in_s3(path: str, extensions: str = None) -> list:
    extensions = extensions if extensions else ""
    files_list = []
    if path[-1] != "/":
        path += "/"

    files_list = file_utils.list_files(path=path, extensions=extensions)

    return files_list


def upload_file_to_s3(file, language: str = None, name: str = None, path: str = None):
    if not name:
        name = file.filename
    if not path:
        if language:
            path = f"{DATA_PATH}/{language}/{name}"
        else:
            logger.error("Não foi informado path ou language")
            raise ValueError("Não foi informado path ou language")
    else:
        if path[-1] == "/":
            path = f"{path}{name}"
        else:
            path = f"{path}/{name}"

    return file_utils.upload_file(file=file, language=language, name=name, path=path)


def delete_file(filename: str, path: str):
    if not file_exists(filename, path):
        logger.error(f"Arquivo {filename} não encontrado na pasta {path}")
        raise ValueError(f"Arquivo {filename} não encontrado na pasta {path}")

    file_utils.delete_file(filename=filename, path=path)

    if not file_exists(filename, path):
        return "Arquivo excluído com sucesso"
    logger.error(f"Não foi possível excluir o arquivo {filename} na pasta {path}")
    raise ValueError(f"Não foi possível excluir o arquivo {filename} na pasta {path}")


def move_file(
    filename: str,
    origin_path: str,
    target_path: str,
    copy: bool = False,
    sufix: str = None,
    new_name: str = None,
):
    if origin_path == target_path and sufix is None and new_name is None:
        raise ValueError(
            "As pastas de origem e destino são iguais e o sufixo não foi informado"
        )
    file_utils.move_file(
        filename=filename,
        origin_path=origin_path,
        target_path=target_path,
        sufix=sufix,
        new_name=new_name,
    )

    if not copy:
        name = new_name if new_name else filename
        if sufix:
            file_path, file_extension = os.path.splitext(name)
            name = file_path + sufix + file_extension
        if file_exists(filename=name, path=target_path):
            delete_file(filename, origin_path)
        else:
            logger.error("Não foi possível mover o arquivo")
            raise ValueError("Não foi possível mover o arquivo")

    return f"Arquivo {'copiado' if copy else 'movido'} com sucesso"


def start_exclusion_process():
    send_file(
        file_object="created",
        filename="exclude_flag.flg",
        path=f"{DATA_PATH}",
    )
    start_process()


def start_process():
    session = s3_boto3_session()

    ec2 = session.resource("ec2", region_name="us-east-1")

    instance_id = "i-0d3145dac937169dd"

    instance = ec2.Instance(instance_id)

    instance.start()
