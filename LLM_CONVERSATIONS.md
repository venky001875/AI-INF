# 🧠 LLM Conversations & Development Log

> Important prompts, engineering decisions, debugging conversations, and AI development iterations used to build the AI Influencer Research Agent.

## 📑 Contents

- Project Planning
- AI Research Prompt
- Web Search Strategy
- Structured Data Extraction
- Groq Integration
- JSON Parsing & Validation
- Influencer Data Normalization
- Follower Count Handling
- Streamlit Development
- SQLite CRM
- Debugging & Problem Solving
- Testing
- Final Engineering Decisions

## Project Planning

### Purpose
Define a minimal but useful MVP for a Python-based influencer research assistant that combines web search, LLM extraction, Streamlit presentation, and SQLite storage.

> **Prompt**

```text
Create a workflow that searches for category-specific influencers in a target location, filters by platform, extracts relevant profile data, and presents it in a Streamlit app.
```

- Problem encountered: The project needed a simple architecture that was maintainable while still supporting real-world search and extraction tasks.
- Solution/decision: Keep the app modular by separating search, LLM extraction, validation, UI rendering, and CRM storage.

## AI Research Prompt

### Purpose
Turn search results into a concise list of relevant individual creators that match the requested category, platform, and location.

> **Prompt**

```text
Find relevant individual creators and people based on the category, location, and platform described in the web search results. Return only real people, not companies or organizations.
```

- Problem encountered: The model could overgenerate or return matches that were not clearly relevant to the topic.
- Solution/decision: Restrict the prompt to relevant individuals only and prefer fewer accurate results over invented suggestions.

## Web Search Strategy

### Purpose
Improve search quality so social media handles and creator pages are easier to find from search results.

> **Prompt**

```text
Use search queries such as: "{category} {location} influencer Instagram", "{category} {location} creator YouTube", and site-specific searches like site:instagram.com and site:youtube.com.
```

- Problem encountered: Broad searches often returned generic or noisy results, making extraction harder.
- Solution/decision: Use targeted queries with platform and location emphasis while keeping the existing search flow intact.

## Structured Data Extraction

### Purpose
Force the LLM to return a predictable JSON structure for influencer data.

> **Prompt**

```text
Return only valid JSON with influencers as a list. Include fields such as name, platform, username, followers, category, location, profile_url, email, description, match_reason, and source_url.
```

- Problem encountered: The model sometimes returned partial, malformed, or markdown-wrapped results.
- Solution/decision: Standardize the schema and validate each record before accepting it.

## Groq Integration

### Purpose
Connect the application to Groq with LangChain and keep response handling consistent.

> **Prompt**

```text
Use Groq for structured influencer extraction with temperature 0 and clear JSON-only output requirements.
```

- Problem encountered: Groq occasionally returned empty output, markdown code fences, or unexpected non-JSON content.
- Solution/decision: Add a robust parser that extracts usable JSON from text and handles common response variations safely.

## JSON Parsing & Validation

### Purpose
Extract usable JSON from model output and reject invalid or incomplete records.

> **Prompt**

```text
Parse the response even if it is wrapped in markdown, and validate that it contains an influencers list before using it.
```

- Problem encountered: The app previously failed when the model returned mixed text or irrelevant content before the JSON object.
- Solution/decision: Parse the first valid JSON object found in the response and validate the schema before accepting the data.

## Influencer Data Normalization

### Purpose
Recover usable influencer records when the real name is missing but a valid username exists.

> **Prompt**

```text
If name is unavailable but username exists, use the username as the name. If username exists and profile_url is missing, generate a platform-specific profile link.
```

- Problem encountered: Records were discarded when `name` was null, even when a valid handle was available.
- Solution/decision: Normalize records before validation and generate Instagram or YouTube profile URLs when appropriate.

## Follower Count Handling

### Purpose
Avoid fake or invented engagement data.

> **Prompt**

```text
Only use follower counts when they are explicitly shown in the search results. Never invent follower totals.
```

- Problem encountered: The model sometimes guessed follower counts or returned numeric values that were not in the expected string schema.
- Solution/decision: Treat followers as optional and preserve them only when explicitly available, while safely normalizing numeric values without inventing missing counts.

## Streamlit Development

### Purpose
Display influencer results in a clean, readable, and user-friendly interface.

> **Prompt**

```text
Display user-friendly fields, show missing values as "Not available", and make profile links clickable.
```

- Problem encountered: The UI could show raw missing values and did not clearly explain why a profile matched the search.
- Solution/decision: Add consistent display formatting, a `match_reason` section, clickable links, and modern Streamlit width styling.

## SQLite CRM

### Purpose
Keep influencer records persistently stored after research.

> **Prompt**

```text
Store the core identity, platform, username, followers, category, location, profile_url, email, and description in the CRM without breaking the existing database design.
```

- Problem encountered: CRM storage had to remain simple and stable while still accepting incomplete fields.
- Solution/decision: Keep the existing SQLite schema and insert only the supported core fields, leaving the design unchanged unless a future enhancement requires it.

## Debugging & Problem Solving

### Purpose
Diagnose failure modes such as empty or malformed model output and inconsistent influencer records.

> **Prompt**

```text
Why did Groq return an empty response or non-JSON text on some searches? How can we produce a cleaner and more reliable extraction path?
```

- Problem encountered: Empty responses caused the app to fail even when the rest of the pipeline was functional.
- Solution/decision: Add explicit validation, clear error handling, better prompt instructions, and safer parsing for empty content.

## Testing

### Purpose
Validate the core logic and confirm the system works for realistic search scenarios.

> **Prompt**

```text
Test the parser with markdown JSON, missing names, username-only records, and empty response cases. Then validate a live search for Cricket in India on Instagram.
```

- Problem encountered: The model was sometimes too permissive in edge cases and too strict in others, especially around required fields.
- Solution/decision: Add regression tests for empty responses, JSON parsing, and username fallback behavior; refine prompt wording and search queries using live results.

## Final Engineering Decisions

### Purpose
Document the final practical decisions that kept the project reliable and simple.

> **Prompt**

```text
Keep the architecture simple, maintain the working flow, ensure the model never invents data, and preserve user-facing clarity across search, validation, UI, and CRM.
```

- Problem encountered: The project needed to balance AI flexibility with disciplined validation and minimal complexity.
- Solution/decision: Use a small, maintainable pipeline that validates each record, keeps missing data explicit, and avoids fabricating names, usernames, or follower counts.

---

This document intentionally avoids API keys, secrets, or personal data and focuses on the prompts and decisions that shaped the AI Influencer Research Agent.
