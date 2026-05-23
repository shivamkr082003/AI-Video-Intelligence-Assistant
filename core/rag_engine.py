from langchain_core.prompts import ChatPromptTemplate
from core.vector_store import build_vector_store, load_vector_store, get_retriever
from core.llm import invoke_with_fallback

def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])

def build_rag_chain(transcript:str):

    vector_store = build_vector_store(transcript)

    retriever = get_retriever(vector_store, k = 4)

    prompt = ChatPromptTemplate.from_messages(

        [(
            "system",
            """You are an expert meeting assistant. Answer the user's question 
based ONLY on the meeting transcript context provided below.

If the answer is not found in the context, say: 
"I could not find this information in the meeting transcript."

Always be concise and precise. If quoting someone, mention it clearly.

Context from meeting transcript:
{context}""",
        ),
        ("human", "{question}"),
    ]
    )

    return {"retriever": retriever, "prompt": prompt}


def load_rag_chain():
    vector_store = load_vector_store()
    retriver = get_retriever(vector_store)

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert meeting assistant. Answer the user's question 
based ONLY on the meeting transcript context provided below.

If the answer is not found in the context, say: 
"I could not find this information in the meeting transcript."

Always be concise and precise. If quoting someone, mention it clearly.

Context from meeting transcript:
{context}""",
        ),
        ("human", "{question}"),
    ])

    return {"retriever": retriver, "prompt": prompt}


def ask_question(rag_chain, question:str) -> str:
    print(f"Question : {question}")
    docs = rag_chain["retriever"].invoke(question)
    context = format_docs(docs)
    answer = invoke_with_fallback(
        rag_chain["prompt"],
        {"context": context, "question": question},
        temperature=0.3,
    )
    print(f"answer :{answer}")
    return answer
