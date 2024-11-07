import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./QueryForm.css";

function QueryForm() {
  const [documentId, setDocumentId] = useState("");
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [messages, setMessages] = useState([]);
  const navigate = useNavigate();

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get(
          "http://localhost:8000/api/v1/documents?skip=0&limit=10",
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        console.log("Fetched documents:", response.data);
        setDocuments(response.data || []);
      } catch (error) {
        console.error("Error fetching documents", error);
        setDocuments([]);
      }
    };

    fetchDocuments();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!documentId) {
      alert("Please select a document first");
      return;
    }
    setLoading(true);
    try {
      const token = localStorage.getItem("token");
      const response = await axios.post(
        "http://localhost:8000/api/v1/documents/query",
        {
          document_id: documentId,
          question: question.trim(),
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setMessages([
        ...messages,
        { type: "question", content: question },
        { type: "answer", content: response.data.answer },
      ]);
      setQuestion("");
    } catch (error) {
      const errorMessage =
        error.response?.data?.detail || "Error querying document";
      setMessages([
        ...messages,
        { type: "question", content: question },
        { type: "answer", content: errorMessage },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleBackToSelection = () => {
    navigate("/select");
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <div className="chat-container">
      <h1>Chat with Document</h1>

      <div className="document-selector">
        <h2>Select Document</h2>
        <select
          value={documentId}
          onChange={(e) => setDocumentId(e.target.value)}
          required
          aria-label="Select a document"
        >
          <option value="">Select a document...</option>
          {documents.map((doc) => (
            <option key={doc.id} value={doc.id}>
              {doc.title}
            </option>
          ))}
        </select>
      </div>

      <div className="chat-messages" role="log" aria-live="polite">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.type}`}
            role={message.type === "question" ? "note" : "status"}
          >
            <strong>{message.type === "question" ? "You: " : "AI: "}</strong>
            {message.content}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Type your question..."
          required
          aria-label="Your question"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !documentId || !question.trim()}
          aria-label={loading ? "Sending question" : "Send question"}
        >
          {loading ? (
            <>
              <span className="loading-spinner" aria-hidden="true" />
              Sending...
            </>
          ) : (
            "Send"
          )}
        </button>
      </form>

      <div className="navigation-buttons">
        <button
          onClick={handleBackToSelection}
          aria-label="Back to document selection"
        >
          Back
        </button>
        <button onClick={handleLogout} aria-label="Logout from application">
          Logout
        </button>
      </div>
    </div>
  );
}

export default QueryForm;
