import logging
import os

import botocore
from datetime import date
from src.capcobot_question_manager import get_config
from src.capcobot_question_manager.clients.s3_client import (
    s3_boto3_client,
    s3_boto3_session,
)

logger = logging.getLogger("CapcoBot")


BUCKET = get_config().BUCKET
WORKDIR = get_config().WORKDIR
DATA_FOLDER = get_config().DATA_FOLDER
DATA_PATH = f"{WORKDIR}{DATA_FOLDER}"
STORAGE = get_config().STORAGE


def send_file(file_object, filename: str, path: str):
    s3 = s3_boto3_client()
    s3.put_object(Body=file_object, Bucket=BUCKET, Key=f"{path}/{filename}")


def get_file(filename: str, folder: str):
    logger.info("Iniciando conexão com S3")
    s3 = s3_boto3_client()
    try:
        logger.info(f"Obtendo arquivo {filename} na pasta {folder}")
        file_obj = s3.get_object(
            Bucket=BUCKET,
            Key=f"{folder}/{filename}",
        )
        logger.info("Arquivo carregado com sucesso")
        return file_obj["Body"]
    except botocore.exceptions.ClientError:
        logger.error(f" O arquivo {filename} não foi encontrado na pasta {folder}.")
        return None


def list_files(path: str, extensions: str = None) -> list:
    files_list = []
    logger.info("Iniciando conexão com S3")
    session = s3_boto3_session()
    s3 = session.resource("s3")
    logger.info(f"Iniciando geração de lista de arquivos na pasta {path}")
    bucket = s3.Bucket(BUCKET)
    files = bucket.objects.filter(Prefix=path)
    for file in files:
        temp_file = file.key.replace(path, "")
        if len(temp_file) > 0 and temp_file.endswith(extensions):
            files_list.append(temp_file)
    logger.info("Arquivo listado com sucesso")
    return files_list


def upload_file(file, language: str = None, name: str = None, path: str = None):
    s3 = s3_boto3_client()
    try:
        s3.upload_fileobj(
            Fileobj=file,
            Bucket=BUCKET,
            Key=path,
            ExtraArgs={"Metadata": {"created_at": str(date.today())}},
        )
    except Exception as e:
        logger.error("Não foi possível enviar o arquivo. Error: ", e)
        raise e
    return "Arquivo enviado com sucesso"


def delete_file(filename: str, path: str):
    s3 = s3_boto3_client()
    s3.delete_object(
        Bucket=BUCKET,
        Key=f"{path}/{filename}",
    )


def move_file(
    filename: str,
    origin_path: str,
    target_path: str,
    sufix: str = None,
    new_name: str = None,
):
    client = s3_boto3_client()
    response = client.list_objects_v2(Bucket=BUCKET, Prefix=f"{origin_path}/{filename}")
    source_key = response.get("Contents")
    if not source_key:
        logger.error(f"Arquivo {filename} não encontrado na pasta {origin_path}")
        raise ValueError(f"Arquivo {filename} não encontrado na pasta {origin_path}")
    source_key = source_key[0].get("Key")
    copy_source = {"Bucket": BUCKET, "Key": source_key}

    source_key = source_key.replace(origin_path, target_path)
    if new_name:
        source_key = f"{os.path.dirname(source_key)}/{new_name}"
    if sufix:
        file_path, file_extension = os.path.splitext(source_key)
        source_key = file_path + sufix + file_extension
    client.copy_object(Bucket=BUCKET, CopySource=copy_source, Key=source_key)
