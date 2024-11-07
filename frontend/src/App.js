import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./components/HomePage";
import SelectionPage from "./components/SelectionPage";
import UploadForm from "./components/UploadForm";
import QueryForm from "./components/QueryForm";
import AuthForm from "./components/AuthForm";
import PrivateRoute from "./components/PrivateRoute";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<AuthForm type="login" />} />
        <Route path="/signup" element={<AuthForm type="signup" />} />
        <Route
          path="/select"
          element={
            <PrivateRoute>
              <SelectionPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/upload"
          element={
            <PrivateRoute>
              <UploadForm />
            </PrivateRoute>
          }
        />
        <Route
          path="/query"
          element={
            <PrivateRoute>
              <QueryForm />
            </PrivateRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
