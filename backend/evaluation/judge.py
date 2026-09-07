import json

from langchain_google_genai import (
    ChatGoogleGenerativeAI
)

from app.config import (
    GOOGLE_API_KEY,
    LLM_MODEL,
)


judge_llm = ChatGoogleGenerativeAI(
    model=LLM_MODEL,
    temperature=0,
    google_api_key=GOOGLE_API_KEY,
)


JUDGE_PROMPT = """
You are evaluating an internal company RAG system.

Evaluate whether the actual answer correctly answers
the question compared with the expected answer.

Question:
{question}

Expected Answer:
{expected_answer}

Actual Answer:
{actual_answer}

Return ONLY valid JSON using this format:

{{
    "correct": true,
    "score": 1.0,
    "reason": "short explanation"
}}

Rules:

- score must be between 0.0 and 1.0
- correct should be true only if the actual answer
  is semantically consistent with the expected answer
- if expected answer is "Not found", the actual answer
  should clearly state that the information is unavailable
- do not reward answers that contradict the expected answer
"""


def judge_answer(
    question: str,
    expected_answer: str,
    actual_answer: str,
) -> dict:

    prompt = JUDGE_PROMPT.format(
        question=question,
        expected_answer=expected_answer,
        actual_answer=actual_answer,
    )

    response = judge_llm.invoke(prompt)

    content = response.content

    if isinstance(content, list):
        content = "".join(
            item.get("text", "")
            for item in content
            if isinstance(item, dict)
        )

    content = content.strip()

    # Remove markdown code fence if Gemini adds it

    if content.startswith("```json"):
        content = content[7:]

    elif content.startswith("```"):
        content = content[3:]

    if content.endswith("```"):
        content = content[:-3]

    content = content.strip()

    return json.loads(content)