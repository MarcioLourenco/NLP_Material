from src.capcobot_question_manager.utils import personas


def test_get_gpt_executive_role_trait():
    expected_prompt = "Act as a experienced experienced professional in strategic"
    returned_prompt = personas.get_gpt_role_trait(role="Executive", prefix="Act as")
    assert returned_prompt.startswith(expected_prompt)


def test_get_gpt_engineer_role_trait():
    expected_prompt = "Act as an engineer that is working as a compliance"
    returned_prompt = personas.get_gpt_role_trait(role="Engineer", prefix="Act as ")
    assert returned_prompt.startswith(expected_prompt)


def test_get_gpt_administrative_assistant_role_trait():
    expected_prompt = "a 25 years old female analyst, focusing on learning as much as"
    returned_prompt = personas.get_gpt_role_trait(role="AdministrativeAssistant")
    assert returned_prompt.startswith(expected_prompt)


def test_get_gpt_default_role_trait():
    expected_prompt = "Act as an employee of a relevant bank, working in"
    returned_prompt = personas.get_gpt_role_trait("Default", "Act as")
    assert returned_prompt.startswith(expected_prompt)


def test_get_gpt_nonexistent_role_trait():
    expected_prompt = personas.get_gpt_role_trait("Default")
    returned_prompt = personas.get_gpt_role_trait("nonexistent")
    assert expected_prompt == returned_prompt


def test_get_gpt_executive_role_answer_type():
    expected_prompt = "The answer must be clear, objective, with a summarized text that"
    returned_prompt = personas.get_gpt_role_answer_type("Executive")
    assert returned_prompt.startswith(expected_prompt)


def test_get_gpt_engineer_role_answer_type():
    expected_prompt = "The answer should contain details on the subject, technical data"
    returned_prompt = personas.get_gpt_role_answer_type("Engineer")
    assert returned_prompt.startswith(expected_prompt)


def test_get_gpt_administrative_assistant_role_answer_type():
    expected_prompt = "The answer must be simple and objective to facilitate the tasks."
    returned_prompt = personas.get_gpt_role_answer_type("AdministrativeAssistant")
    assert returned_prompt.startswith(expected_prompt)


def test_get_gpt_default_role_answer_type():
    expected_prompt = "The answer must be short and concise, but no important"
    returned_prompt = personas.get_gpt_role_answer_type("Default")
    assert returned_prompt.startswith(expected_prompt)


def test_get_gpt_nonexistent_role_answer_type():
    expected_prompt = personas.get_gpt_role_answer_type("Default")
    returned_prompt = personas.get_gpt_role_answer_type("nonexistent")
    assert expected_prompt == returned_prompt
