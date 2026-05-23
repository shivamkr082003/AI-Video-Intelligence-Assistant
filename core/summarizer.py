from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from core.llm import invoke_with_fallback


def split_transcript(transcript: str) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 3000,
        chunk_overlap = 200
    )

    return splitter.split_text(transcript)

def summarize(transcript : str) -> str:
    map_prompt = ChatPromptTemplate.from_messages(
        [
        ("system", "Summarize this portion of a meeting transcript concisely."),
        ("human", "{text}"),
    ]
    )

    chunks = split_transcript(transcript)

    chunk_summaries = [
        invoke_with_fallback(map_prompt, {"text": chunk}, temperature=0.3)
        for chunk in chunks
    ]

    combined = "\n\n".join(chunk_summaries)

    combined_prompt = ChatPromptTemplate.from_messages(
        [
        (
            "system",
            "You are an expert meeting summarizer. Combine these partial summaries "
            "into one final professional meeting summary in bullet points.",
        ),
        ("human", "{text}"),
    ]
    )

    return invoke_with_fallback(combined_prompt, {"text": combined}, temperature=0.3)

def generate_title(transcipt : str) -> str:
    title_prompt = ChatPromptTemplate.from_messages([
             (
                "system",
                "Based on the meeting transcript, generate a short professional meeting title "
                "(max 8 words). Only return the title, nothing else.",
            ),
            ("human", "{text}"),
        ])

    return invoke_with_fallback(title_prompt, {"text": transcipt[:2000]}, temperature=0.3)


