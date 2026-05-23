# 🎥 AI Video Assistant & Meeting RAG Pipeline

An intelligent, end-to-end AI pipeline that processes local videos or YouTube URLs to transcribe, summarize, and extract key insights, featuring a modern **Streamlit Web UI** and a context-aware **RAG Chat** assistant.

---

## ✨ Features

*   **🎙️ Smart Audio Processing:** Automatically splits and processes audio from YouTube links or local video files.
*   **🗣️ Bilingual Support:** Accurate transcriptions for both **English** and **Hinglish** languages.
*   **📊 Structured Extraction:** Automatically extracts:
    *   Catchy & Relevant **Title**
    *   Executive **Summary**
    *   ✅ **Action Items** (Who needs to do what)
    *   🔑 **Key Decisions** made during the meeting
    *   ❓ **Open Questions** left unanswered
*   **💬 Interactive Chat (RAG):** Context-aware Q&A system that lets you query the video transcript directly.
*   **🎨 Streamlit Web UI:** A clean, user-friendly interface to run the pipeline and chat visually instead of the terminal.

---

## 🏗️ Project Architecture

Here is how the data flows through the pipeline:

```text
[YouTube URL / Local File] 
           │
           ▼
   (audio_processor) ──> Splits audio into Chunks
           │
           ▼
     (transcriber)   ──> Generates Raw Text (English/Hinglish)
           │
     ┌─────┴────────────────────────────────────────┐
     ▼                                              ▼
(LLM Extractors)                              (RAG Engine)
 ├── Title & Summary                           └── Build RAG Chain
 ├── Action Items                                   │
 ├── Key Decisions                                  ▼
 └── Open Questions                       [Streamlit Web UI / Chat]

🚀 Getting Started
1. Prerequisites
Make sure you have Python 3.8+ installed. This project uses uv for blazing-fast dependency management.

2. Installation & Setup
Instead of traditional pip, we use uv to sync and install the environment instantly

# Clone the repository
git clone :[https://github.com/shivamkr082003/AI-Video-Intelligence-Assistant.git]

cd ai-video-assistant

# Install uv (if you haven't already)
pip install uv

# Create a virtual environment and install all dependencies
uv venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
uv pip install -r requirements.txt

3. Environment Setup
Create a .env file in the root directory of your project and add your API keys:

💻 Usage
Launching the Streamlit Web App
Run the following command to start the interactive web interface:

Bash
uv run streamlit run app.py

How it works in CLI:
Input: The script will ask for a YouTube URL or a local file path.

Language: Select english or hinglish.

Processing: The pipeline runs transcription and AI extraction.

Insights: It prints the Title, Summary, Action Items, Decisions, and Questions on the screen.

Chat Mode: The script enters a loop allowing you to ask specific questions about the video (Type exit to quit).

📁 File Structure
Plaintext
├── core/
│   ├── transcriber.py       # Audio-to-text logic
│   ├── summarizer.py        # Title & Summary generation
│   ├── extractor.py         # Action items, decisions & questions extraction
│   └── rag_engine.py        # Vector embedding and RAG chain setup
├── utils/
│   └── audio_processor.py   # Downloading & chunking audio
├── .env                     # API Keys & Environment variables (Hidden)
├── app.py                   # Streamlit Web UI Frontend
├── main.py                  # CLI Entry point / Pipeline core
└── README.md                # Project documentation


🛠️ Tech Stack
Package Manager: uv (Astral)

Frontend UI: Streamlit

Language: Python 3.x

AI/RAG Framework: LangChain / LlamaIndex

Environment Management: python-dotenv