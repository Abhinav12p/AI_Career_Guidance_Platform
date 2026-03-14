from __future__ import annotations

from typing import List, Optional


def _lazy_client(api_key: str):
    from google import genai
    return genai.Client(api_key=api_key)


def generate_text(api_key: str, prompt: str, model: str = "gemini-2.5-flash") -> str:
    client = _lazy_client(api_key)
    response = client.models.generate_content(model=model, contents=prompt)
    text = getattr(response, "text", None)
    if text:
        return text.strip()

    candidates = getattr(response, "candidates", None) or []
    parts: List[str] = []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        if not content:
            continue
        for part in getattr(content, "parts", []) or []:
            if getattr(part, "text", None):
                parts.append(part.text)
    return "\n".join(parts).strip() if parts else "No response returned by Gemini."


def build_roadmap_prompt(career: str, profile_summary: str, hint: str) -> str:
    return f"""
You are a career roadmap expert.
Create a practical roadmap for becoming a {career}.
Use the user profile below.

User profile:
{profile_summary}

Guidance hint:
{hint}

Return:
1. 30 day plan
2. 60 day plan
3. 90 day plan
4. 6 month plan
5. Key projects to build
6. Free learning sources
7. Skill gaps to close first

Keep the answer structured, simple, and useful for a final year student.
""".strip()


def build_insights_prompt(career: str, profile_summary: str, tools: list[str], certifications: list[str]) -> str:
    return f"""
You are a career analyst.
Explain the career path: {career}.

User profile:
{profile_summary}

Known tools for this path:
{', '.join(tools)}

Known certifications:
{', '.join(certifications)}

Return sections:
1. What this role does
2. Day to day work
3. Tools and technologies
4. Hiring expectations
5. Certifications that matter
6. Salary and growth factors in general terms
7. Portfolio ideas
8. Common mistakes beginners make

Write in simple English. Use headings.
""".strip()


def build_chat_prompt(career: str, profile_summary: str, chat_history: List[dict], user_question: str) -> str:
    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in chat_history[-8:]])
    return f"""
You are a helpful career chat assistant.
Selected career: {career}
User profile: {profile_summary}
Recent chat:
{history_text}

Answer the latest user question clearly and practically.
Question: {user_question}
""".strip()
