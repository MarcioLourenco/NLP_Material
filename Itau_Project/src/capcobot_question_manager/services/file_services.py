import logging


from src.capcobot_question_manager.services.topic_modeling_services import (
    calculate_distance_matrix,
    counter_matrix_recalculate,
    doc_selection_based_on_distance_matrix,
)

logger = logging.getLogger("CapcoBot")


def document_question(question_language, question_topics):
    question_counter_matrix = counter_matrix_recalculate(
        question_language, question_topics
    )
    question_distance_matrix = calculate_distance_matrix(
        question_counter_matrix, "cosine"
    )
    docs = doc_selection_based_on_distance_matrix(question_distance_matrix)

    logger.info(docs)
    return docs
