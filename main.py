import json
import re
from typing import Optional

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel

from tools import search_tool, wiki_tool, save_tool

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_tokens=4096,
    reasoning_effort="low"
)


# ==============================
# Data Model
# ==============================

class Influencer(BaseModel):
    name: Optional[str] = None
    platform: Optional[str] = None
    username: Optional[str] = None
    followers: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    profile_url: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    match_reason: Optional[str] = None
    source_url: Optional[str] = None


def _normalize_influencer(person, category, location, platform):
    if not isinstance(person, dict):
        return None

    person = dict(person)

    if not person.get("name"):
        person["name"] = person.get("username")

    name = str(person.get("name") or "").strip()
    username = str(person.get("username") or "").strip()

    if not name:
        return None

    person["name"] = name
    person["username"] = username or None

    followers = person.get("followers")
    if followers is not None:
        if isinstance(followers, bool):
            person["followers"] = None
        elif isinstance(followers, (int, float)):
            person["followers"] = str(int(followers)) if float(followers).is_integer() else str(followers)
        else:
            person["followers"] = str(followers).strip() or None

    if person.get("followers") is not None and not str(person.get("followers")).strip():
        person["followers"] = None

    if not person.get("profile_url") and person.get("username"):
        username = str(person["username"]).lstrip("@").strip()
        platform_name = str(person.get("platform") or platform or "").strip()

        if platform_name.lower() == "instagram":
            person["profile_url"] = f"https://www.instagram.com/{username}/"
        elif platform_name.lower() == "youtube":
            person["profile_url"] = f"https://www.youtube.com/@{username}"

    if not person.get("match_reason"):
        person["match_reason"] = (
            f"{location} {category} creator relevant to {platform} on "
            f"{person.get('platform') or platform}."
        )

    return person


def _parse_ai_response(response):
    content = getattr(response, "content", response)

    if isinstance(content, list):
        content = "\n".join(
            block.get("text", "")
            if isinstance(block, dict) and isinstance(block.get("text"), str)
            else str(block)
            for block in content
        )

    if isinstance(content, dict):
        return content

    if not isinstance(content, str):
        if content is None:
            raise ValueError("Groq returned an empty response.")
        content = str(content)

    text = content.strip()
    if not text:
        raise ValueError("Groq returned an empty response.")

    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text, flags=re.IGNORECASE | re.DOTALL)

    decoder = json.JSONDecoder()

    for start, character in enumerate(text):
        if character != "{":
            continue

        try:
            data, _ = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            continue

        if isinstance(data, dict):
            return data

    raise ValueError("Groq response did not contain valid JSON.")


# ==============================
# Influencer Search
# ==============================

def influencer_search(category, location, platform, number):
    try:
        limit = max(0, int(number))
    except (TypeError, ValueError):
        limit = 0

    queries = [
        f'"{category}" "{location}" influencer Instagram',
        f'"{category}" "{location}" creator Instagram',
        f'"{category}" "{location}" creator YouTube',
        f'"{category}" influencer "{location}"',
        f'"{category}" creator "{location}"',
        f'site:instagram.com "{category}" "{location}"',
        f'site:youtube.com "{category}" "{location}"',
        f'site:linkedin.com/in "{category}" "{location}"'
    ]

    results = []

    for query in queries:
        try:
            data = search_tool.invoke(query)

            if data is not None:
                if isinstance(data, (dict, list)):
                    data = json.dumps(data, ensure_ascii=False)
                results.append(str(data))

        except Exception as e:
            print("Search error:", e)

    if not results:
        return json.dumps({"influencers": []})

    web_data = "\n\n".join(results)
    print(f"Search results combined: {len(web_data)} characters")

    prompt = f"""
You are an influencer research assistant.

Find up to {number} relevant individual creators/people from the search results.

Category: {category}
Location: {location}
Platform: {platform}

SEARCH RESULTS:
{web_data}

Instructions:
- Extract the real person's name when available.
- Extract the social media username/handle when available.
- Extract the profile URL when available.
- Extract follower count ONLY when explicitly shown in the search results.
- If name is unavailable but username exists, return the username as the name.
- Never invent names.
- Never invent usernames.
- Never invent follower counts.
- Return only relevant individual influencers/creators.
- Do not return companies or organizations.
- Return fewer results rather than inventing information.
- Set any missing value to null.
- Include a brief match_reason explaining why this person matches the requested category, location, and platform.

Return ONLY valid JSON.
No markdown.
No explanation.

Example:
{{
  "influencers": [
    {{
      "name": "Person Name",
      "platform": "Instagram",
      "username": "username",
      "followers": null,
      "category": "{category}",
      "location": "{location}",
      "profile_url": "https://www.instagram.com/username/",
      "email": null,
      "description": "Creator related to {category}",
      "match_reason": "{location} {category} creator sharing relevant content on Instagram.",
      "source_url": null
    }}
  ]
}}
"""


    try:
        response = llm.invoke(prompt)
        print("Groq raw content:", repr(getattr(response, "content", None))[:2000])
        print(
            "Groq finish reason:",
            getattr(response, "response_metadata", {}).get("finish_reason"),
        )

        data = _parse_ai_response(response)
        if not isinstance(data.get("influencers"), list):
            raise ValueError("Groq JSON must contain an influencers list.")

        valid = []

        for person in data.get("influencers", []):
            normalized = _normalize_influencer(person, category, location, platform)

            if normalized is None:
                print("Skipping influencer: name and username are missing.")
                continue

            try:
                valid.append(Influencer(**normalized).model_dump())
            except Exception as e:
                print("Skipping invalid influencer:", e)

        return json.dumps(
            {"influencers": valid[:limit]},
            indent=2
        )

    except Exception as e:

        print("AI extraction error:", e)

        return json.dumps({
            "error": "Could not extract valid influencer results.",
            "message": str(e) or "Groq returned an unexpected response."
        })