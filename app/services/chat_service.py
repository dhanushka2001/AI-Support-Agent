from openai import OpenAI

client = OpenAI()

MODEL = "gpt-4o-mini"

# SYSTEM_PROMPT = (
#     "You are an AI assistant that answers questions using ONLY the provided context. "
#     "If the answer is not contained in the context, say you do not know."
# )

SYSTEM_PROMPT = (
    "You are an AI assistant answering questions based on the provided context from a document. "
    "Use the context to infer and summarize the answer when possible. "
    "If the context does not contain enough information to answer, say you do not know."
)

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

