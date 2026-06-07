from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import init_chat_model



model = init_chat_model(
            # "openrouter:google/gemma-3-27b-it",
            "openrouter:openai/gpt-4o-mini",
            # "openrouter:openai/gpt-oss-120b",
            # "groq:llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=1000
        )

planner_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are an expert research planner.

Generate only 5 search queries that will help create a complete research report.

The queries should collectively cover:

- Definition and overview
- Core concepts
- How it works
- Applications and use cases
- Technical implementation
- Challenges and limitations
- Recent developments and trends
- Future outlook

Rules:

- Generate one query per line.
- Do not add years to every query.
- Only use words such as latest, recent, current trends, or a year when searching for developments or news.
- Keep foundational queries timeless.
- Output only the search queries.
        """
    ),
    (
        "human",
        """
        Topic:
        {topic}
        """
    )
])

planner_chain = planner_prompt | model | StrOutputParser()
