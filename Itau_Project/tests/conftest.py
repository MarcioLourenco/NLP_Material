import json
import os

import boto3
import pytest
from moto import mock_s3

from src.capcobot_question_manager import get_config
from src.capcobot_question_manager.utils import file_utils


@pytest.fixture
def app():
    os.environ["BUCKET"] = get_config().BUCKET
    return get_config("testing")


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture
def s3_client(aws_credentials):
    with mock_s3():
        conn = boto3.client("s3", region_name="us-east-1")
        yield conn


@pytest.fixture
def s3_resource(aws_credentials):
    with mock_s3():
        s3 = boto3.Session().resource("s3", region_name="us-east-1")
        yield s3


@pytest.fixture
def bucket_name(app):
    return app.BUCKET


@pytest.fixture
def s3_test(s3_client, bucket_name):
    s3_client.create_bucket(Bucket=bucket_name)
    yield


@pytest.fixture
def send_language_json(aws_credentials, s3_resource, bucket_name, s3_test):
    language_params = {
        "Languages": {
            "EN": {
                "spacy": "en_core_web_sm",
                "nltk": "english",
                "not_found_answer": (
                    "Sorry, I'm still learning. Can you rephrase your question?"
                ),
                "language": "EN",
                "part_of_speech": ["NOUN", "PROPN"],
            },
            "IT": {
                "spacy": "it_core_news_sm",
                "nltk": "italian",
                "not_found_answer": "Testo non trovato nel PDF.",
                "language": "IT",
                "part_of_speech": ["NOUN", "PROPN"],
            },
            "PT": {
                "spacy": "pt_core_news_sm",
                "nltk": "portuguese",
                "not_found_answer": (
                    "Desculpe, Eu ainda estou aprendendo. Você pode reformular sua"
                    " questão?"
                ),
                "language": "PT",
                "part_of_speech": ["NOUN", "PROPN"],
            },
            "Default": {"language": "PT"},
        }
    }
    file_utils.send_file(
        json.dumps(language_params), filename="language_params.json", path="config"
    )
