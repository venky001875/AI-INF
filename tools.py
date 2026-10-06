from datetime import datetime

import requests

from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun




search = DuckDuckGoSearchRun()


@tool
def search_tool(query: str) -> str:
    """
    Search the internet for current information.
    """

    try:

        return search.run(query)

    except Exception as e:

        return f"Web search failed: {str(e)}"




@tool
def wiki_tool(query: str) -> str:
    """
    Search Wikipedia for general factual information.
    """

    try:

        search_url = (
            "https://en.wikipedia.org/w/rest.php/v1/search/page"
        )

        response = requests.get(
            search_url,
            params={
                "q": query,
                "limit": 2
            },
            headers={
                "User-Agent": "AI-Research-Agent/1.0"
            },
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        pages = data.get(
            "pages",
            []
        )

        if not pages:

            return (
                f"No Wikipedia results found for: {query}"
            )


        results = []


        for page in pages[:2]:

            title = page.get(
                "title",
                ""
            )


            summary_url = (
                "https://en.wikipedia.org/api/rest_v1/page/summary/"
                + requests.utils.quote(title)
            )


            summary_response = requests.get(
                summary_url,
                headers={
                    "User-Agent": "AI-Research-Agent/1.0"
                },
                timeout=10
            )


            if summary_response.status_code != 200:

                continue


            summary_data = (
                summary_response.json()
            )


            extract = summary_data.get(
                "extract",
                "No summary available."
            )


            results.append(
                f"Title: {title}\n"
                f"Summary: {extract}"
            )


        if not results:

            return (
                "Wikipedia found pages, but summaries "
                f"were unavailable for: {query}"
            )


        return "\n\n".join(
            results
        )


    except requests.exceptions.RequestException as e:

        return (
            f"Wikipedia request failed: {str(e)}"
        )


    except ValueError:

        return (
            "Wikipedia returned an invalid response."
        )


    except Exception as e:

        return (
            f"Wikipedia search failed: {str(e)}"
        )



@tool
def save_tool(data: str) -> str:
    """
    Save research data to research_output.txt.
    """

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    formatted_text = (
        "--- Research Output ---\n"
        f"Timestamp: {timestamp}\n\n"
        f"{data}\n\n"
    )


    with open(
        "research_output.txt",
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            formatted_text
        )


    return (
        "Data successfully saved to research_output.txt"
    )