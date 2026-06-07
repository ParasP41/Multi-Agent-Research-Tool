from langchain.tools import tool
from tavily import TavilyClient
import os
from dotenv import load_dotenv
load_dotenv()
from rich import print

TavilyClient = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)   
@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic . Returns Titles , URLs and snippets."""
    response = TavilyClient.search(
    query=query,
    max_results=5,
    )

    out=[]

    for result in response['results']:
        out.append(f"Title: {result['title']}\nURL: {result['url']}\nSnippet: {result['content'][:300]}\n")

    return "\n-----\n".join(out)



