import logging
from io import StringIO

import numpy as np
import pandas as pd
from sklearn.metrics import pairwise_distances

from src.capcobot_question_manager.utils.file_utils import (
    get_file_from_s3,
)
from src.capcobot_question_manager import get_config

logger = logging.getLogger("CapcoBot")

SIMILARITY_QUESTION_DOCUMENT = 0.02

WORKDIR = get_config().WORKDIR
DATA_FOLDER = get_config().DATA_FOLDER
DATA_PATH = f"{WORKDIR}{DATA_FOLDER}"


def calculate_distance_matrix(c_matrix, metric):
    dist_matrix = pairwise_distances(np.array(c_matrix), metric=metric)
    result = pd.DataFrame(dist_matrix, index=c_matrix.index, columns=c_matrix.index)
    return result


def counter_matrix_recalculate(language: str, external_topic_list: list):
    try:
        file_content_from_s3 = get_file_from_s3(
            "counter_matrix_docs.csv", f"{DATA_PATH}/{language}"
        )
        file_content_from_s3 = file_content_from_s3.read().decode("utf-8")
    except Exception as e:
        logger.error('Não foi possível processar o arquivo "counter_matrix_docs.csv"')
        logger.error("Detalhes do erro: " + str(e))
        raise e
    counter_matrix_docs = pd.read_csv(StringIO(file_content_from_s3), sep=";")
    doc_dimensions = counter_matrix_docs.columns.to_list()[1:]
    external_counter = ["Question"]

    for doc_topic in doc_dimensions:
        if doc_topic in external_topic_list:
            external_counter.append(1)
        else:
            external_counter.append(0)

    counter_matrix_docs.loc[len(counter_matrix_docs.index)] = external_counter
    counter_matrix_docs.index = counter_matrix_docs.iloc[:, 0]

    return counter_matrix_docs.iloc[:, 1:]


def doc_selection_based_on_distance_matrix(dist_matrix: pd.DataFrame):
    filtered_matrix = dist_matrix.loc["Question"] < 1 - SIMILARITY_QUESTION_DOCUMENT
    selected_docs = filtered_matrix.drop("Question").reindex()
    selected_doc_names = []

    for i in range(0, len(selected_docs)):
        if selected_docs[i]:
            doc_json_name = selected_docs.index[i].replace("csv", "json")
            selected_doc_names.append(doc_json_name)

    return selected_doc_names
