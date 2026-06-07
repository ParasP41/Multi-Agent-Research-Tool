from langchain.tools import tool
from tavily import TavilyClient
import os
import time
import requests
from dotenv import load_dotenv
load_dotenv()
from rich import print

tavily_client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)   
@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic . Returns Titles , URLs and snippets."""
    response = None
    last_error = None

    for attempt in range(3):
        try:
            response = tavily_client.search(
                query=query,
                max_results=5,
            )
            break
        except requests.exceptions.RequestException as e:
            last_error = e
            if attempt < 2:
                time.sleep(1 + attempt)
        except Exception as e:
            last_error = e
            break

    if response is None:
        return (
            "Search failed because the remote search service closed the connection. "
            f"Please try again in a moment. Details: {last_error}"
        )

    out = []

    if response.get("answer"):
        out.append(f"Overview:\n{response['answer']}\n")

    for result in response.get("results", []):
        out.append(
            f"Title: {result.get('title', 'Untitled')}\n"
            f"URL: {result.get('url', 'No URL')}\n"
            f"Snippet: {result.get('content', '')[:3000]}\n"
        )

    if not out:
        return "Search completed, but no results were returned. Try a more specific topic."

    return "\n-----\n".join(out)



