import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function AuthForm({ type }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const endpoint =
        type === "signup" ? "/api/v1/users/" : "/api/v1/users/login";

      const params = new URLSearchParams();
      params.append("grant_type", "password");
      params.append("username", username);
      params.append("password", password);
      params.append("scope", "");
      params.append("client_id", "string");
      params.append("client_secret", "string");

      const response = await axios.post(
        `http://localhost:8000${endpoint}`,
        params,
        {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            Accept: "application/json",
          },
        }
      );

      setMessage(response.data.msg || "Login successful");
      if (type === "login") {
        localStorage.setItem("token", response.data.access_token);
        navigate("/select");
      }
    } catch (error) {
      setMessage(
        "Error: " +
          (error.response ? error.response.data.detail : error.message)
      );
    }
  };

  const handleBackToHome = () => {
    navigate("/");
  };

  return (
    <div>
      <h1>{type === "signup" ? "Signup" : "Login"}</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Username:</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Password:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">{type === "signup" ? "Signup" : "Login"}</button>
      </form>
      {message && <p>{message}</p>}
      <button onClick={handleBackToHome}>Back to Home</button>
    </div>
  );
}

export default AuthForm;
