from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import init_chat_model

model = init_chat_model(
            # "openrouter:google/gemma-3-27b-it",
            "openrouter:openai/gpt-4o-mini",
            # "openrouter:openai/gpt-oss-120b",
            # "groq:llama-3.3-70b-versatile",
            temperature=0,
            max_tokens=4000
        )

fact_checker_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a professional fact checker.

Your job is to compare the report against the research material.

Identify:

- Unsupported claims
- Missing evidence
- Contradictions
- Potential hallucinations
- Inaccurate statements

Be specific and concise.
"""
    ),
    (
        "human",
        """
Research Material:
{research}

Generated Report:
{report}
"""
    )
])

fact_checker_chain = (
    fact_checker_prompt
    | model
    | StrOutputParser()
)