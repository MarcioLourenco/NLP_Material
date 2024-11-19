from utils.gpt_utils import execute_query
from utils.personas import get_gpt_role_trait, get_gpt_role_answer_type


def generate_answer(
    question: str, topics: list, topn_chunks: list, language_param: dict, role: str
) -> str:
    role_trait = get_gpt_role_trait(role=role, prefix="Act as")
    role_answer_type = get_gpt_role_answer_type(role)
    key_phrases_str = ", ".join(topics)
    prompt = ""
    prompt += "search results:\n\n"
    for chunk in topn_chunks:
        prompt += chunk + "\n\n"

    not_found_answer = language_param["not_found_answer"]
    prompt += (
        "Instructions: Compose a comprehensive reply to the query using the search"
        " results given. If the search results mention multiple subjects.with the same"
        " name, create separate answers for each. Only include information found in"
        " the results and don't add any additional information. Make sure the answer"
        " is correct and don't output false content. If the text does not relate to"
        f" the query, simply state '{not_found_answer}'. Ignore outlier search results"
        " which has nothing to do with the question. Only answer what is asked. The"
        f" question topics are: {key_phrases_str}\n\n\nQuery: {{question}}\nAnswer:"
        f" {role_trait} {role_answer_type}"
    )

    prompt += f"Query: {question}\nAnswer:"

    return execute_query(prompt=prompt, engine="text-davinci-003")


def generate_synonyms(topics: list, language_param: dict, role: str) -> dict:
    key_phrases_str = "', '".join(topics)
    role_trait = get_gpt_role_trait(role=role)
    prompt = (
        f"Instructions: Give me the synonyms for the list of topics '{key_phrases_str}'"
        f" in the context of {role_trait} Answer in {language_param.get('nltk')}"
    )
    response = execute_query(prompt=prompt, engine="text-davinci-003")
    synonyms = list(filter(None, response.split("\n")))
    synonyms_dict = dict()
    for synonym in synonyms:
        split_synonym = synonym.split(":")
        synonyms_dict.update(
            {split_synonym[0]: list(map(str.strip, split_synonym[1].split(",")))}
        )

    return synonyms_dict
