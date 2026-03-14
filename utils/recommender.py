from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .careers import CAREER_PROFILES


@dataclass
class Recommendation:
    career: str
    score: float
    fit_label: str
    gaps: List[str]
    summary: str
    tools: List[str]
    certifications: List[str]
    roadmap_hint: str


SKILL_MAP = {
    "technical": "Technical Skills",
    "analytical": "Analytical Skills",
    "communication": "Communication Skills",
    "creative": "Creative Skills",
}


def _fit_label(score: float) -> str:
    if score >= 86:
        return "Excellent Fit"
    if score >= 74:
        return "Strong Fit"
    if score >= 62:
        return "Good Potential"
    return "Needs Skill Growth"


def recommend_careers(profile: Dict[str, object]) -> List[Recommendation]:
    education = str(profile.get("education", "Bachelor's Degree"))
    experience = str(profile.get("experience", "Student/No experience"))
    user_skills = {
        "technical": int(profile.get("technical", 5)),
        "analytical": int(profile.get("analytical", 5)),
        "communication": int(profile.get("communication", 5)),
        "creative": int(profile.get("creative", 5)),
    }

    results: List[Recommendation] = []
    for career, cfg in CAREER_PROFILES.items():
        target_skills = cfg["skills"]
        skill_total = 0.0
        gaps: List[str] = []
        for key, target in target_skills.items():
            diff = abs(user_skills[key] - target)
            component = max(0.0, 10.0 - diff) / 10.0
            skill_total += component * 20.0
            if user_skills[key] < target:
                gaps.append(f"Improve {SKILL_MAP[key]} from {user_skills[key]} to at least {target}")

        education_bonus = cfg["education_weight"].get(education, 2) * 2.5
        experience_bonus = cfg["experience_weight"].get(experience, 2) * 2.5
        score = min(100.0, round(skill_total + education_bonus + experience_bonus, 1))

        results.append(
            Recommendation(
                career=career,
                score=score,
                fit_label=_fit_label(score),
                gaps=gaps[:3],
                summary=str(cfg["summary"]),
                tools=list(cfg["tools"]),
                certifications=list(cfg["certifications"]),
                roadmap_hint=str(cfg["roadmap_hint"]),
            )
        )

    return sorted(results, key=lambda x: x.score, reverse=True)


def profile_snapshot(profile: Dict[str, object]) -> Dict[str, object]:
    return {
        "name": profile.get("name", ""),
        "education": profile.get("education", "Bachelor's Degree"),
        "experience": profile.get("experience", "Student/No experience"),
        "technical": int(profile.get("technical", 5)),
        "analytical": int(profile.get("analytical", 5)),
        "communication": int(profile.get("communication", 5)),
        "creative": int(profile.get("creative", 5)),
    }
