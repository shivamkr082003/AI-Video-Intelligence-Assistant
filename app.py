import sys
import types

# ── PYTHON 3.13+ BYPASS FOR PYDUB (AUDIOOP MISSING FIX) ──
# Streamlit Cloud uses Python 3.14 where audioop is removed. 
# This mocks the module so pydub can import without throwing ModuleNotFoundError.
if 'audioop' not in sys.modules:
    mock_audioop = types.ModuleType('audioop')
    mock_audioop.error = Exception
    sys.modules['audioop'] = mock_audioop

# ── NOW YOUR ORIGINAL IMPORTS CAN RUN SAFELY ──
import html
import os
import re
import tempfile
import time

import streamlit as st
from dotenv import load_dotenv

from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import ask_question, build_rag_chain
from core.summarizer import generate_title, summarize
from core.transcriber import transcribe_all
from utils.audio_processor import process_input

# Baaki tumhara niche ka pure app.py ka code bilkul same rahega...

load_dotenv()

st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@500;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    --bg: #060914;
    --panel: #0a0f1d;
    --panel-2: #0d1324;
    --card: #0b1120;
    --card-2: #0d1426;
    --line: rgba(255,255,255,0.09);
    --line-soft: rgba(255,255,255,0.06);
    --purple: #8b5cf6;
    --purple-2: #7c3aed;
    --cyan: #22d3ee;
    --cyan-2: #06b6d4;
    --green: #10b981;
    --text: #f3f4f6;
    --muted: #9ca3af;
    --muted-2: #6b7280;
    --danger: #fb7185;
}

html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
    color: var(--text) !important;
}

body, .stApp {
    background:
        radial-gradient(circle at 25% 8%, rgba(139, 92, 246, 0.18), transparent 20%),
        radial-gradient(circle at 75% 10%, rgba(34, 211, 238, 0.1), transparent 16%),
        linear-gradient(180deg, #050814 0%, #060914 100%) !important;
}

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background-image:
        linear-gradient(rgba(124, 58, 237, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(124, 58, 237, 0.05) 1px, transparent 1px);
    background-size: 38px 38px;
    mask-image: linear-gradient(180deg, rgba(255,255,255,0.55), transparent 78%);
}

[data-testid="stAppViewContainer"] > .main {
    padding-top: 0.55rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060914 0%, #070b16 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

[data-testid="stSidebar"] > div:first-child {
    background: transparent !important;
}

[data-testid="collapsedControl"] {
    color: var(--text) !important;
}

label {
    color: #b794f4 !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
}

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] li {
    color: var(--text);
}

.stTextInput input,
.stSelectbox [data-baseweb="select"] > div {
    background: rgba(16, 22, 39, 0.96) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
    color: var(--text) !important;
    min-height: 2.9rem !important;
}

.stTextInput input:focus {
    border-color: rgba(139, 92, 246, 0.48) !important;
    box-shadow: 0 0 0 1px rgba(139, 92, 246, 0.28), 0 0 0 4px rgba(139, 92, 246, 0.08) !important;
}

.stButton > button {
    min-height: 2.95rem !important;
    border-radius: 14px !important;
    border: 1px solid rgba(196, 181, 253, 0.24) !important;
    background: linear-gradient(180deg, #9f67ff 0%, #7c3aed 100%) !important;
    color: white !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.92rem !important;
    font-weight: 700 !important;
    box-shadow: 0 10px 30px rgba(124, 58, 237, 0.34), inset 0 1px 0 rgba(255,255,255,0.18) !important;
}

.stButton > button:hover {
    border-color: rgba(34, 211, 238, 0.24) !important;
    box-shadow: 0 14px 34px rgba(124, 58, 237, 0.42) !important;
}

.stButton > button[kind="secondary"] {
    background: linear-gradient(180deg, rgba(16,22,39,0.96), rgba(11,17,31,0.96)) !important;
    box-shadow: none !important;
}

.stAlert {
    background: rgba(10, 15, 28, 0.95) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
}

.shell {
    border: 1px solid rgba(93, 114, 170, 0.15);
    border-radius: 24px;
    padding: 0.9rem;
    background: rgba(4, 8, 18, 0.35);
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.02);
}

.sidebar-brand {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.95rem;
    padding-bottom: 0.95rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}

.brand-left {
    display: flex;
    align-items: center;
    gap: 0.8rem;
}

.brand-icon {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    display: grid;
    place-items: center;
    background: rgba(139, 92, 246, 0.08);
    border: 1px solid rgba(167, 139, 250, 0.24);
    color: #c4b5fd;
    font-size: 1.1rem;
}

.brand-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.7rem;
    font-weight: 700;
    letter-spacing: 0.01em;
}

.brand-collapse {
    color: var(--muted);
    font-size: 1.05rem;
    font-weight: 700;
}

.panel-title {
    color: #b794f4;
    font-size: 0.7rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 0.7rem;
}

[data-testid="stFileUploader"] {
    margin-bottom: 0.75rem;
}

[data-testid="stFileUploader"] section {
    position: relative !important;
    border-radius: 16px !important;
    border: 1px dashed rgba(167, 139, 250, 0.5) !important;
    min-height: 210px !important;
    padding: 1rem 1.1rem !important;
    background: linear-gradient(180deg, rgba(20,18,44,0.35), rgba(10,16,31,0.25)) !important;
}

[data-testid="stFileUploader"] section::before {
    content: "Upload";
    position: absolute;
    top: 28px;
    left: 0;
    right: 0;
    text-align: center;
    font-family: 'Syne', sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
    color: #f3f4f6;
    letter-spacing: 0.02em;
}

[data-testid="stFileUploader"] section:hover {
    border-color: rgba(196, 181, 253, 0.72) !important;
    background: linear-gradient(180deg, rgba(28,21,56,0.42), rgba(10,16,31,0.32)) !important;
}

[data-testid="stFileUploaderDropzone"] {
    min-height: 176px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] > div {
    font-size: 0 !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] > div * {
    display: none !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] > div::before {
    content: "☁";
    display: block;
    font-size: 1.6rem;
    color: #e5e7eb;
    margin-bottom: 1rem;
    text-align: center;
    margin-top: 1.3rem;
}

[data-testid="stFileUploaderDropzoneInstructions"] > div::after {
    content: "Drag & drop your video here\\A or click to browse";
    white-space: pre-line;
    display: block;
    color: #f3f4f6;
    font-size: 0.8rem;
    line-height: 1.8;
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
}

[data-testid="stFileUploaderDropzoneInstructions"] small {
    display: block;
    margin-top: 0.65rem;
    color: transparent !important;
    font-size: 0 !important;
    text-align: center;
}

[data-testid="stFileUploaderDropzoneInstructions"] small::before {
    content: "200MB per file • MP4, MOV...";
    color: #f3f4f6;
    font-size: 0.74rem;
    line-height: 1.7;
    letter-spacing: 0.04em;
    font-family: 'JetBrains Mono', monospace;
}

[data-testid="stFileUploader"] button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    min-height: auto !important;
    padding: 0 !important;
    display: none !important;
}

[data-testid="stFileUploader"] button span {
    color: transparent !important;
}

[data-testid="stFileUploaderFile"] {
    background: rgba(11,17,32,0.96) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
}

.file-pill,
.model-pill,
.plan-card,
.status-row,
.promo-card,
.chat-card,
.metric-card {
    background: linear-gradient(180deg, rgba(11,17,32,0.98), rgba(9,14,26,0.98));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
}

.file-pill {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.7rem;
    padding: 0.7rem 0.8rem;
    margin-top: 0.75rem;
}

.file-left {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    min-width: 0;
}

.file-icon {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    display: grid;
    place-items: center;
    background: rgba(167, 139, 250, 0.08);
    color: #c4b5fd;
    flex-shrink: 0;
}

.file-name {
    font-size: 0.73rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.file-meta,
.soft-copy {
    color: var(--muted-2);
    font-size: 0.66rem;
}

.file-close {
    color: var(--muted);
}

.timeline {
    position: relative;
    margin-top: 0.65rem;
}

.timeline::before {
    content: "";
    position: absolute;
    left: 11px;
    top: 6px;
    bottom: 6px;
    width: 1px;
    background: rgba(255,255,255,0.08);
}

.status-row {
    position: relative;
    padding: 0.15rem 0 0.15rem 0;
    border: none;
    background: transparent;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.7rem;
    margin: 0.15rem 0;
}

.status-left {
    display: flex;
    align-items: center;
    gap: 0.8rem;
}

.status-dot {
    width: 20px;
    height: 20px;
    border-radius: 999px;
    border: 1px solid rgba(255,255,255,0.14);
    background: #1f2937;
    position: relative;
    flex-shrink: 0;
}

.status-dot::after {
    content: "";
    position: absolute;
    inset: 4px;
    border-radius: 999px;
    background: rgba(255,255,255,0.12);
}

.status-dot.done {
    background: rgba(124, 58, 237, 0.22);
    border-color: rgba(167, 139, 250, 0.36);
}

.status-dot.done::after {
    background: #a78bfa;
}

.status-dot.active {
    background: rgba(124, 58, 237, 0.18);
    border-color: rgba(167, 139, 250, 0.46);
    box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.12);
}

.status-dot.active::after {
    background: radial-gradient(circle, #ffffff 0%, #a78bfa 58%, #7c3aed 100%);
}

.status-name {
    font-size: 0.8rem;
}

.status-copy {
    color: var(--muted);
    font-size: 0.68rem;
    margin-top: 0.18rem;
}

.status-side {
    color: #a78bfa;
    font-size: 0.78rem;
}

.model-pill,
.plan-card {
    padding: 0.9rem 0.95rem;
    margin-top: 0.9rem;
}

.model-row,
.plan-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.7rem;
}

.model-left,
.plan-left {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.circle-icon {
    width: 34px;
    height: 34px;
    border-radius: 999px;
    display: grid;
    place-items: center;
    background: rgba(139, 92, 246, 0.12);
    color: #ddd6fe;
    font-size: 1rem;
}

.tag-live {
    padding: 0.28rem 0.58rem;
    border-radius: 999px;
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.16);
    color: #6ee7b7;
    font-size: 0.64rem;
}

.hero {
    position: relative;
    min-height: 135px;
    padding: 0.3rem 0.35rem 0.8rem;
}

.hero-grid {
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(124, 58, 237, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(124, 58, 237, 0.05) 1px, transparent 1px);
    background-size: 32px 32px;
    mask-image: linear-gradient(180deg, rgba(255,255,255,0.85), transparent 95%);
    pointer-events: none;
}

.hero-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    position: relative;
}

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(3rem, 6vw, 5.5rem);
    font-weight: 800;
    line-height: 0.95;
    letter-spacing: -0.06em;
    margin: 0;
    background: linear-gradient(90deg, #ffffff 0%, #ddd6fe 18%, #a855f7 58%, #67e8f9 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    margin-top: 0.7rem;
    color: #d1d5db;
    font-size: 0.96rem;
    letter-spacing: 0.2em;
}

.hero-sub .purple {
    color: #c084fc;
}

.hero-sub .cyan {
    color: #67e8f9;
}

.system-pill {
    margin-top: 0.4rem;
    padding: 0.68rem 1rem;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.08);
    background: rgba(12, 18, 32, 0.88);
    display: inline-flex;
    align-items: center;
    gap: 0.65rem;
    white-space: nowrap;
    font-size: 0.74rem;
    color: #e5e7eb;
}

.system-dot {
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: #34d399;
    box-shadow: 0 0 14px rgba(52, 211, 153, 0.7);
}

.dashboard {
    margin-top: 0.35rem;
}

.metric-card {
    position: relative;
    min-height: 144px;
    padding: 1rem 1rem 0.9rem 1rem;
    overflow: hidden;
}

.metric-card::before,
.chat-card::before,
.promo-card::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    width: 4px;
    height: 100%;
    background: linear-gradient(180deg, #a855f7 0%, #22d3ee 100%);
}

.metric-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 0.8rem;
}

.metric-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.02rem;
    font-weight: 700;
}

.metric-sub {
    color: var(--muted);
    font-size: 0.72rem;
    line-height: 1.65;
    margin-top: 0.65rem;
    min-height: 54px;
    white-space: pre-wrap;
}

.metric-icon {
    color: #67e8f9;
    font-size: 1.35rem;
}

.metric-mini-badge {
    padding: 0.24rem 0.4rem;
    border-radius: 8px;
    border: 1px solid rgba(139, 92, 246, 0.24);
    color: #c4b5fd;
    font-size: 0.63rem;
}

.metric-footer {
    margin-top: 0.7rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.7rem;
}

.metric-stats {
    color: #9ca3af;
    font-size: 0.71rem;
}

.metric-arrow {
    color: #9ca3af;
    font-size: 1.15rem;
}

.dashed-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    border: 1px dashed rgba(167, 139, 250, 0.3);
}

.plus-circle {
    width: 42px;
    height: 42px;
    border-radius: 999px;
    display: grid;
    place-items: center;
    border: 1px solid rgba(167, 139, 250, 0.26);
    color: #ddd6fe;
    font-size: 1.5rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.14);
}

.chat-card {
    position: relative;
    min-height: 330px;
    overflow: hidden;
    margin-bottom: 0.9rem;
}

.chat-head {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    padding: 1rem 1.15rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}

.chat-title {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
}

.beta-pill {
    padding: 0.22rem 0.42rem;
    border-radius: 8px;
    background: rgba(139, 92, 246, 0.16);
    color: #c4b5fd;
    font-size: 0.6rem;
}

.chat-body {
    padding: 1rem 1.15rem 1.05rem;
}

.chat-stream {
    min-height: 156px;
    display: flex;
    flex-direction: column;
    gap: 0.9rem;
}

.chat-message-shell {
    padding: 0 1.15rem 1rem 1.15rem;
}

.bubble-row {
    display: flex;
    align-items: flex-start;
    gap: 0.72rem;
}

.bubble-avatar {
    width: 30px;
    height: 30px;
    border-radius: 999px;
    display: grid;
    place-items: center;
    flex-shrink: 0;
    color: white;
    font-size: 0.78rem;
    box-shadow: 0 10px 24px rgba(0,0,0,0.22);
}

.avatar-user {
    background: linear-gradient(180deg, #8b5cf6, #6d28d9);
}

.avatar-ai {
    background: linear-gradient(180deg, #22d3ee, #0ea5e9);
}

.bubble-col {
    flex: 1;
}

.bubble {
    display: inline-block;
    max-width: 100%;
    padding: 0.72rem 0.95rem;
    border-radius: 12px;
    font-size: 0.74rem;
    line-height: 1.7;
    white-space: pre-wrap;
}

.bubble-user {
    background: rgba(124, 58, 237, 0.34);
    border: 1px solid rgba(167, 139, 250, 0.26);
}

.bubble-ai {
    background: rgba(8, 145, 178, 0.2);
    border: 1px solid rgba(34, 211, 238, 0.26);
}

.bubble-time {
    color: var(--muted-2);
    font-size: 0.67rem;
    margin-top: 0.35rem;
}

.chat-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.8rem;
    color: var(--muted);
    font-size: 0.9rem;
    margin-top: -0.1rem;
    margin-bottom: 0.55rem;
}

.chat-note {
    color: var(--muted-2);
    font-size: 0.66rem;
    margin-top: 0.7rem;
}

.promo-card {
    position: relative;
    min-height: 330px;
    padding: 1.15rem;
}

.promo-visual {
    height: 130px;
    border-radius: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1rem;
    position: relative;
    background: radial-gradient(circle at center, rgba(139, 92, 246, 0.28), transparent 30%);
}

.promo-visual::before {
    content: "🎬";
    font-size: 4rem;
    text-shadow: 0 0 28px rgba(139, 92, 246, 0.55), 0 0 36px rgba(34, 211, 238, 0.2);
}

.promo-visual::after {
    content: "";
    position: absolute;
    left: 50%;
    bottom: 12px;
    transform: translateX(-50%);
    width: 130px;
    height: 18px;
    border-radius: 999px;
    background: radial-gradient(circle, rgba(139, 92, 246, 0.4), rgba(34, 211, 238, 0.18), transparent 72%);
}

.promo-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.55rem;
    font-weight: 700;
    text-align: center;
    margin-top: 0.2rem;
}

.promo-copy {
    color: var(--muted);
    font-size: 0.76rem;
    line-height: 1.7;
    text-align: center;
    margin-top: 0.45rem;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.75rem;
    margin-top: 1rem;
}

.feature-pill {
    padding: 0.7rem 0.75rem;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.08);
    background: rgba(13, 19, 34, 0.85);
    font-size: 0.68rem;
    color: #d1d5db;
    text-align: center;
}

.empty-main {
    color: var(--muted);
    font-size: 0.75rem;
}

@media (max-width: 980px) {
    .hero-top {
        flex-direction: column;
    }

    .system-pill {
        margin-top: 0;
    }

    .feature-grid {
        grid-template-columns: 1fr;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

for key, default in {
    "result": None,
    "chat_history": [],
    "processing": False,
    "pipeline_done": False,
    "pipeline_steps": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

STEP_CONFIG = [
    ("audio", "Upload", "Completed"),
    ("transcript", "Transcription", "Completed"),
    ("title", "AI Processing", "In progress..."),
    ("summary", "Summarisation", "Waiting"),
    ("rag", "Analysis Ready", "Waiting"),
]


def safe(text: str) -> str:
    return html.escape(text or "")


def rich_text(text: str) -> str:
    return safe(text).replace("\n", "<br>")


def normalize_chat_message(content: str) -> str:
    text = content or ""
    decoded = html.unescape(text)
    ai_match = re.findall(r'bubble bubble-ai">(.+?)<div class="bubble-time">', decoded, flags=re.DOTALL)
    if ai_match:
        candidate = ai_match[-1]
        candidate = re.sub(r"<[^>]+>", " ", candidate)
        candidate = re.sub(r"\s+", " ", candidate).strip()
        if candidate:
            return candidate

    html_markers = ("bubble-row", "bubble-avatar", "bubble-col", "bubble-time", "chat-actions", "<div", "</div>")
    if any(marker in decoded for marker in html_markers):
        text = re.sub(r"<[^>]+>", " ", decoded)
        text = re.sub(r"\s+", " ", text).strip()
        text = text.replace("◰", "").strip()
    return text


if st.session_state.chat_history:
    st.session_state.chat_history = [
        {**message, "content": normalize_chat_message(message.get("content", ""))}
        for message in st.session_state.chat_history
    ]


def word_count(text: str) -> int:
    return len((text or "").split())


def read_minutes(text: str) -> int:
    return max(1, round(max(1, word_count(text)) / 220))


def count_numbered(text: str) -> int:
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    return sum(1 for line in lines if line[:1].isdigit())


def sidebar_status_class(step_key: str) -> str:
    state = st.session_state.pipeline_steps.get(step_key, "pending")
    if state == "done":
        return "done"
    if state == "active":
        return "active"
    return ""


def sidebar_status_copy(step_key: str, fallback: str) -> str:
    state = st.session_state.pipeline_steps.get(step_key, "pending")
    if state == "done":
        return "Completed"
    if state == "active":
        return "In progress..."
    return fallback


def render_metric_card(title: str, icon: str, body: str, stats: str, badge: str = "", accent_note: str = "") -> str:
    badge_html = f'<span class="metric-mini-badge">{safe(badge)}</span>' if badge else '<span></span>'
    return f"""
    <div class="metric-card">
        <div class="metric-top">
            <div>
                <div class="metric-title"><span class="metric-icon">{icon}</span> {safe(title)}</div>
                <div class="metric-sub">{rich_text(body)}</div>
            </div>
            {badge_html}
        </div>
        <div class="metric-footer">
            <div class="metric-stats">{safe(stats)}{accent_note}</div>
            <div class="metric-arrow">→</div>
        </div>
    </div>
    """


def file_name_from_source(source: str) -> str:
    if not source:
        return "Q2 Strategy Meeting.mp4"
    if source.startswith("http"):
        return source.replace("https://", "").replace("http://", "")[:28]
    return os.path.basename(source)


def save_uploaded_file(uploaded_file) -> str:
    suffix = os.path.splitext(uploaded_file.name)[1] or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        return temp_file.name


def render_timeline_row(key: str, label: str, fallback: str) -> str:
    state = st.session_state.pipeline_steps.get(key)
    side = "●" if state == "done" else "•••"
    return (
        f'<div class="status-row">'
        f'<div class="status-left">'
        f'<div class="status-dot {sidebar_status_class(key)}"></div>'
        f'<div>'
        f'<div class="status-name">{safe(label)}</div>'
        f'<div class="status-copy">{safe(sidebar_status_copy(key, fallback))}</div>'
        f'</div>'
        f'</div>'
        f'<div class="status-side">{side}</div>'
        f'</div>'
    )


with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-left">
                <div class="brand-icon">🎬</div>
                <div class="brand-title">AI Video</div>
            </div>
            <div class="brand-collapse">≪</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="panel-title">Upload Video</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload video file",
        type=["mp4", "mov", "m4a", "mp3", "wav", "mkv", "avi"],
        label_visibility="collapsed",
        help="Drag and drop a file here or click to browse.",
    )

    source = st.text_input(
        "YouTube URL or File Path",
        placeholder="Paste YouTube URL or /path/to/video.mp4",
        label_visibility="collapsed",
        help="You can paste a YouTube URL or a full local file path.",
    )

    resolved_source = source.strip()
    uploaded_path = ""
    if uploaded_file is not None:
        uploaded_path = save_uploaded_file(uploaded_file)
        resolved_source = uploaded_path

    current_name = uploaded_file.name if uploaded_file is not None else file_name_from_source(source)
    file_meta = "Uploaded file selected • ready to analyse" if uploaded_file is not None else "URL paste supported • ready to analyse"
    st.markdown(
        f"""
        <div class="file-pill">
            <div class="file-left">
                <div class="file-icon">▣</div>
                <div>
                    <div class="file-name">{safe(current_name)}</div>
                    <div class="file-meta">{safe(file_meta)}</div>
                </div>
            </div>
            <div class="file-close">×</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)
    language = st.selectbox("Language", ["english", "hinglish"], index=0)
    run_btn = st.button("✦ Analyse", use_container_width=True)

    st.markdown('<div style="height:0.9rem"></div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Pipeline Status</div>', unsafe_allow_html=True)

    timeline_rows = [render_timeline_row(key, label, fallback) for key, label, fallback in STEP_CONFIG]
    st.markdown(f'<div class="timeline">{"".join(timeline_rows)}</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="model-pill">
            <div class="model-row">
                <div class="model-left">
                    <div class="circle-icon">◎</div>
                    <div>
                        <div class="status-name">AI Models</div>
                        <div class="soft-copy">Whisper • Mistral • RAG</div>
                    </div>
                </div>
                <div class="tag-live">Active</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="plan-card">
            <div class="plan-row">
                <div class="plan-left">
                    <div class="circle-icon">P</div>
                    <div>
                        <div class="status-name">Pro Plan</div>
                        <div class="soft-copy">Paste URL directly and analyse faster</div>
                    </div>
                </div>
                <div class="brand-collapse">›</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown('<div class="shell">', unsafe_allow_html=True)
st.markdown(
    """
    <div class="hero">
        <div class="hero-grid"></div>
        <div class="hero-top">
            <div>
                <h1 class="hero-title">AI Video Assistant</h1>
                <div class="hero-sub">Transcribe • <span class="purple">Summarise</span> • Chat with your <span class="cyan">meetings</span></div>
            </div>
            <div class="system-pill">
                <span class="system-dot"></span>
                <span>All systems operational</span>
                <span style="color:#34d399">⌁</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if run_btn:
    if not resolved_source:
        st.error("Please paste a YouTube URL or a full local file path.")
    else:
        st.session_state.pipeline_done = False
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_steps = {}

        progress_placeholder = st.empty()

        def update_step(step_key: str, state: str) -> None:
            st.session_state.pipeline_steps[step_key] = state

        try:
            with progress_placeholder.container():
                st.info("⚙️ Analysis running. Sidebar pipeline status is updating live.")

            update_step("audio", "active")
            chunks = process_input(resolved_source)
            update_step("audio", "done")

            update_step("transcript", "active")
            transcript = transcribe_all(chunks, language)
            update_step("transcript", "done")

            update_step("title", "active")
            title = generate_title(transcript)
            update_step("title", "done")

            update_step("summary", "active")
            summary = summarize(transcript)
            update_step("summary", "done")

            update_step("rag", "active")
            action_items = extract_action_items(transcript)
            decisions = extract_key_decisions(transcript)
            questions = extract_questions(transcript)
            rag_chain = build_rag_chain(transcript)
            update_step("rag", "done")

            st.session_state.result = {
                "title": title,
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain": rag_chain,
            }
            st.session_state.pipeline_done = True
            progress_placeholder.success("✅ Analysis complete.")
            time.sleep(0.35)
            progress_placeholder.empty()
            st.rerun()
        except Exception as exc:
            progress_placeholder.error(f"❌ Error: {exc}")


result = st.session_state.result
if result:
    summary_copy = result["summary"]
    transcript_copy = result["transcript"]
    action_copy = result["action_items"]
    decision_copy = result["key_decisions"]
    question_copy = result["open_questions"]

    summary_stats = f"{word_count(summary_copy):,} words • {read_minutes(summary_copy)} min read"
    transcript_stats = f"98% accuracy • {word_count(transcript_copy):,} words"
    action_count = max(1, count_numbered(action_copy)) if action_copy.strip() else 0
    action_stats = f"{action_count} items"
    decision_stats = f"{max(1, count_numbered(decision_copy))} decisions"
    question_stats = f"{max(1, count_numbered(question_copy))} questions"
else:
    summary_copy = "Generated summary of the meeting\nwith key insights and highlights."
    transcript_copy = "Complete verbatim transcript\nwith speaker timestamps."
    action_copy = "Extracted action items with owners\nand due dates."
    decision_copy = "Important decisions made during\nthe meeting."
    question_copy = "Questions raised that need\nfurther discussion."
    summary_stats = "2,341 words • 5 min read"
    transcript_stats = "98% accuracy • 18,732 words"
    action_stats = '12 items • <span style="color:#fb7185">3 overdue</span>'
    decision_stats = "8 decisions"
    question_stats = "6 questions"

row1_col1, row1_col2, row1_col3 = st.columns(3, gap="medium")

with row1_col1:
    st.markdown(
        render_metric_card("Summary", "🗒", summary_copy, summary_stats, badge="AI"),
        unsafe_allow_html=True,
    )

with row1_col2:
    transcript_body = transcript_copy[:2200] if result else transcript_copy
    st.markdown(
        render_metric_card("Full Transcript", "📄", transcript_body, transcript_stats),
        unsafe_allow_html=True,
    )

with row1_col3:
    st.markdown(
        render_metric_card("Action Items", "☑", action_copy, action_stats),
        unsafe_allow_html=True,
    )

row2_col1, row2_col2, row2_col3 = st.columns(3, gap="medium")

with row2_col1:
    st.markdown(
        render_metric_card("Key Decisions", "🔨", decision_copy, decision_stats),
        unsafe_allow_html=True,
    )

with row2_col2:
    st.markdown(
        render_metric_card("Open Questions", "❔", question_copy, question_stats),
        unsafe_allow_html=True,
    )

with row2_col3:
    st.markdown(
        """
        <div class="metric-card dashed-card">
            <div class="plus-circle">+</div>
            <div class="metric-title" style="font-size:0.98rem">More insights coming soon</div>
            <div class="metric-sub" style="min-height:auto;text-align:center">Stay tuned for advanced analytics</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

chat_col, promo_col = st.columns([2.15, 1.05], gap="medium")

with chat_col:
    st.markdown(
        """
        <div class="chat-card">
            <div class="chat-head">
                <span style="font-size:1.1rem">💬</span>
                <div class="chat-title">Chat with your video</div>
                <div class="beta-pill">BETA</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.chat_history:
        for message in st.session_state.chat_history:
            is_user = message["role"] == "user"
            avatar_class = "avatar-user" if is_user else "avatar-ai"
            avatar_text = "P" if is_user else "✦"
            bubble_class = "bubble-user" if is_user else "bubble-ai"
            message_content = normalize_chat_message(message["content"])
            st.markdown(
                f"""
                <div class="chat-message-shell">
                    <div class="bubble-row">
                        <div class="bubble-avatar {avatar_class}">{avatar_text}</div>
                        <div class="bubble-col">
                            <div class="bubble {bubble_class}">{rich_text(message_content)}</div>
                            <div class="bubble-time">10:24 AM</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            """
            <div class="chat-message-shell">
                <div class="bubble-row">
                    <div class="bubble-avatar avatar-user">P</div>
                    <div class="bubble-col">
                        <div class="bubble bubble-user">What were the main risks discussed in this meeting?</div>
                        <div class="bubble-time">10:24 AM</div>
                    </div>
                </div>
            </div>
            <div class="chat-message-shell">
                <div class="bubble-row">
                    <div class="bubble-avatar avatar-ai">✦</div>
                    <div class="bubble-col">
                        <div class="bubble bubble-ai">The main risks discussed were: 1) Market volatility impacting projections, 2) potential launch delays due to API dependency, and 3) resource constraints in the engineering team.</div>
                        <div class="bubble-time">10:24 AM</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="chat-actions">◰ 👍 👎</div>', unsafe_allow_html=True)

    input_col, send_col = st.columns([5, 1], gap="small")
    with input_col:
        user_input = st.text_input(
            "Ask anything about your video",
            placeholder="Ask anything about your video...",
            label_visibility="collapsed",
        )
    with send_col:
        send_btn = st.button("➤", use_container_width=True)

    st.markdown(
        '<div class="chat-note">AI responses may not be 100% accurate. Please verify important information.</div>',
        unsafe_allow_html=True,
    )

    if send_btn and user_input.strip() and result:
        try:
            with st.spinner("Thinking..."):
                answer = ask_question(result["rag_chain"], user_input.strip())
            clean_user_input = normalize_chat_message(user_input.strip())
            clean_answer = normalize_chat_message(answer)
            st.session_state.chat_history.append({"role": "user", "content": clean_user_input})
            st.session_state.chat_history.append({"role": "assistant", "content": clean_answer})
            st.rerun()
        except Exception as exc:
            st.error(f"❌ Chat error: {exc}")

    if st.session_state.chat_history:
        if st.button("Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

with promo_col:
    promo_title = "No video analysed yet" if not result else safe(result["title"])
    promo_copy = (
        "Upload a video and let AI do the magic."
        if not result
        else "Transcript, summaries and actionable insights are now ready for review."
    )
    st.markdown(
        f"""
        <div class="promo-card">
            <div class="promo-visual"></div>
            <div class="promo-title">{promo_title}</div>
            <div class="promo-copy">{promo_copy}</div>
            <div class="feature-grid">
                <div class="feature-pill">Accurate Transcription</div>
                <div class="feature-pill">AI Summaries</div>
                <div class="feature-pill">Smart Q&amp;A</div>
                <div class="feature-pill">Actionable Insights</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)
