import React from "react";
import { Link, useNavigate } from "react-router-dom";
import "../styles/common.css";

function SelectionPage() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <div className="page-container">
      <div className="card">
        <h1 className="page-title">Document Management</h1>
        <Link to="/upload" className="link-button">
          <button className="btn">
            <i className="fas fa-upload" /> Upload New Document
          </button>
        </Link>
        <Link to="/query" className="link-button">
          <button className="btn btn-outline">
            <i className="fas fa-search" /> Query Documents
          </button>
        </Link>
        <button className="btn btn-secondary" onClick={handleLogout}>
          <i className="fas fa-sign-out-alt" /> Sign Out
        </button>
      </div>
    </div>
  );
}

export default SelectionPage;
