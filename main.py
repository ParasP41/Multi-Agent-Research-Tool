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
    --bg: #050505;
    --surface: #101010;
    --surface-2: #171717;
    --ink: #ffffff;
    --muted: #b8b8b8;
    --line: #2a2a2a;
    --soft: #1f1f1f;
    --accent: #f97316;
    --accent-2: #22c55e;
    --accent-3: #38bdf8;
    --warn: #f59e0b;
}

html, body, [class*="css"] {
    color: var(--ink);
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(249, 115, 22, 0.18), transparent 32rem),
        radial-gradient(circle at bottom right, rgba(56, 189, 248, 0.08), transparent 28rem),
        linear-gradient(180deg, #0b0b0b 0%, var(--bg) 58%, #000000 100%);
}

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    max-width: 1120px;
    padding: 2.5rem 2rem 4rem;
}

.app-shell {
    border: 1px solid var(--line);
    background: rgba(16, 16, 16, 0.72);
    border-radius: 8px;
    padding: 1rem;
}

.hero {
    border-bottom: 1px solid var(--line);
    padding: 0.75rem 0 1.5rem;
    margin-bottom: 1.5rem;
}

.eyebrow {
    color: var(--accent);
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

.hero h1 {
    color: var(--ink);
    font-size: 3rem;
    font-weight: 800;
    line-height: 1.05;
    letter-spacing: 0;
    margin: 0;
}

.hero p {
    color: var(--muted);
    max-width: 680px;
    font-size: 1rem;
    line-height: 1.65;
    margin: 0.85rem 0 0;
}

.section-title {
    color: var(--ink);
    font-size: 1.05rem;
    font-weight: 800;
    margin: 0 0 0.75rem;
}

.panel {
    background: var(--surface);
    border: 1px solid var(--line);
    box-shadow: 0 18px 45px rgba(0, 0, 0, 0.28);
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
}

.muted {
    color: var(--muted);
    font-size: 0.9rem;
    line-height: 1.5;
}

.trend-heading {
    color: var(--muted);
    font-size: 0.82rem;
    line-height: 1.4;
    margin-top: 1rem;
    margin-bottom: 0.45rem;
}

.trend-note {
    color: #777777;
    font-size: 0.76rem;
    margin-top: 0.35rem;
}

.pipeline {
    display: grid;
    gap: 0.65rem;
}

.step-card {
    background: linear-gradient(180deg, var(--surface-2), var(--surface));
    border: 1px solid var(--line);
    border-left: 4px solid #ffffff;
    border-radius: 8px;
    padding: 0.85rem 0.95rem;
    box-shadow: 0 14px 34px rgba(0, 0, 0, 0.22);
}

.step-card.running {
    border-left-color: var(--accent);
    background: linear-gradient(180deg, rgba(249, 115, 22, 0.14), var(--surface));
}

.step-card.done {
    border-left-color: var(--accent-2);
}

.step-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
}

.step-name {
    color: var(--ink);
    font-size: 0.95rem;
    font-weight: 800;
}

.step-status {
    color: var(--muted);
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    white-space: nowrap;
}

.running .step-status {
    color: var(--accent);
}

.done .step-status {
    color: var(--accent-2);
}

.step-desc {
    color: var(--muted);
    font-size: 0.84rem;
    line-height: 1.45;
    margin-top: 0.35rem;
}

.result-box {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 1rem;
    margin-top: 0.75rem;
}

.compact-divider {
    background: var(--line);
    height: 1px;
    margin: 0.85rem 0 0.75rem;
    width: 100%;
}

[data-testid="stSpinner"] {
    margin-top: 0.45rem !important;
}

.label {
    color: var(--muted);
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}

.label.blue {
    color: var(--accent-3);
}

.label.green {
    color: var(--accent-2);
}

.raw-output {
    color: var(--ink);
    font-size: 0.9rem;
    line-height: 1.65;
    overflow-wrap: anywhere;
    white-space: pre-wrap;
}

.console-error {
    background: #080808;
    border: 1px solid #3a1f1f;
    border-left: 4px solid #ef4444;
    border-radius: 8px;
    color: #ffd7d7;
    font-family: Consolas, "Courier New", monospace;
    font-size: 0.82rem;
    line-height: 1.55;
    overflow-x: auto;
    padding: 1rem;
    white-space: pre-wrap;
}

.footer-note {
    color: var(--muted);
    border-top: 1px solid var(--line);
    background: rgba(5, 5, 5, 0.92);
    backdrop-filter: blur(10px);
    font-size: 0.8rem;
    left: 0;
    margin-top: 0;
    padding: 0.85rem 1rem;
    position: fixed;
    right: 0;
    bottom: 0;
    text-align: center;
    z-index: 50;
}

.stTextInput label {
    color: var(--ink) !important;
    font-weight: 750 !important;
}

.stTextInput input::placeholder {
    color: #777777 !important;
    opacity: 1 !important;
}

.stTextInput input {
    background: #111111 !important;
    border: 1px solid var(--line) !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    caret-color: var(--accent) !important;
    color: var(--ink) !important;
    font-size: 1rem !important;
    font-weight: 550 !important;
    letter-spacing: 0 !important;
    min-height: 3rem;
    outline: none !important;
    -webkit-text-fill-color: var(--ink) !important;
}

.stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.2) !important;
}

.stTextInput input:-webkit-autofill,
.stTextInput input:-webkit-autofill:focus {
    box-shadow: 0 0 0 1000px #111111 inset !important;
    caret-color: var(--accent) !important;
    -webkit-text-fill-color: var(--ink) !important;
}

.stDownloadButton button, .stFormSubmitButton button {
    background: var(--accent) !important;
    border: 1px solid var(--accent) !important;
    border-radius: 8px !important;
    color: #111111 !important;
    font-weight: 800 !important;
    min-height: 2.8rem;
    box-shadow: 0 10px 28px rgba(249, 115, 22, 0.18) !important;
    transition: background 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease !important;
}

.stDownloadButton button:hover, .stFormSubmitButton button:hover {
    background: #fb923c !important;
    border-color: #fed7aa !important;
    color: #111111 !important;
    box-shadow: 0 14px 34px rgba(249, 115, 22, 0.34) !important;
    transform: translateY(-1px) !important;
}

.stDownloadButton button:active, .stFormSubmitButton button:active {
    background: #ea580c !important;
    border-color: #ea580c !important;
    box-shadow: 0 8px 18px rgba(249, 115, 22, 0.22) !important;
    transform: translateY(0) !important;
}

.stButton button {
    background: #151515 !important;
    border: 1px solid var(--line) !important;
    border-radius: 999px !important;
    color: var(--ink) !important;
    font-size: 0.74rem !important;
    font-weight: 750 !important;
    line-height: 1.15 !important;
    min-height: 2.05rem;
    padding: 0.25rem 0.55rem !important;
    transition: background 0.18s ease, border-color 0.18s ease, color 0.18s ease, transform 0.18s ease !important;
    white-space: normal !important;
    word-break: normal !important;
    overflow-wrap: anywhere !important;
}

.stButton button p {
    font-size: 0.74rem !important;
    line-height: 1.15 !important;
    margin: 0 !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
}

.stButton button:hover {
    background: rgba(249, 115, 22, 0.14) !important;
    border-color: var(--accent) !important;
    color: #ffd0ad !important;
    transform: translateY(-1px) !important;
}

.stButton button:active {
    background: rgba(249, 115, 22, 0.22) !important;
    transform: translateY(0) !important;
}

[data-testid="stForm"] {
    background: transparent !important;
    border: 0 !important;
    padding: 0 !important;
}

.start-copy {
    display: block;
}

.stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    color: var(--ink);
}

[data-testid="stExpander"] {
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    border-radius: 8px !important;
}

.stAlert {
    border-radius: 8px;
}

details {
    background: transparent !important;
}

details summary {
    color: var(--ink) !important;
    font-weight: 750;
}

[data-testid="stMarkdownContainer"] code {
    background: #1e1e1e;
    color: #ffd0ad;
    border: 1px solid #303030;
    border-radius: 6px;
    padding: 0.1rem 0.25rem;
}

[data-testid="stMarkdownContainer"] pre {
    background: #111111;
    border: 1px solid var(--line);
    border-radius: 8px;
    color: var(--ink);
    padding: 1rem;
    overflow-x: auto;
}

@media (max-width: 760px) {
    .block-container {
        padding: 1.25rem 1rem 5rem;
    }

    .pipeline-area,
    .trending-area,
    .st-key-pipeline_area,
    .st-key-trending_area {
        display: none !important;
    }

    .start-copy {
        display: none !important;
    }

    .element-container:has(.start-copy) {
        display: none !important;
    }

    [data-testid="stHorizontalBlock"] {
        flex-direction: column;
    }

    [data-testid="column"] {
        flex: 1 1 100% !important;
        width: 100% !important;
        min-width: 0 !important;
    }

    .hero {
        margin-bottom: 0.75rem;
        padding-top: 0;
        text-align: center;
    }

    .hero h1 {
        font-size: 2.15rem;
    }

    .hero p {
        font-size: 0.84rem;
        line-height: 1.5;
        margin-bottom: 0;
        margin-left: auto;
        margin-right: auto;
        text-align: center;
    }

    .st-key-form_area {
        display: flex;
        justify-content: center;
        margin: 0.15rem auto 0;
        max-width: calc(100vw - 2rem);
        width: min(22rem, calc(100vw - 2rem));
    }

    .st-key-form_area > div,
    .st-key-form_area [data-testid="stVerticalBlock"] {
        margin-left: auto !important;
        margin-right: auto !important;
        max-width: calc(100vw - 2rem);
        width: min(22rem, calc(100vw - 2rem)) !important;
    }

    .section-title,
    .muted,
    .stTextInput label,
    .footer-note {
        text-align: center !important;
    }

    .section-title {
        font-size: 0.9rem;
        margin-bottom: 0.45rem;
    }

    .panel {
        background: transparent;
        border: 0;
        box-shadow: none;
        margin-bottom: 0.65rem;
        padding: 0;
    }

    .muted {
        font-size: 0.76rem;
        line-height: 1.4;
        max-width: 18rem;
        margin-left: auto;
        margin-right: auto;
    }

    [data-testid="stForm"] {
        box-sizing: border-box;
        max-width: calc(100vw - 2rem);
        margin-left: auto;
        margin-right: auto;
        width: min(22rem, calc(100vw - 2rem));
    }

    [data-testid="stForm"] > div {
        align-items: center;
        display: flex;
        flex-direction: column;
        gap: 0.8rem;
        width: 100%;
    }

    [data-testid="stForm"] [data-testid="stTextInput"],
    [data-testid="stForm"] .stTextInput,
    [data-testid="stForm"] .stFormSubmitButton,
    [data-testid="stForm"] [data-testid="stFormSubmitButton"] {
        margin-left: auto !important;
        margin-right: auto !important;
        max-width: calc(100vw - 2rem) !important;
        width: min(22rem, calc(100vw - 2rem)) !important;
    }

    .stTextInput {
        box-sizing: border-box;
        max-width: calc(100vw - 2rem);
        margin-left: auto;
        margin-right: auto;
        text-align: center;
        width: min(22rem, calc(100vw - 2rem));
    }

    .stTextInput > div,
    .stTextInput > div > div,
    [data-testid="stTextInputRootElement"] {
        box-sizing: border-box !important;
        max-width: calc(100vw - 2rem) !important;
        margin-left: auto !important;
        margin-right: auto !important;
        width: min(22rem, calc(100vw - 2rem)) !important;
    }

    .stTextInput label {.compact-divider {
    margin: 0.85rem 0 0.04rem;
}
        display: block !important;
        font-size: 0.82rem !important;
        margin-bottom: 0rem !important;
        text-align: center !important;
    }

    .stTextInput [data-testid="stWidgetLabel"] {
        margin-bottom: 0.70rem !important;
    }

    .stTextInput input {
        box-sizing: border-box !important;
        font-size: 0.92rem !important;
        min-height: 2.75rem;
        padding-left: 0.85rem !important;
        padding-right: 0.85rem !important;
        text-align: left !important;
        width: 100% !important;
    }

    .stFormSubmitButton {
        box-sizing: border-box;
        display: flex;
        justify-content: center;
        margin-top: 0 !important;
        margin-left: auto;
        margin-right: auto;
        max-width: calc(100vw - 2rem);
        width: min(22rem, calc(100vw - 2rem));
    }

    .stFormSubmitButton > div {
        box-sizing: border-box;
        display: flex;
        justify-content: center;
        max-width: calc(100vw - 2rem);
        width: min(22rem, calc(100vw - 2rem));
    }

    .stFormSubmitButton button {
        box-sizing: border-box !important;
        min-height: 2.55rem;
        max-width: calc(100vw - 2rem);
        width: 100% !important;
    }

    [data-testid="stFormSubmitButton"] button,
    [data-testid="baseButton-secondaryFormSubmit"] {
        margin-left: auto !important;
        margin-right: auto !important;
        width: 100% !important;
    }

    .result-box {
        padding: 0.9rem;
    }

    .step-top {
        align-items: flex-start;
        flex-direction: column;
        gap: 0.25rem;
    }

    .step-status {
        white-space: normal;
    }

    .trend-heading {
        margin-top: 0.85rem;
    }

    .stButton button {
        min-height: 2rem;
        padding: 0.25rem 0.45rem !important;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


def step_card(title: str, state: str, desc: str) -> None:
    labels = {
        "waiting": "Waiting",
        "running": "Running",
        "done": "Done",
    }
    card_class = state if state in {"running", "done"} else ""
    st.markdown(
        f"""
<div class="step-card {card_class}">
    <div class="step-top">
        <div class="step-name">{escape(title)}</div>
        <div class="step-status">{labels.get(state, "Waiting")}</div>
    </div>
    <div class="step-desc">{escape(desc)}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def step_state(step: str) -> str:
    results = st.session_state.results
    steps = ["search", "reader", "writer", "critic"]

    if step in results:
        return "done"

    if st.session_state.running:
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
    "AI healthcare",
    "Fusion energy",
    "CRISPR medicine",
    "Humanoid robotics",
]


@st.cache_resource(show_spinner=False)
def get_trending_executor() -> ThreadPoolExecutor:
    return ThreadPoolExecutor(max_workers=1)


def fetch_trending_topics() -> list[str]:
    try:
        trending_agent = build_trending_agent()
        response = trending_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        "Find 4 current trending research topics in technology, science, AI, "
                        "health, or energy. Return only the topic names, one per line. "
                        "Keep each topic under 3 words.",
                    )
                ]
            }
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


def start_pipeline(topic_value: str) -> None:
    st.session_state.active_topic = topic_value
    st.session_state.results = {}
    st.session_state.running = True
    st.session_state.done = False
    st.session_state.error = ""
    st.session_state.error_details = ""


def start_pipeline_from_trending(topic_value: str) -> None:
    st.session_state.pending_topic_input = topic_value
    start_pipeline(topic_value)


def stop_with_error(message: str, error: Exception) -> None:
    st.session_state.running = False
    st.session_state.done = False
    st.session_state.error = message
    st.session_state.error_details = "".join(
        traceback.format_exception(type(error), error, error.__traceback__)
    )
    st.rerun()


state_defaults = {
    "results": {},
    "running": False,
    "done": False,
    "error": "",
    "error_details": "",
    "active_topic": "",
    "pending_topic_input": "",
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


st.markdown(
    """
<div class="hero">
    <div class="eyebrow">Multi-agent research workspace</div>
    <h1>Deep Research</h1>
    <p>
        Enter a topic and let the search, reader, writer, and critic agents build a clean research report.
        The interface stays quiet so the work can stay front and center.
    </p>
</div>
""",
    unsafe_allow_html=True,
)


has_results = bool(st.session_state.results)
show_intro_blocks = not has_results and not st.session_state.running

left, right = st.columns([1.15, 0.85], gap="large")

with left:
    st.markdown(
        """
<div class="start-copy">
<div class="section-title">Start a report</div>
<div class="panel">
    <div class="muted">Use a focused topic for better searches and a stronger final report.</div>
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    with st.container(key="form_area"):
        with st.form("research_form", clear_on_submit=False):
            topic = st.text_input(
                "Research topic",
                key="topic_input",
                label_visibility="visible",
            )
            run_btn = st.form_submit_button("Run research pipeline", use_container_width=True)

    if show_intro_blocks:
        with st.container(key="trending_area"):
            st.markdown('<div class="trend-heading">Trending topics</div>', unsafe_allow_html=True)
            trending_topics = get_visible_trending_topics()

            top_row = st.columns(2, gap="small")
            bottom_row = st.columns(2, gap="small")
            for index, trend in enumerate(trending_topics):
                target_column = top_row[index] if index < 2 else bottom_row[index - 2]
                with target_column:
                    st.button(
                        trend,
                        key=f"trend_topic_{index}",
                        use_container_width=True,
                        on_click=start_pipeline_from_trending,
                        args=(trend,),
                    )
            if not st.session_state.trending_loaded:
                st.markdown('<div class="trend-note">Updating in the background...</div>', unsafe_allow_html=True)

with right:
    if show_intro_blocks:
        with st.container(key="pipeline_area"):
            st.markdown('<div class="section-title">Pipeline</div>', unsafe_allow_html=True)
            st.markdown('<div class="pipeline">', unsafe_allow_html=True)
            step_card("Search Agent", step_state("search"), "Finds relevant web results for the topic.")
            step_card("Reader Agent", step_state("reader"), "Reads a useful source and extracts details.")
            step_card("Writer Chain", step_state("writer"), "Turns the research into a structured report.")
            step_card("Critic Chain", step_state("critic"), "Reviews the report and gives feedback.")
            st.markdown("</div>", unsafe_allow_html=True)


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


if st.session_state.running and not st.session_state.done:
    results = {}
    topic_val = st.session_state.active_topic or st.session_state.topic_input

    with st.spinner("Search Agent is working..."):
        search_agent = build_search_agent()
        try:
            sr = search_agent.invoke(
                {
                    "messages": [
                        ("user", f"Find recent, reliable and detailed information about: {topic_val}")
                    ]
                }
            )
        except Exception as e:
            stop_with_error(
                "Search failed because the remote service closed the connection. "
                f"Please try again. Details: {e}",
                e,
            )
        results["search"] = sr["messages"][-1].content
        st.session_state.results = dict(results)

    with st.spinner("Reader Agent is reading a source..."):
        reader_agent = build_reader_agent()
        try:
            rr = reader_agent.invoke(
                {
                    "messages": [
                        (
                            "user",
                            f"Based on the following search results about '{topic_val}', "
                            f"pick the most relevant URL and scrape it for deeper content.\n\n"
                            f"Search Results:\n{results['search'][:800]}",
                        )
                    ]
                }
            )
        except Exception as e:
            stop_with_error(
                f"Reader failed while opening or scraping a source. Please try again. Details: {e}",
                e,
            )
        results["reader"] = rr["messages"][-1].content
        st.session_state.results = dict(results)

    with st.spinner("Writer Chain is drafting the report..."):
        research_combined = (
            f"SEARCH RESULTS:\n{results['search']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
        )
        try:
            results["writer"] = writer_chain.invoke(
                {
                    "topic": topic_val,
                    "research": research_combined,
                    "feedback": "",
                }
            )
        except Exception as e:
            stop_with_error(
                f"Writer failed while creating the report. Please try again. Details: {e}",
                e,
            )
        st.session_state.results = dict(results)

    with st.spinner("Critic Chain is reviewing the report..."):
        try:
            results["critic"] = critic_chain.invoke({"report": results["writer"]})
        except Exception as e:
            stop_with_error(
                f"Critic failed while reviewing the report. Please try again. Details: {e}",
                e,
            )
        st.session_state.results = dict(results)

    st.session_state.running = False
    st.session_state.done = True
    st.rerun()


results = st.session_state.results

if results:
    st.markdown('<div class="compact-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Results</div>', unsafe_allow_html=True)

    if "search" in results:
        with st.expander("Search results", expanded=False):
            raw_result("Search Agent Output", results["search"])

    if "reader" in results:
        with st.expander("Scraped content", expanded=False):
            raw_result("Reader Agent Output", results["reader"])

    if "writer" in results:
        st.markdown(
            """
<div class="result-box">
    <div class="label blue">Final Research Report</div>
</div>
""",
            unsafe_allow_html=True,
        )
        st.markdown(results["writer"])

        st.download_button(
            label="Download report",
            data=results["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    if "critic" in results:
        st.markdown(
            """
<div class="result-box">
    <div class="label green">Critic Feedback</div>
</div>
""",
            unsafe_allow_html=True,
        )
        st.markdown(results["critic"])


st.markdown(
    """
<div class="footer-note">
    DeepAgents Research / LangChain agents / Streamlit
</div>
""",
    unsafe_allow_html=True,
)
