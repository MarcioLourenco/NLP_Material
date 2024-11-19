from src.capcobot_question_manager.utils import language_utils
import pytest


@pytest.fixture
def bucket_name(app):
    return app.BUCKET


@pytest.fixture
def s3_test(s3_client, bucket_name):
    s3_client.create_bucket(Bucket=bucket_name)
    yield


def test_get_language_from_text_pt(send_language_json):
    send_language_json
    sample_text = (
        "E agora, José? A festa acabou, a luz apagou, o povo sumiu, a noite esfriou, e"
        " agora, José?"
    )
    expected_language = "PT"
    returned_language = language_utils.get_language_from_text(sample_text).get(
        "language"
    )
    assert expected_language == returned_language


def test_get_language_from_text_en(send_language_json):
    send_language_json
    sample_text = (
        "We shall defend our island whatever the cost may be; we shall fight on"
        " beaches, landing grounds, in fields, in streets and on the hills."
    )
    expected_language = "EN"
    returned_language = language_utils.get_language_from_text(sample_text).get(
        "language"
    )
    assert expected_language == returned_language


def test_get_language_from_text_de(send_language_json):
    send_language_json
    sample_text = (
        "Bleib' dir treu Niemals auseinandergeh'n Werden immer zueinandersteh'n Für"
        " immer"
    )
    expected_language = "PT"
    returned_language = language_utils.get_language_from_text(sample_text).get(
        "language"
    )
    assert expected_language == returned_language


def test_get_default_language(send_language_json):
    expected_language = {
        "spacy": "pt_core_news_sm",
        "nltk": "portuguese",
        "not_found_answer": (
            "Desculpe, Eu ainda estou aprendendo. Você pode reformular sua questão?"
        ),
        "language": "PT",
        "part_of_speech": ["NOUN", "PROPN"],
    }
    returned_language = language_utils.get_default_language()
    assert expected_language == returned_language
