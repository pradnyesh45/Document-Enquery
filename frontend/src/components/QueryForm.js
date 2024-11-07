import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function QueryForm() {
  const [documentId, setDocumentId] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [documents, setDocuments] = useState([]);
  const navigate = useNavigate();

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
    setLoading(true);
    try {
      const token = localStorage.getItem("token");
      const response = await axios.post(
        "http://localhost:8000/api/v1/documents/query",
        {
          document_id: documentId,
          question: question,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setAnswer(response.data.answer);
    } catch (error) {
      setAnswer("Error querying document");
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
    <div>
      <h1>Query Document</h1>
      <div>
        <h2>Documents</h2>
        <ul>
          {documents.length > 0 ? (
            documents.map((doc) => (
              <li key={doc.id}>
                <button onClick={() => setDocumentId(doc.id)}>
                  {doc.title}
                </button>
              </li>
            ))
          ) : (
            <li>No documents available</li>
          )}
        </ul>
      </div>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Document ID:</label>
          <input
            type="text"
            value={documentId}
            onChange={(e) => setDocumentId(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Question:</label>
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            required
          />
        </div>
        <button type="submit" disabled={loading}>
          {loading ? "Loading..." : "Submit"}
        </button>
      </form>
      {answer && (
        <div>
          <h2>Answer:</h2>
          <p>{answer}</p>
        </div>
      )}
      <button onClick={handleBackToSelection}>Back to Selection</button>
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}

export default QueryForm;
