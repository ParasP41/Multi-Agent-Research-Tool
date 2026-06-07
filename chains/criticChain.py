from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import init_chat_model

model = init_chat_model(
            # "openrouter:google/gemma-3-27b-it",
            "openrouter:openai/gpt-4o-mini",
            # "openrouter:openai/gpt-oss-120b",
            # "groq:llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=3000
        )


#critic_chain 

critic_prompt = ChatPromptTemplate.from_messages([
    ("system",
"""
You are a senior research reviewer.

Evaluate reports for:
- Accuracy
- Completeness
- Structure
- Clarity
- Source usage
- Depth of analysis

Be strict but constructive.
"""
),
    ("human",
"""
Review the report below.

Report:
{report}

Evaluate:

1. Research Quality (0-10)
2. Clarity (0-10)
3. Structure (0-10)
4. Depth of Analysis (0-10)
5. Source Usage (0-10)

Then provide:

Strengths:
- ...

Weaknesses:
- ...

Missing Information:
- ...

Specific Improvements:
- ...

Final Score: X/10

Verdict:
...
"""
)
])

critic_chain = critic_prompt | model | StrOutputParser()