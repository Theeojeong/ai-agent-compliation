from langchain_core.tools import tool
from langgraph.types import Command
from firecrawl import FirecrawlApp, ScrapeOptions
import os
import re


@tool
def transfer_to_agent(agent_name: str):
    """
    주어진 에이전트로 전환합니다

    Args:
        agent_name: 전환할 에이전트의 이름, 다음 중 하나: 'teacher_agent', 'quiz_agent', 'feynman_agent'
    """
    return Command(
        goto=agent_name,
        graph=Command.PARENT,
        update={
            "current_agent": agent_name
        },
    )

@tool
def web_search_tool(query: str):
    """
    Web Search Tool.
    Args:
        query: str
            The query to search the web for.
    Returns
        A list of search results with the website content in Markdown format.
    """

    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

    response = app.search(
        query=query,
        limit=5,
        scrape_options=ScrapeOptions(
            formats=["markdown"]
        )
    )

    if not response.success:
        return "Error using tool."

    cleaned_chunks = []

    for result in response.data:

        title = result["title"]
        url = result["url"]
        markdown = result["markdown"]

        cleaned = re.sub(r"\\+|\n+", "", markdown).strip()
        cleaned = re.sub(r"\[[^\]]+\]\([^\)]+\)|https?://[^\s]+", "", cleaned)

        cleaned_result = {
            "title": title,
            "url": url,
            "markdown": cleaned,
        }

        cleaned_chunks.append(cleaned_result)

    return cleaned_chunks
