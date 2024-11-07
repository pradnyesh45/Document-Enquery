import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function UploadForm() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("file", file);

    try {
      const token = localStorage.getItem("token");
      await axios.post(
        "http://localhost:8000/api/v1/documents/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setMessage("File uploaded successfully");
    } catch (error) {
      setMessage("Error uploading file");
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
      <h1>Upload Document</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} required />
        <button type="submit">Upload</button>
      </form>
      {message && <p>{message}</p>}
      <button onClick={handleBackToSelection}>Back to Selection</button>
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}

export default UploadForm;
