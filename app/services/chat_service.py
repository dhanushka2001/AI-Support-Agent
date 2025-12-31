from openai import OpenAI

client = OpenAI()

MODEL = "gpt-4o-mini"


# SYSTEM_PROMPT = (
#     "You are an AI assistant answering questions based on the provided context from a document. "
#     "Use the context to infer and summarize the answer when possible. "
#     "If the context does not contain enough information to answer, say you do not know."
# )

SYSTEM_PROMPT = (
    "You are an AI assistant answering questions using the provided document context. "
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
            "content": (
                "Rewrite the user's latest question into a fully self-contained "
                "question using the prior messages as context. "
                "If the question is already self-contained, return it unchanged."
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


def generate_answer(question: str, context_chunks: list[str]) -> str:
    if not context_chunks:
        return "I do not know based on the provided documents."

    context = "\n\n---\n\n".join(context_chunks)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""
Context:
{context}

Question:
{question}
"""
        },
    ]


    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.2,  # lower = less creative, more factual
    )

    return response.choices[0].message.content

