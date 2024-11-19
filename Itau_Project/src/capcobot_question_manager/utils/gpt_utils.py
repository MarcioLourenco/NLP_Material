import os
import openai


OPENAI_KEY = os.environ.get("OPENAI_API_KEY")


def execute_query(prompt: str, engine: str = "text-davinci-003") -> str:
    openai.api_key = OPENAI_KEY
    completions = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        max_tokens=512,
        n=1,
        stop=None,
        temperature=0.1,
    )
    message = completions.choices[0].text
    return message
