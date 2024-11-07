import React from "react";
import { Link, useNavigate } from "react-router-dom";

function SelectionPage() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <div>
      <h1>Choose an Action</h1>
      <Link to="/upload">
        <button>Upload Document</button>
      </Link>
      <Link to="/query">
        <button>Query Document</button>
      </Link>
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}

export default SelectionPage;
