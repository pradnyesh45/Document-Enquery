import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "../styles/common.css";

function UploadForm() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", file.name);

    try {
      const token = localStorage.getItem("token");
      const response = await axios.post(
        "http://localhost:8000/api/v1/documents/",
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setMessage({
        type: "success",
        text: `File uploaded successfully. Status: ${response.data.status}`,
      });
    } catch (error) {
      setMessage({
        type: "error",
        text: error.response?.data?.detail || "Error uploading file",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="card">
        <h1 className="page-title">Upload Document</h1>
        {message && (
          <div className={`message ${message.type}`}>{message.text}</div>
        )}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Select File</label>
            <input
              type="file"
              onChange={handleFileChange}
              required
              disabled={loading}
              className="form-input"
              style={{ padding: "var(--spacing-xs)" }}
            />
          </div>
          <button className="btn" type="submit" disabled={loading || !file}>
            {loading ? "Uploading..." : "Upload Document"}
          </button>
          <button
            className="btn btn-outline"
            type="button"
            onClick={() => navigate("/select")}
            disabled={loading}
          >
            Back to Selection
          </button>
        </form>
      </div>
    </div>
  );
}

export default UploadForm;
