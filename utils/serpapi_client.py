from __future__ import annotations

from collections import Counter
from typing import Dict, List, Tuple

import requests

from .careers import COMMON_SKILLS

SEARCH_URL = "https://serpapi.com/search.json"


def fetch_job_market(api_key: str, career: str, location: str = "India") -> Dict[str, object]:
    params = {
        "engine": "google_jobs",
        "q": f"{career} jobs",
        "location": location,
        "hl": "en",
        "api_key": api_key,
    }
    response = requests.get(SEARCH_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    jobs = data.get("jobs_results", []) or []
    top_jobs = []
    skills_counter: Counter[str] = Counter()
    company_counter: Counter[str] = Counter()
    location_counter: Counter[str] = Counter()

    for job in jobs[:10]:
        title = job.get("title", "Unknown Role")
        company = job.get("company_name", "Unknown Company")
        job_location = job.get("location", "Unknown Location")
        description = job.get("description", "") or ""
        via = job.get("via", "")
        extensions = job.get("detected_extensions", {}) or {}
        salary = extensions.get("salary") or extensions.get("schedule_type") or "Not listed"

        company_counter[company] += 1
        location_counter[job_location] += 1
        normalized = description.lower()
        for skill in COMMON_SKILLS:
            if skill.lower() in normalized or skill.lower() in title.lower():
                skills_counter[skill] += 1

        top_jobs.append(
            {
                "title": title,
                "company": company,
                "location": job_location,
                "salary": salary,
                "via": via,
                "description": description[:450] + ("..." if len(description) > 450 else ""),
            }
        )

    return {
        "job_count": len(jobs),
        "top_jobs": top_jobs,
        "top_companies": company_counter.most_common(5),
        "top_locations": location_counter.most_common(5),
        "top_skills": skills_counter.most_common(8),
        "raw": data,
    }
