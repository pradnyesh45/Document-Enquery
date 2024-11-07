import React from "react";
import { useNavigate } from "react-router-dom";
import "../styles/common.css";

function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="page-container">
      <div className="card">
        <h1 className="page-title">Document Enquiry System</h1>
        <p style={{ textAlign: "center", marginBottom: "var(--spacing-lg)" }}>
          Upload and query documents securely with our advanced AI-powered
          system.
        </p>
        <button className="btn btn-outline" onClick={() => navigate("/signup")}>
          Create Account
        </button>
        <button className="btn" onClick={() => navigate("/login")}>
          Sign In
        </button>
      </div>
    </div>
  );
}

export default HomePage;
