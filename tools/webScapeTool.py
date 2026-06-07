from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from rich import print



@tool
def scrape_website(url: str) -> str:
    """Scrape the main text content from a webpage."""
    try:
        response = requests.get(url, timeout=10,headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"})

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)[:5000]

        return text

    except Exception as e:
        return f"Error scraping website: {str(e)}"


