from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from agents.searchAgent import search_Agent
from agents.readerAgent import reader_Agent

from chains.writerChain import writer_chain
from chains.criticChain import critic_chain
from chains.plannerChain import planner_chain
from chains.factCheckerChain import fact_checker_chain


class ResearchState(TypedDict):
    topic: str
    search_queries: str
    search_results: str
    scraped_content: str
    report: str
    fact_check: str
    feedback: str
    revision_count: int

def planner_node(state: ResearchState):

    queries = planner_chain.invoke({
        "topic": state["topic"]
    })

    print("\n=== SEARCH PLAN ===")
    print(queries)

    return {
        "search_queries": queries
    }

def search_node(state: ResearchState):

    agent = search_Agent()

    combined_results = []

    queries = list(
    dict.fromkeys(
        q.strip()
        for q in state["search_queries"].split("\n")
        if q.strip()
    )
)

    for query in queries:
        query = query.strip()
        if not query:
            continue

        result = agent.invoke({
            "messages": [
                (
                    "user",
                    f"Find recent, reliable and detailed information about: {query}"
                )
            ]
        })

        combined_results.append(
            result["messages"][-1].content
        )

    return {
        "search_results": "\n\n".join(combined_results)
    }

def reader_node(state: ResearchState):

    agent = reader_Agent()

    result = agent.invoke({
        "messages": [
            (
                "user",
                f"""
Based on the search results about '{state['topic']}',

Select the 3 most relevant URLs.

Use the scrape_website tool to scrape EACH selected URL.

After scraping all selected URLs:

1. Combine the information.
2. Remove duplicate information.
3. Create a detailed research summary.
4. Mention which sources were used.

Search Results:

{state['search_results']}
"""
            )
        ]
    })

    return {
        "scraped_content": result["messages"][-1].content
    }

def writer_node(state: ResearchState):

    research_combined = f"""
    SEARCH RESULTS:
    {state['search_results']}

    SCRAPED CONTENT:
    {state['scraped_content']}
    """

    report = writer_chain.invoke({
        "topic": state["topic"],
        "research": research_combined,
        "feedback": state.get("feedback", "")
    })

    return {
        "report": report
    }

def fact_checker_node(state: ResearchState):

    research = f"""
    SEARCH RESULTS:
    {state['search_results']}

    SCRAPED CONTENT:
    {state['scraped_content']}
    """

    fact_check = fact_checker_chain.invoke({
        "research": research,
        "report": state["report"]
    })

    print("\n" + "=" * 50)
    print("FACT CHECK")
    print("=" * 50)
    print(fact_check)

    return {
        "fact_check": fact_check
    }

def critic_node(state: ResearchState):

    feedback = critic_chain.invoke({
    "report": f"""
REPORT:
{state['report']}

FACT CHECK:
{state['fact_check']}
"""
})

    print("\n" + "=" * 50)
    print("CRITIC FEEDBACK")
    print("=" * 50)
    print(feedback)

    return {
        "feedback": feedback,
        "revision_count": state.get("revision_count", 0) + 1
    }


def review_router(state: ResearchState):

    feedback = state["feedback"]

    try:
        score_line = feedback.split("Score:")[1]
        score = int(score_line.split("/")[0].strip())
    except Exception:
        score = 5

    print("\n" + "=" * 50)
    print(f"Current Score: {score}")
    print(f"Revision Count: {state['revision_count']}")
    print("=" * 50)

    if score >= 8:
        print("Report Approved")
        return "end"

    if state["revision_count"] >= 2:
        print("Maximum Revisions Reached")
        return "end"

    print("Rewriting Report...")
    return "rewrite"


graph_builder = StateGraph(ResearchState)

graph_builder.add_node("planner", planner_node)
graph_builder.add_node("search", search_node)
graph_builder.add_node("reader", reader_node)
graph_builder.add_node("writer", writer_node)
graph_builder.add_node("fact_checker",fact_checker_node)
graph_builder.add_node("critic", critic_node)

graph_builder.add_edge(START, "planner")
graph_builder.add_edge("planner", "search")
graph_builder.add_edge("search", "reader")
graph_builder.add_edge("reader", "writer")
graph_builder.add_edge("writer", "fact_checker")
graph_builder.add_edge("fact_checker", "critic")

graph_builder.add_conditional_edges(
    "critic",
    review_router,
    {
        "rewrite": "writer",
        "end": END
    }
)

research_graph = graph_builder.compile()


if __name__ == "__main__":
    topic=input("Enter the prompt : ")
    result = research_graph.invoke({
        "topic":topic,
        "revision_count": 0
    })

    print("\n" + "=" * 50)
    print("FINAL REPORT")
    print("=" * 50)
    print(result["report"])

    print("\n" + "=" * 50)
    print("FINAL FEEDBACK")
    print("=" * 50)
    print(result["feedback"])