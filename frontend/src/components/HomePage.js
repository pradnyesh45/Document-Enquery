import React from "react";
import { useNavigate } from "react-router-dom";

function HomePage() {
  const navigate = useNavigate();

  return (
    <div>
      <h1>Welcome to the Document Enquiry System</h1>
      <p>This system allows you to upload and query documents securely.</p>
      <button onClick={() => navigate("/signup")}>Signup</button>
      <button onClick={() => navigate("/login")}>Login</button>
    </div>
  );
}

export default HomePage;
