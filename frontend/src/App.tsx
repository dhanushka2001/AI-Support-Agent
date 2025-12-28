import { useState } from "react";

type Message = {
  role: "user" | "assistant";
  content: string;
};

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!question.trim()) return;

    const userMessage: Message = { role: "user", content: question };
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setLoading(true);

    const body: any = {
      question,
      top_k: 5,
    };

    if (conversationId) {
      body.conversation_id = conversationId;
    }

    const res = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const data = await res.json();

    setConversationId(data.conversation_id);

    const assistantMessage: Message = {
      role: "assistant",
      content: data.answer,
    };

    setMessages((prev) => [...prev, assistantMessage]);
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 600, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h2>Chatbot</h2>

      <div style={{ border: "1px solid #ccc", padding: 12, minHeight: 300 }}>
        {messages.map((m, i) => (
          <div key={i} style={{ marginBottom: 10 }}>
            <strong>{m.role === "user" ? "You" : "AI"}:</strong>
            <div>{m.content}</div>
          </div>
        ))}
        {loading && <div>Thinking...</div>}
      </div>

      <div style={{ display: "flex", marginTop: 10 }}>
        <input
          style={{ flex: 1, padding: 8 }}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button onClick={sendMessage} style={{ marginLeft: 8 }}>
          Send
        </button>
      </div>
    </div>
  );
}

export default App;

