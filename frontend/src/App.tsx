import { useState, useEffect, useRef } from "react";

type Message = {
  role: "user" | "assistant";
  content: string;
};

type Conversation = {
  conversation_id: string;
  title?: string;
};

type Pdf = {
  file_id: string;
  original_filename: string;
  status: "processing" | "UPLOADED" | "EXTRACTED" | "failed";
};


function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [pdfs, setPdfs] = useState<Pdf[]>([]);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  
  useEffect(() => {
    const loadLatestConversation = async () => {
      try {
        const res = await fetch("http://localhost:8000/chat/latest");
        const data = await res.json();
  
	if (!data.messages) {
	  console.error("No messages in conversation response", data);
	  return;
	}
        if (data.conversation_id && data.messages) {
          setConversationId(data.conversation_id);
          setMessages(data.messages);
        }

      } catch (err) {
        console.error("Failed to load latest conversation", err);
      }
    };
  
    loadLatestConversation();
  }, []);

  
  useEffect(() => {
    const loadConversations = async () => {
      const res = await fetch("http://localhost:8000/chat/conversations");
      const data = await res.json();
      setConversations(data);
    };
  
    loadConversations();
  }, []);

  
  useEffect(() => {
    fetch("http://localhost:8000/pdf/list")
      .then(res => res.json())
      .then(setPdfs);
  }, []);

  
  const startNewChat = () => {
    setConversationId(null);
    setMessages([]);
  };

  const loadConversation = async (id: string) => {
    setConversationId(id);
    setMessages([]);

    const res = await fetch(`http://localhost:8000/chat/${id}`);
    const data = await res.json();
  
    setMessages(data.messages);
  };


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

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
  
    const formData = new FormData();
    formData.append("file", file);
  
    setUploading(true);
  
    const res = await fetch("http://localhost:8000/pdf/upload", {
      method: "POST",
      body: formData,
    });
  
    if (res.ok) {
      const pdf = await res.json();
      setPdfs(prev => [...prev, pdf]);
    } else {
      const err = await res.json();
      alert(err?.detail?.error ?? "Upload failed");
    }

    if (fileInputRef.current) {
    	fileInputRef.current.value = "";
    }
  
    setUploading(false);
  };
  
  const deletePdf = async (fileId: string) => {
    if (!confirm("Delete this PDF?")) return;
  
    await fetch(`http://localhost:8000/pdf/${fileId}`, {
	method: "DELETE",
    });
  
    setPdfs(prev => prev.filter(p => p.file_id !== fileId));
  };


  return (
    <div style={{ display: "flex", height: "100vh", fontFamily: "sans-serif" }}>
      
      {/*** Sidebar ***/}
      <div
        style={{
          width: 220,
          borderRight: "1px solid #ddd",
          padding: 10,
          overflowY: "auto",
        }}
      >
      	{/* New chat button */}
        <button
          onClick={startNewChat}
          style={{ width: "100%", marginBottom: 10 }}
        >
          + New Chat
        </button>
  
	{/* Conversations list */}
        {conversations.map((c) => (
          <div
            key={c.conversation_id}
            onClick={() => loadConversation(c.conversation_id)}
            style={{
              padding: "6px 8px",
              cursor: "pointer",
              background:
                c.conversation_id === conversationId ? "#aaa" : "transparent",
            }}
          >
            {c.title || "New Chat"}
          </div>
        ))}


	{/* Documents */}
	<input
	  type="file"
	  accept="application/pdf"
	  hidden
	  ref={fileInputRef}
	  onChange={handleUpload}
	/>
	
	{/* Upload PDF button */}
	<button 
	  onClick={() => fileInputRef.current?.click()}
          style={{ width: "100%", marginBottom: 10 }}
	>
	  + Upload PDF
	</button>
       	
	{/* PDF list */}
	{pdfs.map(pdf => (
	  <div 
	      key={pdf.file_id}
	      style={{
		display: "flex",
		alignItems: "flex-start",
		gap: 6,
		marginBottom: 6,
	      }}
	  >
	    
	    {/* Emoji column */}
	    <span style={{ flexShrink: 0 }}>📄</span>

	    {/* Filename column */}
	    <span
		style={{
		    wordBreak: "break-word",
		    overflowWrap: "anywhere",
		    whiteSpace: "normal",
		    flex: 1,
		    lineHeight: "1.3",
		}}
	    >
	      {pdf.original_filename}
	      {pdf.status === "processing" && " (processing)"}
	    </span>

	    {/* Delete button */}
	    <button
	      onClick={() => deletePdf(pdf.file_id)}
	      style={{
		color: "red",
		background: "transparent",
		fontSize: 12,
		padding: "2px 4px",
		lineHeight: 1,
		marginLeft: "auto" }}
	    >
	      ✕
	    </button>
	  </div>
	))}
      </div>
  

      {/*** Chat panel ***/}
      <div
        style={{
          flex: 1,
          maxWidth: 700,
          margin: "40px auto",
          padding: "0 20px",
        }}
      >
        <h2>Chatbot</h2>
  
        <div
          style={{
            border: "1px solid #ccc",
            padding: 12,
	    width: 650,
            height: 600,
            overflowY: "auto",
          }}
        >
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
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            style={{ marginLeft: 8 }}
            disabled={loading}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );


}

export default App;

