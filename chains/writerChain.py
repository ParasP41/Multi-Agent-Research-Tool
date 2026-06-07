from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import init_chat_model


model = init_chat_model(
            # "openrouter:google/gemma-3-27b-it",
            "openrouter:openai/gpt-4o-mini",
            # "openrouter:openai/gpt-oss-120b",
            # "groq:llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=4000
        )



#writer chain

writer_prompt = ChatPromptTemplate.from_messages([
    ("system",
"""
You are a senior research analyst.

Your job is to create comprehensive, factual, and well-structured research reports.

Use only the information provided in the research material.

Do not invent facts, statistics, URLs, or sources.

Clearly explain findings with sufficient detail and examples when available.
"""
),
    ("human",
"""
Create a professional research report.

Topic:
{topic}

Research Material:
{research}

Previous Critic Feedback:
{feedback}

If feedback is provided, improve the report according to the feedback.

Requirements:

1. Introduction
   - Explain the topic.
   - Explain why it matters.

2. Key Findings
   - At least 3 major findings.
   - Each finding should have its own heading.
   - Explain each finding in detail.

3. Insights and Trends
   - Mention notable patterns, developments, or observations.

4. Conclusion
   - Summarize the overall research.

5. Sources
   - List every URL that appears in the research material.

Rules:
- Use only the provided research.
- Do not make up information.
- Write professionally.
- Be detailed and analytical.
"""
)
])

writer_chain = writer_prompt | model | StrOutputParser()
