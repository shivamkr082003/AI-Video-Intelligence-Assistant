#Actionableitems , decision , questions 

from langchain_core.prompts import ChatPromptTemplate
from core.llm import invoke_with_fallback



def build_chain(system_prompt : str):
    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human","{text}"),
    ])

def extract_action_items(transcript:str)->str:
    prompt = build_chain(
         "You are an expert meeting analyst. From the meeting transcript, "
        "extract all action items. For each provide:\n"
        "- Task description\n"
        "- Owner (who is responsible)\n"
        "- Deadline (if mentioned, else write 'Not specified')\n\n"
        "Format as a numbered list. If none found say 'No action items found.'"
    )

    return invoke_with_fallback(prompt, {"text": transcript}, temperature=0.2)


def extract_key_decisions(transcript: str) -> str:
    prompt = build_chain(
        "You are an expert meeting analyst. From the meeting transcript, "
        "extract all key decisions made. Format as a numbered list. "
        "If none found say 'No key decisions found.'"
    )
    return invoke_with_fallback(prompt, {"text": transcript}, temperature=0.2)


def extract_questions(transcript: str) -> str:
    prompt = build_chain(
        "From the meeting transcript, extract all unresolved questions "
        "or topics needing follow-up. Format as a numbered list. "
        "If none found say 'No open questions found.'"
    )
    return invoke_with_fallback(prompt, {"text": transcript}, temperature=0.2)
