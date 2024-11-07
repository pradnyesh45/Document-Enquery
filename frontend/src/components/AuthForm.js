import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "../styles/common.css";

function AuthForm({ type }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (type === "signup") {
        await axios.post("http://localhost:8000/api/v1/users/", {
          email: username,
          password: password,
        });
        setMessage({
          type: "success",
          text: "Signup successful! Please login.",
        });
        setTimeout(() => navigate("/login"), 2000);
      } else {
        const params = new URLSearchParams({
          grant_type: "password",
          username,
          password,
          scope: "",
          client_id: "string",
          client_secret: "string",
        });

        const response = await axios.post(
          "http://localhost:8000/api/v1/users/login",
          params
        );

        localStorage.setItem("token", response.data.access_token);
        setMessage({ type: "success", text: "Login successful!" });
        navigate("/select");
      }
    } catch (error) {
      setMessage({
        type: "error",
        text: error.response?.data?.detail || "An error occurred",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="card">
        <h1 className="page-title">
          {type === "signup" ? "Create Account" : "Sign In"}
        </h1>
        {message && (
          <div className={`message ${message.type}`}>{message.text}</div>
        )}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              className="form-input"
              type="email"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              className="form-input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
            />
          </div>
          <button className="btn" type="submit" disabled={loading}>
            {loading
              ? "Please wait..."
              : type === "signup"
              ? "Create Account"
              : "Sign In"}
          </button>
          <button
            className="btn btn-outline"
            type="button"
            onClick={() => navigate("/")}
            disabled={loading}
          >
            Back to Home
          </button>
        </form>
      </div>
    </div>
  );
}

export default AuthForm;
