import json


def __get_roles():
    f = open("roles.json")
    roles_gpt = json.load(f)
    f.close()
    return roles_gpt


def get_gpt_role_trait(role: str, prefix: str = "") -> str:
    roles_gpt = __get_roles()

    prompt = prefix
    if prompt:
        prompt += "" if prompt[-1] == " " else " "
    prompt += roles_gpt.get(role, roles_gpt.get("Default")).get("trait")
    return prompt


def get_gpt_role_answer_type(role: str):
    roles_gpt = __get_roles()

    prompt = roles_gpt.get(role, roles_gpt.get("Default")).get("answer_type")
    return prompt
