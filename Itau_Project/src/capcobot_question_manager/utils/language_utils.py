import json
from io import StringIO

from langdetect import DetectorFactory, detect
from src.capcobot_question_manager.utils.file_utils import (
    get_file_from_s3,
)


def __get_language_params():
    language_params = (
        get_file_from_s3("language_params.json", "config").read().decode("utf-8")
    )
    return json.load(StringIO(language_params))


def filter_character(text: str, max_length: int = 100):
    # TODO: maybe cat just little words or implement regex to not get links
    text_split = text.split()[:max_length]
    str_filter = [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "0",
        "http",
        ":",
        "/",
        "°",
        "º",
    ]

    new_text = []
    for word in text_split:
        if not any([x in word for x in str_filter]):
            new_text.append(word)
    return " ".join(new_text).replace(".", "").replace("_", "").lower()


def get_language_from_text(text):
    DetectorFactory.seed = 0
    text_filtered = filter_character(text, 300)
    return get_language(detect(text_filtered))


def get_default_language():
    language_params = __get_language_params()
    return language_params["Languages"][
        language_params["Languages"]["Default"]["language"]
    ]


def get_language(language: str):
    language_params = __get_language_params()
    all_json_languages = list(language_params["Languages"])
    language = language.upper() if language else ""

    if language in all_json_languages:
        return language_params["Languages"][language]
    else:
        return get_default_language()


def get_available_languages():
    language_params = __get_language_params()
    all_json_languages = list(language_params["Languages"])
    return all_json_languages


if __name__ == "__main__":
    text = "Regolamento illustra e motiva le"
    language = get_language_from_text(text)
    print(language)
