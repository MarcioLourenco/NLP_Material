import logging

import boto3

from src.capcobot_question_manager import get_config

logger = logging.getLogger("CapcoBot")


def s3_boto3_client():
    logger.info("Iniciando conexão com S3")
    client = boto3.client(
        "s3",
        aws_access_key_id=get_config().AWS_ACCESS_KEY_ID,
        aws_secret_access_key=get_config().AWS_SECRET_ACCESS_KEY,
    )

    return client


def s3_boto3_session():
    logger.info("Iniciando conexão com S3")
    resource = boto3.Session(
        aws_access_key_id=get_config().AWS_ACCESS_KEY_ID,
        aws_secret_access_key=get_config().AWS_SECRET_ACCESS_KEY,
    )

    return resource
