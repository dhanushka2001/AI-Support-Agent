from openai import OpenAI

client = OpenAI()

MODEL = "gpt-4o-mini"


# SYSTEM_PROMPT = (
#     "You are an AI assistant answering questions based on the provided context from a document. "
#     "Use the context to infer and summarize the answer when possible. "
#     "If the context does not contain enough information to answer, say you do not know."
# )

SYSTEM_PROMPT = (
    "You are an AI assistant answering questions using the provided documents and chat as context "
    "Use the context as the primary source of information. "
    "If the question requires a simple transformation, calculation, or conversion "
    "(such as currency conversion or unit conversion) based on values found in the context, "
    "you may perform that transformation using general knowledge. "
    "If the context does not provide any relevant information at all, say you do not know."
)


def rewrite_query(question: str, previous_messages: list[dict]) -> str:
    if not previous_messages:
        return question

    # keep last 4 turns (2 from user, 2 from AI)
    last_n_messages = previous_messages[-4:]

    messages = [
        {
            "role": "system",
            #"content": (
            #    "Rewrite the user's latest query into a fully self-contained "
            #    "query using the prior messages as context. "
            #    "If the user's latest query is a question, your output MUST be a question. "
            #    "If the question is already self-contained, return it unchanged. "
            #    "Do NOT answer the user's question. "
            #    "Preserve the user's intent and phrasing, if they ask for a `brief` "
            #    "summary/explanation, your rewrite MUST include this. "
            #    "The prior messages are prodivded in the order they were sent, later messages "
            #    "may be more relevant."
            #)
            #"content": (
            #    "If the user's latest message is already self-contained, "
            #    "leave it unchanged. Otherwise: If the user's latest message is a question, "
            #    "rewrite the user's latest message into a single, fully self-contained "
            #    "QUESTION that can be used for semantic search over documents. You MUST "
            #    "PRESERVE the original intent and phrasing, e.g. if they ask for a `brief` "
            #    "summary/explanation, your rewrite must include this.\n\n"
            #    "Rules:\n"
            #    "- If the user's latest message is a question, your output MUST be a question.\n"
            #    "- Do NOT answer the question.\n"
            #    "- Do NOT explain, summarize, or add extra information.\n"
            #    "- Do NOT include phrases like 'Sure', 'This question asks', or any answers.\n"
            #    "- Preserve the user's intent, but add missing context from prior messages.\n"
            #    "- The prior messages are provided in the order they were sent.\n" 
            #    "- The later messages may be more relevant.\n"
            #    "- If the question is already self-contained, repeat it verbatim.\n"
            #    "- Output ONLY the rewritten question, nothing else."
            #)
            "content": (
                "If the user's last query asks for a simple transformation, summary, explanation, conversion, or calculation, do NOT answer their query, instead rewrite their query as is with provided context. "
                "Otherwise, rewrite the user's last query into a fully self-contained query using the prior messages as context. "
                "If the user asks a question, output a question. "
                "Do NOT answer the user's question."
            )
        }
    ]

    for message in last_n_messages:
        messages.append({
            "role": message["role"],
            "content": message.get("rewrite", message["content"])
        })

    # append the new question to the message history
    messages.append({
        "role": "user",
        "content": question
    })

    # generate the rewritten query with the message history context
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0,      # Zero-temperature rewriting
    )

    return response.choices[0].message.content.strip()


def generate_answer(question: str, previous_messages: list[dict], context_chunks: list[str]) -> str:
    if not context_chunks:
        return "I do not know based on the provided documents."

    context = "\n\n---\n\n".join(context_chunks)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "system",
            "content":f"""{context}"""
        }
    ]
    
    if previous_messages:
        last_n_messages = previous_messages[-4:]
        
        for message in last_n_messages:
            messages.append({
                "role": message["role"],
                "content": message.get("rewrite", message["content"])
            })

    # append the new question to the message history
    messages.append({
        "role": "user",
        "content": question
    })

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.2,  # lower = less creative, more factual
    )

    return response.choices[0].message.content

