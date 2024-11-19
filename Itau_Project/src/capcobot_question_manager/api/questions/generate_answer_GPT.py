import json
import logging
import os

import pandas as pd
import requests

from src.capcobot_question_manager.utils.file_utils import (
    file_exists,
    get_file_from_s3,
    list_files_in_s3,
)
from src.capcobot_question_manager.utils.language_utils import get_language
from src.capcobot_question_manager.utils.semantic_search import (
    SemanticSearch,
)
from src.capcobot_question_manager import get_config
from src.capcobot_question_manager.api.questions.topic_modeling import (
    get_topics,
)
from src.capcobot_question_manager.services.file_services import (
    document_question,
)
from src.capcobot_question_manager.services.gpt_services import (
    generate_answer,
    generate_synonyms,
)

WORKDIR = get_config().WORKDIR
DATA_FOLDER = get_config().DATA_FOLDER
DATA_PATH = f"{WORKDIR}{DATA_FOLDER}"

logger = logging.getLogger("CapcoBot")


class GenerateAnswerGPT:
    def __init__(self) -> None:
        self.recommender = SemanticSearch()

    @staticmethod
    def rename_file(file: str, new_ext: str, old_ext: str = ""):
        pre, ext = os.path.splitext(file)
        new_ext = new_ext if new_ext[0] == "." else f".{new_ext}"
        old_ext = old_ext if old_ext[0] == "." else f".{old_ext}"
        if old_ext in ext:
            file = pre + new_ext
        return file

    def load_recommender(self, chunks=[]):
        self.recommender.fit(chunks)
        return "Corpus Loaded."

    def find_topics(self, topics, chunks):
        key_chunk = []
        for text in chunks:
            text = text.replace(",", "").replace(".", "").lower()
            for key in topics:
                key = key.replace(",", "").replace(".", "").lower()
                if key in text:
                    key_chunk.append([key, text])

        return key_chunk

    def remove_incomplete_sentence(self, text, splitter=".pdf]"):
        text_list = text.split(splitter)

        if text_list[-1] != "" and len(text) > 100:
            new_text = ""
            for chunk in text_list[:-1]:
                new_text = new_text + chunk + splitter
            return new_text
        else:
            return text

    def get_context(self, language):
        files = list_files_in_s3(path=DATA_PATH, language=language)
        context = ""
        for file in files:
            extension = file.split(".")[-1]
            if extension == "json":
                response_aws = get_file_from_s3(file, f"{DATA_PATH}/{language}")
                json_text = response_aws["Body"].read().decode()
                json_dict = json.loads(json_text)
                len_pages = len(json_dict["pages"])
                for page in range(len_pages):
                    if json_dict["pages"][page]["paragraphs"] is not None:
                        len_paragraphs = len(json_dict["pages"][page]["paragraphs"])
                    else:
                        continue
                    for paragraph in range(len_paragraphs):
                        text = json_dict["pages"][page]["paragraphs"][paragraph][
                            "paragraph text"
                        ]
                        context = context + " " + text
        return context

    # def intersection(self, list1, list2):
    #     lst3 = [value for value in list1 if value in list2]
    #     return lst3

    def get_chunk_topic(self, file, language, topic):
        response_aws = get_file_from_s3(file, f"{DATA_PATH}/{language}")
        json_text = response_aws.read().decode()
        json_dict = json.loads(json_text)

        df = pd.DataFrame.from_dict(json_dict)
        df_pages = pd.json_normalize(df["pages"])
        paragraphs_list = df_pages["paragraphs"]

        paragraphs_avaible = []
        for p in paragraphs_list:
            if p is not None:
                paragraphs_avaible.append(p)

        df_paragraphs = pd.json_normalize(pd.Series(paragraphs_avaible))
        n_paragraphs = len(df_paragraphs.columns)

        df_final = pd.DataFrame()
        for i in range(n_paragraphs):
            df_parag = (
                pd.json_normalize(df_paragraphs[i])
                .reset_index()
                .rename(columns={"index": "page"})
            )
            df_final = pd.concat([df_final, df_parag])

        df = df[["path", "author", "title", "total pages"]].drop_duplicates()
        df_pages = df_pages[["page", "total paragraphs"]].drop_duplicates()
        df_final = df_final[df_final["paragraph topics"].notna()]
        df_final = df_final.merge(df_pages, how="left", on=["page"])

        df_final["key"] = 0
        df["key"] = 0
        df_final = df_final.merge(df, how="outer", on="key")
        df_final = df_final.sort_values(by=["page", "paragraph number"])

        df = pd.DataFrame()
        for t in topic:
            df_topic = df_final[df_final["paragraph topics"].apply(lambda x: t in x)]
            df = pd.concat([df, df_topic])

        df["chunk"] = "[Document:" + df["path"] + "] " + df["paragraph text"]

        return list(df["chunk"])

    def find_documents(self, url, json_head):
        try:
            response = requests.post(
                url,
                json=json_head,
            )
            files_response = json.loads(response.content)
            logger.info("Consulta realizada com sucesso:")
            logger.info(str(files_response))
            return files_response
        except ValueError as e:
            logger.error("Error in request")
            files_response = []

            raise e

    def get_files_intersection(self, files, files_response):
        tmp_files = []
        for file in files:
            tmp_files.append(
                GenerateAnswerGPT.rename_file(file=file, new_ext="json", old_ext="pdf")
            )

        if tmp_files:
            files_intersection = set(tmp_files).intersection(set(files_response))
        else:
            files_intersection = set(files_response)
        return files_intersection

    def get_answer_by_file(
        self,
        files_intersection,
        language,
        topics,
        question,
        language_param,
        role,
    ):
        answer_file = {}

        if len(files_intersection) > 0:
            for file in files_intersection:
                tmp_file = GenerateAnswerGPT.rename_file(
                    file=file, new_ext="json", old_ext="pdf"
                )
                logger.info(f"get answer file: {file}")

                if not file_exists(tmp_file, DATA_PATH, language):
                    return "File not found"

                chunks_file = self.get_chunk_topic(tmp_file, language, topics)
                print(chunks_file)

                if topics is not None:
                    search_key_chunk = self.find_topics(topics, chunks_file)
                    if len(search_key_chunk) > 0:
                        self.load_recommender(chunks_file)

                        answer = generate_answer(
                            question=question,
                            topics=topics,
                            topn_chunks=self.recommender(question),
                            language_param=language_param,
                            role=role,
                        )

                        # answer = self.remove_incomplete_sentence(answer)
                        answer_file[file] = answer
                    else:
                        answer = language_param["not_found_answer"]
                        answer_file[file] = answer
                else:
                    answer = language_param["not_found_answer"]
                    answer_file[file] = answer
        else:
            logger.warning("Document list is empty.")
            return language_param["not_found_answer"]

        logger.info(question)
        logger.info(answer)
        return answer_file

    def get_final_answer(self, answer_file, language_param):
        if not answer_file or isinstance(answer_file, str):
            return language_param["not_found_answer"]

        answer_list = list(set(answer_file.values()))

        if (
            len(answer_list) == 1
            and answer_list[0].strip() == language_param["not_found_answer"]
        ) or answer_list is None:
            final_answer = language_param["not_found_answer"]
        else:
            final_answer = ""
            for k, v in answer_file.items():
                if v.strip() != language_param["not_found_answer"]:
                    ref = str(k).replace(".json", ".pdf")
                    final_answer += v
                    final_answer += f" [{ref}] "

        return final_answer

    def generate_answer_GPT(
        self, question: str, language: str, role: str, files: list
    ) -> str:
        language_param = get_language(language)
        # context = self.get_context(language)

        topics = get_topics(question, language_param)
        if topics is None:
            logger.error("Nenhum tópico enontrado para a questão")
            logger.error(str(question))
            return self.get_final_answer(None, language_param)
        # topics = get_synonyms_words(topics, context, language_param["nltk"])
        synonymous_topics = generate_synonyms(
            topics=topics, language_param=language_param, role=role
        )

        syn_topics = set()
        syn_topics = set().union(syn_topics, topics)

        for key in synonymous_topics.keys():
            syn_topics = set().union(syn_topics, synonymous_topics[key])

        syn_topics = list(syn_topics)
        syn_topics = list(map(str.lower, syn_topics))
        files_response = document_question(language, topics)

        if not isinstance(files_response, list):
            logger.error(f"erro ao processar tópicos: {str(files_response)}")
            return self.get_final_answer(None, language_param)
        
        files_intersection = self.get_files_intersection(files, files_response)

        answer_by_file = self.get_answer_by_file(
            files_intersection,
            language,
            topics,
            question,
            language_param,
            role,
        )

        final_answer = self.get_final_answer(answer_by_file, language_param)
        return final_answer
