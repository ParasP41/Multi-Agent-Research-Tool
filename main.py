from html import escape
from concurrent.futures import Future, ThreadPoolExecutor
import re
import time
import traceback

import streamlit as st

from agents.readerAgent import reader_Agent as build_reader_agent
from agents.searchAgent import search_Agent as build_search_agent
from agents.trendingAgent import trending_Agent as build_trending_agent
from chains.criticChain import critic_chain
from chains.writerChain import writer_chain


st.set_page_config(
    page_title="DeepAgents Research",
    page_icon="R",
    layout="wide",
    initial_sidebar_state="collapsed",
)


st.markdown(
    """
<style>
:root {
    --bg: #000000;
    --surface: #0a0a0a;
    --ink: #ffffff;
    --muted: #8a8a8a;
    --line: #1f1f1f;
    --accent-2: #22c55e;
    --accent-3: #38bdf8;
}

html, body, [class*="css"] {
    color: var(--ink);
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.stApp { background: #000000; }
#MainMenu, footer, header { visibility: hidden; }

.block-container {
    max-width: 1100px;
    padding: 4rem 2rem 6rem;
}

/* Extra bottom padding when search bar is docked so content isn't hidden */
.block-container.has-docked-bar { padding-bottom: 12rem; }

/* ===== Hero ===== */
.hero {
    text-align: center;
    margin: 1.5rem auto 0;
    max-width: 820px;
    animation: hero-in 0.55s ease-out both;
}
.hero.leaving { animation: hero-out 0.45s ease-in both; }
.hero h1 {
    color: #ffffff;
    font-size: 3rem;
    font-weight: 600;
    line-height: 1.15;
    letter-spacing: -0.01em;
    margin: 0 0 1.1rem;
}
.hero p {
    color: #9a9a9a;
    font-size: 1.05rem;
    line-height: 1.6;
    margin: 0 auto;
    max-width: 640px;
    font-weight: 400;
}

@keyframes hero-in {
    from { opacity: 0; transform: translateY(-12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes hero-out {
    from { opacity: 1; transform: translateY(0); }
    to   { opacity: 0; transform: translateY(-24px); }
}

/* ===== Slide/fade transitions for results layout ===== */
.results-stack { animation: results-in 0.55s ease-out both; }
@keyframes results-in {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ===== Search pill (hero mode) ===== */
.st-key-form_area {
    max-width: 820px;
    margin: 2.5rem auto 0 !important;
    position: relative;
    animation: bar-in 0.5s ease-out both;
}
@keyframes bar-in {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ===== Search pill (docked / bottom mode) ===== */
.docked-mode .st-key-form_area {
    position: fixed !important;
    left: 0; right: 0; bottom: 0;
    margin: 0 !important;
    padding: 1rem 1.25rem 1.5rem;
    background: linear-gradient(180deg, rgba(0,0,0,0) 0%, #000 35%, #000 100%);
    z-index: 100;
    max-width: 100% !important;
    animation: dock-up 0.55s ease-out both;
}
.docked-mode .st-key-form_area > div {
    max-width: 820px;
    margin: 0 auto;
}
@keyframes dock-up {
    from { opacity: 0; transform: translateY(40px); }
    to   { opacity: 1; transform: translateY(0); }
}

.st-key-form_area [data-testid="stForm"] {
    background: #0a0a0a !important;
    border: 1px solid #222222 !important;
    border-radius: 999px !important;
    padding: 0.55rem 0.6rem 0.55rem 3.4rem !important;
    box-shadow: 0 1px 0 rgba(255,255,255,0.03) inset, 0 20px 60px rgba(0,0,0,0.55);
    position: relative;
}

.st-key-form_area [data-testid="stForm"]::before {
    content: "";
    position: absolute;
    left: 1.4rem;
    top: 50%;
    transform: translateY(-50%);
    width: 22px;
    height: 22px;
    background-repeat: no-repeat;
    background-position: center;
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%236b6b6b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='11' cy='11' r='7'/><line x1='21' y1='21' x2='16.65' y2='16.65'/></svg>");
    pointer-events: none;
    z-index: 5;
}

.st-key-form_area [data-testid="stForm"] > div {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 0.5rem !important;
}

.st-key-form_area [data-testid="stTextInput"] {
    flex: 1 1 auto !important;
    margin: 0 !important;
    position: relative;
}

.st-key-form_area .stTextInput label,
.st-key-form_area [data-testid="stWidgetLabel"] {
    display: none !important;
}

.st-key-form_area .stTextInput div[data-baseweb="input"],
.st-key-form_area .stTextInput > div > div {
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
}

.st-key-form_area .stTextInput input {
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-size: 1.05rem !important;
    font-weight: 400 !important;
    min-height: 3rem !important;
    padding: 0 0.25rem !important;
    outline: none !important;
    position: relative;
    z-index: 2;
}

.st-key-form_area .stTextInput input::placeholder {
    color: transparent !important;
}

/* ===== Animated rotating placeholder overlay ===== */
.docked-mode .st-key-form_area [data-testid="stTextInput"]::after,
.st-key-form_area [data-testid="stTextInput"]::after {
    content: "";
    position: absolute;
    left: 0.45rem;
    top: 50%;
    transform: translateY(-50%);
    color: #5a5a5a;
    font-size: 1.05rem;
    font-weight: 400;
    pointer-events: none;
    z-index: 1;
    white-space: nowrap;
    overflow: hidden;
    max-width: calc(100% - 5rem);
    animation: placeholder-cycle 16s linear infinite;
}
@keyframes placeholder-cycle {
    0%, 22%   { content: "Ask anything  e.g. \"the future of solid-state batteries\""; }
    25%, 47%  { content: "Try  \"breakthroughs in fusion energy\""; }
    50%, 72%  { content: "Try  \"latest in autonomous driving\""; }
    75%, 97%  { content: "Try  \"protein folding with AI\""; }
}
/* Hide animated placeholder once user has typed */
.st-key-form_area [data-testid="stTextInput"]:has(input:not(:placeholder-shown))::after,
.st-key-form_area [data-testid="stTextInput"]:focus-within::after {
    display: none;
}

.st-key-form_area .stFormSubmitButton {
    flex: 0 0 auto !important;
    margin: 0 !important;
    width: auto !important;
}

.st-key-form_area .stFormSubmitButton button {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 14px !important;
    color: transparent !important;
    width: 3.25rem !important;
    min-width: 3.25rem !important;
    height: 3rem !important;
    min-height: 3rem !important;
    padding: 0 !important;
    position: relative;
    box-shadow: none !important;
    transition: background 0.18s ease, border-color 0.18s ease, transform 0.18s ease !important;
}
.st-key-form_area .stFormSubmitButton button p {
    color: transparent !important;
    font-size: 0 !important;
    margin: 0 !important;
}
.st-key-form_area .stFormSubmitButton button::after {
    content: "";
    position: absolute;
    inset: 0;
    background-repeat: no-repeat;
    background-position: center;
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><line x1='5' y1='12' x2='19' y2='12'/><polyline points='12 5 19 12 12 19'/></svg>");
}
.st-key-form_area .stFormSubmitButton button:hover {
    background: #242424 !important;
    border-color: #3a3a3a !important;
}

/* ===== Stop / Cancel button (replaces submit button while running) ===== */
.st-key-form_area .stFormSubmitButton button:disabled {
    display: none !important;
}
.st-key-form_area > div {
    position: relative;
}
.st-key-form_area .st-key-stop_area {
    position: absolute !important;
    top: 0.55rem;
    right: 0.6rem;
    margin: 0 !important;
    max-width: none !important;
    width: auto !important;
    z-index: 10;
    display: block !important;
}
.st-key-stop_area .stButton {
    margin: 0 !important;
}
.st-key-stop_area .stButton button {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    color: transparent !important;
    width: 3.25rem !important;
    min-width: 3.25rem !important;
    height: 3rem !important;
    min-height: 3rem !important;
    padding: 0 !important;
    border-radius: 14px !important;
    position: relative;
    overflow: hidden;
    box-shadow: none !important;
    transition: background 0.18s ease, border-color 0.18s ease !important;
}
.st-key-stop_area .stButton button p {
    color: transparent !important;
    font-size: 0 !important;
    margin: 0 !important;
}
/* Spinner ring (default, visible while running) */
.st-key-stop_area .stButton button::before {
    content: "";
    position: absolute;
    left: 50%;
    top: 50%;
    width: 1.1rem;
    height: 1.1rem;
    margin: -0.55rem 0 0 -0.55rem;
    border-radius: 50%;
    border: 2px solid rgba(255,255,255,0.18);
    border-top-color: #ffffff;
    animation: spin 0.8s linear infinite;
    transition: opacity 0.15s ease;
    opacity: 1;
}
/* Stop square (revealed on hover) */
.st-key-stop_area .stButton button::after {
    content: "";
    position: absolute;
    inset: 0;
    background-repeat: no-repeat;
    background-position: center;
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='%23ef4444'><rect x='5' y='5' width='14' height='14' rx='2'/></svg>");
    opacity: 0;
    transition: opacity 0.15s ease;
}
.st-key-stop_area .stButton button:hover {
    background: #242424 !important;
    border-color: rgba(239,68,68,0.55) !important;
}
.st-key-stop_area .stButton button:hover::before { opacity: 0; }
.st-key-stop_area .stButton button:hover::after { opacity: 1; }

/* ===== Trending divider ===== */
.trending-divider {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin: 4rem auto 1.5rem;
    max-width: 1000px;
    color: #6a6a6a;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    justify-content: center;
}
.trending-divider::before,
.trending-divider::after {
    content: "";
    flex: 1;
    height: 1px;
    background: #1f1f1f;
}

/* ===== Trending cards ===== */
.st-key-trending_area .stButton button {
    background: #0a0a0a !important;
    border: 1px solid #1f1f1f !important;
    border-radius: 14px !important;
    color: #ffffff !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 1.15rem 1rem 1.15rem 3.25rem !important;
    min-height: 4.5rem !important;
    line-height: 1.3 !important;
    position: relative;
    box-shadow: 0 1px 0 rgba(255,255,255,0.02) inset;
    transition: background 0.18s ease, border-color 0.18s ease, transform 0.18s ease !important;
    white-space: normal !important;
    word-break: normal !important;
}
.st-key-trending_area .stButton button p {
    color: #ffffff !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    text-align: left !important;
    margin: 0 !important;
    line-height: 1.3 !important;
}
.st-key-trending_area .stButton button:hover {
    background: #121212 !important;
    border-color: #2e2e2e !important;
    transform: translateY(-1px);
}

.trend-note {
    color: #555;
    font-size: 0.78rem;
    text-align: center;
    margin-top: 1rem;
}

/* ===== Pipeline / steps ===== */
.section-title {
    color: var(--ink);
    font-size: 1rem;
    font-weight: 700;
    margin: 0 0 0.75rem;
}
.pipeline { display: grid; gap: 0.65rem; }
.step-card {
    position: relative;
    background: #0a0a0a;
    border: 1px solid var(--line);
    border-left: 3px solid #2a2a2a;
    border-radius: 12px;
    padding: 0.9rem 1rem;
    overflow: hidden;
    transition: transform 0.18s ease, border-color 0.18s ease, background 0.18s ease;
    cursor: help;
    animation: step-in 0.35s ease-out both;
}
@keyframes step-in {
    from { opacity: 0; }
    to   { opacity: 1; }
}
.step-card:hover {
    transform: translateY(-1px);
    border-color: #3a3a3a;
    background: #101010;
}
.step-card.running {
    border-left-color: #ffffff;
    background: #111111;
    animation: card-pulse 1.6s ease-in-out infinite;
}
.step-card.running::before {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.06) 50%, transparent 100%);
    transform: translateX(-100%);
    animation: shimmer 1.6s linear infinite;
    pointer-events: none;
}
@keyframes card-pulse {
    0%, 100% { border-left-color: #ffffff; }
    50%      { border-left-color: #cfcfcf; box-shadow: 0 0 0 3px rgba(255,255,255,0.04); }
}
@keyframes shimmer {
    0%   { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

.step-card.done { border-left-color: var(--accent-2); }
.step-card.cancelled { border-left-color: #ef4444; opacity: 0.7; }
.step-top { display: flex; align-items: center; justify-content: space-between; gap: 0.75rem; }
.step-name { color: var(--ink); font-size: 0.95rem; font-weight: 700; display: flex; align-items: center; gap: 0.55rem; }
.step-status { color: var(--muted); font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; display: inline-flex; align-items: center; gap: 0.4rem; }
.running .step-status { color: #ffffff; }
.done .step-status { color: var(--accent-2); }
.cancelled .step-status { color: #ef4444; }
.step-desc { color: var(--muted); font-size: 0.84rem; line-height: 1.45; margin-top: 0.35rem; position: relative; z-index: 1; }

.spinner {
    width: 0.85rem; height: 0.85rem; border-radius: 50%;
    border: 2px solid rgba(255,255,255,0.18);
    border-top-color: #ffffff;
    animation: spin 0.8s linear infinite;
    display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }

.dots::after {
    content: ""; display: inline-block; width: 1ch; text-align: left;
    animation: dots 1.2s steps(4, end) infinite;
}
@keyframes dots {
    0% { content: ""; } 25% { content: "."; } 50% { content: ".."; }
    75% { content: "..."; } 100% { content: ""; }
}

.check {
    display: inline-block; width: 0.85rem; height: 0.85rem;
    border-radius: 50%; background: var(--accent-2); position: relative;
    animation: pop 0.3s ease-out;
}
.check::after {
    content: ""; position: absolute; left: 4px; top: 1px;
    width: 3px; height: 7px; border: solid #000;
    border-width: 0 2px 2px 0; transform: rotate(45deg);
}
@keyframes pop { 0% { transform: scale(0.2); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }

.loading-bar {
    position: relative; height: 3px; width: 100%;
    background: #141414; border-radius: 999px; overflow: hidden; margin: 0 0 1rem;
}
.loading-bar::after {
    content: ""; position: absolute; inset: 0; width: 40%;
    background: linear-gradient(90deg, transparent, #ffffff, transparent);
    animation: slide 1.4s ease-in-out infinite;
}
@keyframes slide { 0% { left: -40%; } 100% { left: 100%; } }

/* ===== Results ===== */
.session-block {
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 1.25rem 1.25rem 1.5rem;
    margin: 1.25rem 0;
    background: #060606;
    animation: results-in 0.45s ease-out both;
}
.session-topic {
    color: #ffffff;
    font-size: 1.1rem;
    font-weight: 600;
    margin: 0 0 0.5rem;
}
.session-meta {
    color: #666;
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.session-meta.cancelled { color: #ef4444; }

.result-box {
    background: #0a0a0a; border: 1px solid var(--line);
    border-radius: 12px; padding: 1rem; margin-top: 0.75rem;
}
.label {
    color: var(--muted); font-size: 0.72rem; font-weight: 700;
    letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.6rem;
}
.label.blue { color: var(--accent-3); }
.label.green { color: var(--accent-2); }
.raw-output { color: var(--ink); font-size: 0.9rem; line-height: 1.65; white-space: pre-wrap; overflow-wrap: anywhere; }

.compact-divider { background: var(--line); height: 1px; margin: 2rem 0 1rem; }

.console-error {
    background: #080808; border: 1px solid #3a1f1f; border-left: 4px solid #ef4444;
    border-radius: 8px; color: #ffd7d7; font-family: Consolas, monospace;
    font-size: 0.82rem; padding: 1rem; white-space: pre-wrap;
}

.stDownloadButton button {
    background: #ffffff !important; border: 1px solid #ffffff !important;
    border-radius: 10px !important; color: #000000 !important;
    font-weight: 600 !important; min-height: 2.75rem;
}
.stDownloadButton button:hover { background: #e5e5e5 !important; border-color: #e5e5e5 !important; }

[data-testid="stExpander"] {
    background: #0a0a0a !important;
    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
}

@media (max-width: 760px) {
    .block-container { padding: 2rem 1rem 4rem; }
    .block-container.has-docked-bar { padding-bottom: 11rem; }
    .hero h1 { font-size: 2rem; }
    .hero p { font-size: 0.9rem; }
    .st-key-form_area [data-testid="stForm"] { padding-left: 2.75rem !important; }
    .st-key-form_area [data-testid="stForm"]::before { left: 0.9rem; }
    .st-key-trending_area [data-testid="stHorizontalBlock"] { flex-direction: column; }
    .st-key-trending_area [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
}
</style>
""",
    unsafe_allow_html=True,
)


# ====================== Helpers ======================

def step_card(title: str, state: str, desc: str, tip: str = "") -> None:
    labels = {"waiting": "Waiting", "running": "Running", "done": "Done", "cancelled": "Cancelled"}
    card_class = state if state in {"running", "done", "cancelled"} else ""
    if state == "running":
        status_html = '<span class="spinner"></span><span>Running</span>'
    elif state == "done":
        status_html = '<span class="check"></span><span>Done</span>'
    elif state == "cancelled":
        status_html = '<span>Cancelled</span>'
    else:
        status_html = f'<span>{labels.get(state, "Waiting")}</span>'
    tip_attr = f' data-tip="{escape(tip)}"' if tip else ""
    st.markdown(
        f"""
<div class="step-card {card_class}"{tip_attr}>
    <div class="step-top">
        <div class="step-name">{escape(title)}</div>
        <div class="step-status">{status_html}</div>
    </div>
    <div class="step-desc">{escape(desc)}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def step_state_for(results: dict, running: bool, step: str, cancelled: bool = False) -> str:
    steps = ["search", "reader", "writer", "critic"]
    if step in results:
        return "done"
    if cancelled:
        return "cancelled"
    if running:
        for item in steps:
            if item not in results:
                return "running" if item == step else "waiting"
    return "waiting"


def raw_result(title: str, content: str) -> None:
    st.markdown(
        f"""
<div class="result-box">
    <div class="label">{escape(title)}</div>
    <div class="raw-output">{escape(content)}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def parse_trending_topics(text: str) -> list[str]:
    topics = []
    for line in text.splitlines():
        cleaned = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", line).strip()
        cleaned = cleaned.strip("\"'` ")
        if ":" in cleaned:
            cleaned = cleaned.split(":", 1)[-1].strip()
        if 4 <= len(cleaned) <= 80 and cleaned not in topics:
            topics.append(cleaned)
        if len(topics) == 4:
            break
    return topics


FALLBACK_TRENDING_TOPICS = [
    "AI in Healthcare",
    "Renewable Innovations",
    "Sustainable Solutions",
    "Autonomous Robotics",
]


@st.cache_resource(show_spinner=False)
def get_trending_executor() -> ThreadPoolExecutor:
    return ThreadPoolExecutor(max_workers=1)


def fetch_trending_topics() -> list[str]:
    try:
        trending_agent = build_trending_agent()
        response = trending_agent.invoke(
            {"messages": [(
                "user",
                "Find 4 current trending research topics in technology, science, AI, "
                "health, or energy. Return only the topic names, one per line. "
                "Keep each topic under 4 words.",
            )]}
        )
        content = response["messages"][-1].content
        topics = parse_trending_topics(content)
        return topics[:4] if len(topics) == 4 else FALLBACK_TRENDING_TOPICS
    except Exception:
        return FALLBACK_TRENDING_TOPICS


def get_visible_trending_topics() -> list[str]:
    future: Future | None = st.session_state.trending_future
    if st.session_state.trending_loaded:
        return st.session_state.trending_topics
    if future is None:
        st.session_state.trending_future = get_trending_executor().submit(fetch_trending_topics)
        return st.session_state.trending_topics
    if future.done():
        try:
            st.session_state.trending_topics = future.result()
        except Exception:
            st.session_state.trending_topics = FALLBACK_TRENDING_TOPICS
        st.session_state.trending_loaded = True
        st.session_state.trending_future = None
    return st.session_state.trending_topics


# ====================== State ======================

def start_pipeline(topic_value: str) -> None:
    st.session_state.active_topic = topic_value
    st.session_state.results = {}
    st.session_state.running = True
    st.session_state.done = False
    st.session_state.cancel_requested = False
    st.session_state.error = ""
    st.session_state.error_details = ""


def start_pipeline_from_trending(topic_value: str) -> None:
    st.session_state.pending_topic_input = topic_value
    start_pipeline(topic_value)


def request_cancel() -> None:
    """Cancel running pipeline and revert UI to input state.

    Note: a blocking agent call already in flight cannot be killed mid-call
    in pure Python; we set a flag that is checked between pipeline steps
    and immediately clear the active run from the UI on rerun.
    """
    st.session_state.cancel_requested = True
    st.session_state.running = False
    st.session_state.done = False
    # Drop the in-progress run entirely so the UI reverts to the input state.
    st.session_state.results = {}
    st.session_state.active_topic = ""


def stop_with_error(message: str, error: Exception) -> None:
    st.session_state.running = False
    st.session_state.done = False
    st.session_state.error = message
    st.session_state.error_details = "".join(
        traceback.format_exception(type(error), error, error.__traceback__)
    )
    st.rerun()


def archive_current_session(status: str = "done") -> None:
    """Move the active run into history so subsequent searches stack like a chat."""
    if not st.session_state.active_topic and not st.session_state.results:
        return
    st.session_state.history.append({
        "topic": st.session_state.active_topic,
        "results": dict(st.session_state.results),
        "status": status,
        "ts": time.time(),
    })


state_defaults = {
    "results": {},
    "running": False,
    "done": False,
    "cancel_requested": False,
    "error": "",
    "error_details": "",
    "active_topic": "",
    "pending_topic_input": "",
    "history": [],
    "trending_topics": FALLBACK_TRENDING_TOPICS,
    "trending_future": None,
    "trending_loaded": False,
}
for key, value in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

if st.session_state.pending_topic_input:
    st.session_state.topic_input = st.session_state.pending_topic_input
    st.session_state.pending_topic_input = ""


has_history = bool(st.session_state.history)
has_active = bool(st.session_state.results) or st.session_state.running
in_chat_mode = has_history or has_active
show_intro = not in_chat_mode

# Toggle docked layout class on the app shell
if in_chat_mode:
    st.markdown(
        "<style>.block-container{padding-bottom:12rem;}</style>"
        "<script>document.body.classList.add('docked-mode');</script>",
        unsafe_allow_html=True,
    )
    # Streamlit strips <script>; emulate via a marker element + CSS selector
    st.markdown('<div id="docked-marker"></div>', unsafe_allow_html=True)
    st.markdown(
        """
<style>
/* When the marker is on the page, treat the app as docked */
.stApp:has(#docked-marker) .st-key-form_area {
    position: fixed !important;
    left: 0; right: 0; bottom: 0;
    margin: 0 !important;
    padding: 1rem 1.25rem 1.5rem;
    background: linear-gradient(180deg, rgba(0,0,0,0) 0%, #000 35%, #000 100%);
    z-index: 100;
    max-width: 100% !important;
    animation: dock-up 0.55s ease-out both;
}
.stApp:has(#docked-marker) .st-key-form_area > div {
    max-width: 820px;
    margin: 0 auto;
}
.stApp:has(#docked-marker) .st-key-form_area .st-key-stop_area {
    top: 1.55rem;
    right: 1.85rem;
}
</style>
""",
        unsafe_allow_html=True,
    )


# ===== Intro (hero) mode =====
if show_intro:
    st.markdown(
        """
<div class="hero">
    <h1>What should we research today?</h1>
    <p>Give it a topic and the search, reader, writer, and critic agents
    will work together to build a clean, sourced research report.</p>
</div>
""",
        unsafe_allow_html=True,
    )


# ===== Chat-like history of previous research sessions =====
if has_history:
    st.markdown('<div class="results-stack">', unsafe_allow_html=True)
    for idx, session in enumerate(st.session_state.history):
        status_class = "cancelled" if session.get("status") == "cancelled" else ""
        st.markdown(
            f"""
<div class="session-block">
    <div class="session-topic">{escape(session.get("topic", ""))}</div>
    <div class="session-meta {status_class}">
        {"Cancelled" if status_class else "Completed"} ·
        {time.strftime('%H:%M', time.localtime(session.get('ts', time.time())))}
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
        results = session.get("results", {})
        if "search" in results:
            with st.expander(f"Search results · run {idx + 1}", expanded=False):
                raw_result("Search Agent Output", results["search"])
        if "reader" in results:
            with st.expander(f"Scraped content · run {idx + 1}", expanded=False):
                raw_result("Reader Agent Output", results["reader"])
        if "writer" in results:
            st.markdown(
                '<div class="result-box"><div class="label blue">Final Research Report</div></div>',
                unsafe_allow_html=True,
            )
            st.markdown(results["writer"])
            st.download_button(
                label="Download report",
                data=results["writer"],
                file_name=f"research_report_{int(session.get('ts', time.time()))}.md",
                mime="text/markdown",
                use_container_width=True,
                key=f"dl_{idx}",
            )
        if "critic" in results:
            st.markdown(
                '<div class="result-box"><div class="label green">Critic Feedback</div></div>',
                unsafe_allow_html=True,
            )
            st.markdown(results["critic"])
    st.markdown('</div>', unsafe_allow_html=True)


# ===== Active run: pipeline + partial results =====
if has_active:
    st.markdown('<div class="results-stack">', unsafe_allow_html=True)
    st.markdown('<div class="compact-divider"></div>', unsafe_allow_html=True)
    if st.session_state.active_topic:
        st.markdown(
            f'<div class="session-topic">{escape(st.session_state.active_topic)}</div>',
            unsafe_allow_html=True,
        )
    st.markdown('<div class="section-title">Pipeline</div>', unsafe_allow_html=True)
    if st.session_state.running:
        st.markdown('<div class="loading-bar"></div>', unsafe_allow_html=True)

    pipeline_placeholder = st.empty()

    def render_pipeline(results_snapshot: dict, running_flag: bool) -> None:
        with pipeline_placeholder.container():
            st.markdown('<div class="pipeline">', unsafe_allow_html=True)
            step_card("Search Agent",
                      step_state_for(results_snapshot, running_flag, "search"),
                      "Finds relevant web results for the topic.",
                      tip="Queries the web for recent, reliable sources")
            step_card("Reader Agent",
                      step_state_for(results_snapshot, running_flag, "reader"),
                      "Reads a useful source and extracts details.",
                      tip="Opens the best link and scrapes deep content")
            step_card("Writer Chain",
                      step_state_for(results_snapshot, running_flag, "writer"),
                      "Turns the research into a structured report.",
                      tip="Synthesizes findings into a clean markdown report")
            step_card("Critic Chain",
                      step_state_for(results_snapshot, running_flag, "critic"),
                      "Reviews the report and gives feedback.",
                      tip="Audits accuracy, gaps, and clarity")
            st.markdown('</div>', unsafe_allow_html=True)

    render_pipeline(st.session_state.results, st.session_state.running)
    st.session_state["_render_pipeline"] = render_pipeline

    results = st.session_state.results
    if results:
        st.markdown('<div class="section-title" style="margin-top:1.5rem;">Results</div>', unsafe_allow_html=True)
        if "search" in results:
            with st.expander("Search results", expanded=False):
                raw_result("Search Agent Output", results["search"])
        if "reader" in results:
            with st.expander("Scraped content", expanded=False):
                raw_result("Reader Agent Output", results["reader"])
        if "writer" in results:
            st.markdown(
                '<div class="result-box"><div class="label blue">Final Research Report</div></div>',
                unsafe_allow_html=True,
            )
            st.markdown(results["writer"])
            st.download_button(
                label="Download report",
                data=results["writer"],
                file_name=f"research_report_{int(time.time())}.md",
                mime="text/markdown",
                use_container_width=True,
                key="dl_active",
            )
        if "critic" in results:
            st.markdown(
                '<div class="result-box"><div class="label green">Critic Feedback</div></div>',
                unsafe_allow_html=True,
            )
            st.markdown(results["critic"])
    st.markdown('</div>', unsafe_allow_html=True)


# ===== Search pill (always rendered; docked when in chat mode) =====
with st.container(key="form_area"):
    with st.form("research_form", clear_on_submit=True):
        topic = st.text_input(
            "Research topic",
            key="topic_input",
            label_visibility="collapsed",
            placeholder="Ask anything…",
        )
        run_btn = st.form_submit_button(
            "Run",
            use_container_width=False,
            help="Launch the 4-agent research pipeline",
            disabled=st.session_state.running,
        )
    if st.session_state.running:
        with st.container(key="stop_area"):
            st.button(
                "Stop",
                key="cancel_pipeline_btn",
                on_click=request_cancel,
                help="Cancel the running pipeline and return to input",
            )


# ===== Trending (only on intro) =====
if show_intro:
    st.markdown('<div class="trending-divider">Trending Topics</div>', unsafe_allow_html=True)
    with st.container(key="trending_area"):
        trending_topics = get_visible_trending_topics()
        cols = st.columns(4, gap="small")
        for index, trend in enumerate(trending_topics):
            with cols[index]:
                st.button(
                    trend,
                    key=f"trend_topic_{index}",
                    use_container_width=True,
                    on_click=start_pipeline_from_trending,
                    args=(trend,),
                    help=f"Research '{trend}' with all 4 agents",
                )
        if not st.session_state.trending_loaded:
            st.markdown('<div class="trend-note">Updating in the background...</div>', unsafe_allow_html=True)


# ===== Submit handling =====
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        start_pipeline(topic.strip())
        st.rerun()


if st.session_state.error:
    st.error(st.session_state.error)
    if st.session_state.error_details:
        with st.expander("Console error details", expanded=False):
            st.markdown(
                f'<div class="console-error">{escape(st.session_state.error_details)}</div>',
                unsafe_allow_html=True,
            )


# ===== Pipeline execution =====

def _check_cancelled() -> bool:
    return bool(st.session_state.get("cancel_requested"))


if st.session_state.running and not st.session_state.done:
    _rp = st.session_state.get("_render_pipeline")
    def _refresh(results_now: dict) -> None:
        if _rp:
            _rp(results_now, True)
    results: dict = {}
    topic_val = st.session_state.active_topic or st.session_state.topic_input

    if _check_cancelled():
        archive_current_session("cancelled")
        st.session_state.results = {}
        st.session_state.active_topic = ""
        st.rerun()

    with st.spinner("Search Agent is working..."):
        search_agent = build_search_agent()
        try:
            sr = search_agent.invoke(
                {"messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]}
            )
        except Exception as e:
            stop_with_error(
                "Search failed because the remote service closed the connection. "
                f"Please try again. Details: {e}",
                e,
            )
        results["search"] = sr["messages"][-1].content
        st.session_state.results = dict(results)
        _refresh(results)

    if _check_cancelled():
        archive_current_session("cancelled")
        st.session_state.results = {}
        st.session_state.active_topic = ""
        st.rerun()

    with st.spinner("Reader Agent is reading a source..."):
        reader_agent = build_reader_agent()
        try:
            rr = reader_agent.invoke(
                {"messages": [(
                    "user",
                    f"Based on the following search results about '{topic_val}', "
                    f"pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{results['search'][:800]}",
                )]}
            )
        except Exception as e:
            stop_with_error(f"Reader failed while opening or scraping a source. Please try again. Details: {e}", e)
        results["reader"] = rr["messages"][-1].content
        st.session_state.results = dict(results)
        _refresh(results)

    if _check_cancelled():
        archive_current_session("cancelled")
        st.session_state.results = {}
        st.session_state.active_topic = ""
        st.rerun()

    with st.spinner("Writer Chain is drafting the report..."):
        research_combined = (
            f"SEARCH RESULTS:\n{results['search']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
        )
        try:
            results["writer"] = writer_chain.invoke(
                {"topic": topic_val, "research": research_combined, "feedback": ""}
            )
        except Exception as e:
            stop_with_error(f"Writer failed while creating the report. Please try again. Details: {e}", e)
        st.session_state.results = dict(results)
        _refresh(results)

    if _check_cancelled():
        archive_current_session("cancelled")
        st.session_state.results = {}
        st.session_state.active_topic = ""
        st.rerun()

    with st.spinner("Critic Chain is reviewing the report..."):
        try:
            results["critic"] = critic_chain.invoke({"report": results["writer"]})
        except Exception as e:
            stop_with_error(f"Critic failed while reviewing the report. Please try again. Details: {e}", e)
        st.session_state.results = dict(results)
        _refresh(results)

    st.session_state.running = False
    st.session_state.done = True
    archive_current_session("done")
    st.session_state.results = {}
    st.session_state.active_topic = ""
    st.rerun()
