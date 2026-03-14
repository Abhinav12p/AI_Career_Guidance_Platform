from __future__ import annotations

import os
from typing import Dict, List

import pandas as pd
import streamlit as st

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

CAREER_IMAGES = {
    "DevOps Engineer": BASE_DIR / "assets" / "DevOps.jpg",
    "Mobile Developer": BASE_DIR / "assets" / "Mobile Developer.jpg",
    "Cybersecurity Analyst": BASE_DIR / "assets" / "Cybersecurity Analyst.JPG",
    "AI/ML Engineer": BASE_DIR / "assets" / "AI MLEngineer.jpg",
    "Cloud Architecture": BASE_DIR / "assets" / "Cloud Architecture.jpg",
    "Data Scientist": BASE_DIR / "assets" / "Data Scientists.jpg",
}

from utils.recommender import profile_snapshot, recommend_careers
from utils.storage import add_history, read_history
from utils.gemini_client import (
    build_chat_prompt,
    build_insights_prompt,
    build_roadmap_prompt,
    generate_text,
)
from utils.serpapi_client import fetch_job_market

st.set_page_config(
    page_title="AI-Powered Career Guidance Platform",
    page_icon="🚀",
    layout="wide",
)

CUSTOM_CSS = """
<style>
    .stApp {
        background: linear-gradient(180deg, #09090f 0%, #0f172a 100%);
        color: #e5e7eb;
    }
    [data-testid="stSidebar"] {
        background: #12121a;
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    .hero-card {
        padding: 1.4rem 1.6rem;
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(139,92,246,0.15));
        border: 1px solid rgba(96,165,250,0.25);
        margin-bottom: 1rem;
    }
    .metric-card {
        padding: 1rem 1.2rem;
        border-radius: 16px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.06);
    }
    .career-card {
        padding: 1rem 1.1rem;
        border-radius: 16px;
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(99,102,241,0.35);
        min-height: 250px;
    }
    .subtle {
        color: #9ca3af;
        font-size: 0.95rem;
    }
    .section-card {
        padding: 1rem 1.2rem;
        border-radius: 16px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.07);
        margin-bottom: 0.8rem;
    }
    .chip {
        display: inline-block;
        padding: 0.25rem 0.55rem;
        border-radius: 999px;
        background: rgba(99,102,241,0.18);
        border: 1px solid rgba(99,102,241,0.3);
        margin: 0.2rem;
        font-size: 0.85rem;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def resolve_secret(*names: str) -> str:
    for name in names:
        try:
            value = st.secrets.get(name)
            if value:
                return str(value)
        except Exception:
            pass

        value = os.getenv(name)
        if value:
            return value

    return ""


def get_gemini_key() -> str:
    return resolve_secret("GEMINI_API_KEY", "AIzaSyB4cEFQQOPd69H7KiYiUjGRt7YKqFnvxoAy")


def get_serpapi_key() -> str:
    return resolve_secret("SERPAPI_KEY", "e78e00a6c2dbf1e646653742ad77216c4d66d36473dcc4a1d2d1769fcc01d3c3")


if "selected_career" not in st.session_state:
    st.session_state.selected_career = None
if "recommendations" not in st.session_state:
    st.session_state.recommendations = []
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "market_cache" not in st.session_state:
    st.session_state.market_cache = {}
if "roadmap_cache" not in st.session_state:
    st.session_state.roadmap_cache = {}
if "insights_cache" not in st.session_state:
    st.session_state.insights_cache = {}


def get_profile() -> Dict[str, object]:
    return {
        "name": st.session_state.get("name", ""),
        "education": st.session_state.get("education", "Bachelor's Degree"),
        "experience": st.session_state.get("experience", "Student/No experience"),
        "technical": st.session_state.get("technical", 6),
        "analytical": st.session_state.get("analytical", 6),
        "communication": st.session_state.get("communication", 6),
        "creative": st.session_state.get("creative", 5),
        "location": st.session_state.get("location", "India"),
    }


def profile_summary(profile: Dict[str, object]) -> str:
    return (
        f"Name: {profile.get('name') or 'Student'}\n"
        f"Education: {profile['education']}\n"
        f"Experience: {profile['experience']}\n"
        f"Location: {profile['location']}\n"
        f"Technical: {profile['technical']}/10\n"
        f"Analytical: {profile['analytical']}/10\n"
        f"Communication: {profile['communication']}/10\n"
        f"Creative: {profile['creative']}/10"
    )


def ensure_recommendations() -> List:
    recs = recommend_careers(get_profile())
    st.session_state.recommendations = recs
    return recs


gemini_key = get_gemini_key()
serpapi_key = get_serpapi_key()

with st.sidebar:
#     st.title("Configuration")

#     st.caption("API keys automatically load from secrets.toml or environment variables.")
#     if gemini_key:
#         st.success("Gemini API connected")
#     else:
#         st.warning("Gemini API not configured")

#     if serpapi_key:
#         st.success("SerpAPI connected")
#     else:
#         st.warning("SerpAPI not configured")

#     with st.expander("How to make this public without filling keys each time"):
#         st.code(
#             'GEMINI_API_KEY = "your_gemini_key_here"\nSERPAPI_KEY = "your_serpapi_key_here"',
#             language="toml",
#         )

    st.subheader("Your Profile")
    st.text_input("Name", key="name")
    st.text_input("Target Location", value="India", key="location")

    st.selectbox(
        "Education Level",
        ["High School", "Diploma", "Bachelor's Degree", "Master's Degree"],
        key="education",
    )

    st.selectbox(
        "Experience Level",
        ["Student/No experience", "Beginner", "Intermediate", "Advanced"],
        key="experience",
    )

    st.divider()
    st.subheader("Skills Assessment")
    st.slider("Technical Skills", 1, 10, 6, key="technical")
    st.slider("Analytical Skills", 1, 10, 6, key="analytical")
    st.slider("Communication Skills", 1, 10, 6, key="communication")
    st.slider("Creative Skills", 1, 10, 5, key="creative")


profile = get_profile()
recommendations = ensure_recommendations()

selected = st.session_state.selected_career or (
    recommendations[0].career if recommendations else None
)

if st.session_state.selected_career is None and recommendations:
    st.session_state.selected_career = recommendations[0].career
    selected = recommendations[0].career

selected_rec = next((r for r in recommendations if r.career == selected), None)

st.markdown(
    """
<div class="hero-card">
    <h1>🚀 AI-Powered Career Guidance Platform</h1>
    <p class="subtle">Discover careers, analyze live job markets, build a learning roadmap, and chat with an AI career assistant.</p>
    <p><span class="chip">Streamlit UI</span><span class="chip">Gemini Integration</span><span class="chip">SerpAPI Research</span><span class="chip">Career History</span></p>
</div>
""",
    unsafe_allow_html=True,
)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(
        f'<div class="metric-card"><h3>{selected or "-"}</h3><div class="subtle">Selected Career</div></div>',
        unsafe_allow_html=True,
    )
with m2:
    st.markdown(
        f'<div class="metric-card"><h3>{recommendations[0].score if recommendations else 0}</h3><div class="subtle">Top Match Score</div></div>',
        unsafe_allow_html=True,
    )
with m3:
    st.markdown(
        f'<div class="metric-card"><h3>{profile["technical"]}/10</h3><div class="subtle">Technical Strength</div></div>',
        unsafe_allow_html=True,
    )
with m4:
    st.markdown(
        f'<div class="metric-card"><h3>{profile["analytical"]}/10</h3><div class="subtle">Analytical Strength</div></div>',
        unsafe_allow_html=True,
    )

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "Discover Careers",
        "Market Analysis",
        "Learning Roadmap",
        "Career Insights",
        "Chat Assistant",
        "History",
    ]
)

with tab1:
    st.subheader("Discover Your Best Career Paths")
    st.caption("This tab works without external APIs. It uses your profile and skill scores to rank suitable careers.")

    cols = st.columns(3)
    for idx, rec in enumerate(recommendations[:6]):
        with cols[idx % 3]:
            image_path = CAREER_IMAGES.get(rec.career, "")
           
            if image_path and os.path.exists(image_path):
                st.image(image_path, use_container_width=True)
            else:
                st.warning(f"Image not found for {rec.career}")
            
            # st.markdown('<div class="career-card">', unsafe_allow_html=True)
            st.markdown(f"### {rec.career}")
            st.progress(int(rec.score))
            st.write(f"Score: {rec.score} | {rec.fit_label}")
            st.write(rec.summary)
            st.write("Top tools:")
            st.write(", ".join(rec.tools[:5]))

            if rec.gaps:
                st.write("Skill gaps:")
                for gap in rec.gaps:
                    st.write(f"• {gap}")

            if st.button(f"Select {rec.career}", key=f"select_{rec.career}"):
                st.session_state.selected_career = rec.career
                add_history(
                    "recommendation",
                    {
                        "career": rec.career,
                        "score": rec.score,
                        "fit": rec.fit_label,
                        "profile": profile_snapshot(profile),
                    },
                )
                st.rerun()

            # st.markdown("</div>", unsafe_allow_html=True)

    if selected_rec:
        st.markdown("### Selected Career Summary")
        st.info(f"Selected career: {selected_rec.career}")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.write("Why this fits you")
            st.write(selected_rec.summary)
            st.write("Fit label:", selected_rec.fit_label)
            st.write("Roadmap hint:", selected_rec.roadmap_hint)
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.write("Recommended certifications")
            for cert in selected_rec.certifications:
                st.write(f"• {cert}")

            st.write("Skill gaps to close")
            for gap in selected_rec.gaps or ["Your current profile is already close to this target."]:
                st.write(f"• {gap}")
            st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.subheader("Market Analysis")
    st.caption("Uses SerpAPI to pull live Google Jobs research for the selected career.")

    if not selected_rec:
        st.warning("Select a career first in Discover Careers.")
    else:
        st.write(f"Selected career: {selected_rec.career}")

        if st.button("Run Live Market Research", key="market_research"):
            if not serpapi_key:
                st.error("SerpAPI key not found in secrets.toml or environment variables.")
            else:
                with st.spinner("Fetching live job market data..."):
                    try:
                        result = fetch_job_market(
                            serpapi_key,
                            selected_rec.career,
                            profile.get("location", "India"),
                        )
                        st.session_state.market_cache[selected_rec.career] = result
                        add_history(
                            "market_analysis",
                            {
                                "career": selected_rec.career,
                                "location": profile.get("location", "India"),
                                "job_count": result["job_count"],
                            },
                        )
                    except Exception as exc:
                        st.error(f"Market analysis failed: {exc}")

        market = st.session_state.market_cache.get(selected_rec.career)
        if market:
            a, b, c = st.columns(3)
            a.metric("Jobs found", market["job_count"])
            b.metric("Top companies", len(market["top_companies"]))
            c.metric("Top skills", len(market["top_skills"]))

            st.markdown("#### Skills in demand")
            skills_df = pd.DataFrame(market["top_skills"], columns=["Skill", "Mentions"])
            if not skills_df.empty:
                st.bar_chart(skills_df.set_index("Skill"))
            else:
                st.info("No clear skill mentions found in current job results.")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Top companies")
                for company, count in market["top_companies"]:
                    st.write(f"• {company} ({count})")

            with col2:
                st.markdown("#### Top locations")
                for loc, count in market["top_locations"]:
                    st.write(f"• {loc} ({count})")

            st.markdown("#### Live job samples")
            for job in market["top_jobs"]:
                with st.expander(f"{job['title']} | {job['company']} | {job['location']}"):
                    st.write(f"Source: {job['via'] or 'Unknown'}")
                    st.write(f"Salary or schedule: {job['salary']}")
                    st.write(job["description"])
        else:
            st.info("No market analysis yet. Click Run Live Market Research.")

with tab3:
    st.subheader("Learning Roadmap")
    st.caption("Uses Gemini to build a personalized learning roadmap for the selected career.")

    if not selected_rec:
        st.warning("Select a career first in Discover Careers.")
    else:
        if st.button("Generate Roadmap", key="roadmap_btn"):
            if not gemini_key:
                st.error("Gemini API key not found in secrets.toml or environment variables.")
            else:
                prompt = build_roadmap_prompt(
                    selected_rec.career,
                    profile_summary(profile),
                    selected_rec.roadmap_hint,
                )
                with st.spinner("Generating roadmap with Gemini..."):
                    try:
                        roadmap_text = generate_text(gemini_key, prompt)
                        st.session_state.roadmap_cache[selected_rec.career] = roadmap_text
                        add_history("roadmap", {"career": selected_rec.career})
                    except Exception as exc:
                        st.error(f"Roadmap generation failed: {exc}")

        roadmap = st.session_state.roadmap_cache.get(selected_rec.career)
        if roadmap:
            st.markdown(roadmap)
        else:
            st.info("No roadmap generated yet. Click Generate Roadmap.")

with tab4:
    st.subheader("Career Insights")
    st.caption("Uses Gemini to explain role details, tools, certifications, and hiring expectations.")

    if not selected_rec:
        st.warning("Select a career first in Discover Careers.")
    else:
        if st.button("Generate Career Insights", key="insights_btn"):
            if not gemini_key:
                st.error("Gemini API key not found in secrets.toml or environment variables.")
            else:
                prompt = build_insights_prompt(
                    selected_rec.career,
                    profile_summary(profile),
                    selected_rec.tools,
                    selected_rec.certifications,
                )
                with st.spinner("Generating insights with Gemini..."):
                    try:
                        insights_text = generate_text(gemini_key, prompt)
                        st.session_state.insights_cache[selected_rec.career] = insights_text
                        add_history("insights", {"career": selected_rec.career})
                    except Exception as exc:
                        st.error(f"Career insights failed: {exc}")

        insights = st.session_state.insights_cache.get(selected_rec.career)
        if insights:
            st.markdown(insights)
        else:
            st.info("No insights yet. Click Generate Career Insights.")

with tab5:
    st.subheader("Career Chat Assistant")
    st.caption("Ask questions about the selected career. Gemini answers in the context of your profile.")

    if not selected_rec:
        st.warning("Select a career first in Discover Careers.")
    else:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        user_question = st.chat_input(f"Ask about {selected_rec.career}")
        if user_question:
            st.session_state.chat_messages.append({"role": "user", "content": user_question})

            with st.chat_message("user"):
                st.write(user_question)

            with st.chat_message("assistant"):
                if not gemini_key:
                    answer = "Gemini API key not found in secrets.toml or environment variables."
                    st.write(answer)
                else:
                    prompt = build_chat_prompt(
                        selected_rec.career,
                        profile_summary(profile),
                        st.session_state.chat_messages,
                        user_question,
                    )
                    with st.spinner("Thinking..."):
                        try:
                            answer = generate_text(gemini_key, prompt)
                        except Exception as exc:
                            answer = f"Chat failed: {exc}"
                    st.write(answer)

                st.session_state.chat_messages.append({"role": "assistant", "content": answer})
                add_history("chat", {"career": selected_rec.career, "question": user_question})

with tab6:
    st.subheader("History")
    history = read_history()

    if history:
        for item in history:
            with st.expander(f"{item['timestamp']} | {item['type']}"):
                st.json(item["payload"])
    else:
        st.info("No history yet. Select careers and run tabs to start building history.")
