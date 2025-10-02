import React, { useState } from "react";
import "./AuthPage.css";

function AuthPage({ setCurrentPage, setRole, setUserId }) {
  const [roleChoice, setRoleChoice] = useState(null);
  const [companyId, setCompanyId] = useState("");
  const [meterId, setMeterId] = useState("");

  const handleProviderLogin = (e) => {
    e.preventDefault();
    setRole("provider");
    setUserId(companyId);   // store company ID globally
    setCurrentPage("home");
  };

  const handleConsumerLogin = (e) => {
    e.preventDefault();
    setRole("consumer");
    setUserId(meterId);     // store smart meter ID globally
    setCurrentPage("home");
  };

  return (
    <div className="auth-wrapper">
      {!roleChoice && (
        <div className="choice-container text-center">
          <h1 className="mb-4 fw-bold">Smart Energy Platform</h1>
          <p className="mb-5">Please choose your role to continue</p>
          <div className="d-flex justify-content-center gap-4 flex-wrap">
            <button
              className="role-card provider"
              onClick={() => setRoleChoice("provider")}
            >
              <i className="bi bi-buildings display-4 mb-3"></i>
              <h4>Provider</h4>
              <p className="small">Company access</p>
            </button>
            <button
              className="role-card consumer"
              onClick={() => setRoleChoice("consumer")}
            >
              <i className="bi bi-person-circle display-4 mb-3"></i>
              <h4>Consumer</h4>
              <p className="small">Smart meter access</p>
            </button>
          </div>
        </div>
      )}

      {roleChoice === "provider" && (
        <div className="auth-card">
          <h2 className="mb-4 fw-bold text-primary">Provider Login</h2>
          <form onSubmit={handleProviderLogin}>
            <div className="mb-3">
              <label className="form-label">Company Name</label>
              <input type="text" className="form-control" required />
            </div>
            <div className="mb-3">
              <label className="form-label">Company ID</label>
              <input
                type="text"
                className="form-control"
                required
                value={companyId}
                onChange={(e) => setCompanyId(e.target.value)}
              />
            </div>
            <div className="mb-3">
              <label className="form-label">Password</label>
              <input type="password" className="form-control" required />
            </div>
            <button type="submit" className="btn btn-primary w-100">
              Login
            </button>
            <button
              type="button"
              className="btn btn-link w-100 mt-2"
              onClick={() => setRoleChoice(null)}
            >
              Back
            </button>
          </form>
        </div>
      )}

      {roleChoice === "consumer" && (
        <div className="auth-card">
          <h2 className="mb-4 fw-bold text-primary">Consumer Login</h2>
          <form onSubmit={handleConsumerLogin}>
            <div className="mb-3">
              <label className="form-label">Email</label>
              <input type="email" className="form-control" required />
            </div>
            <div className="mb-3">
              <label className="form-label">Smart Meter ID</label>
              <input
                type="text"
                className="form-control"
                required
                value={meterId}
                onChange={(e) => setMeterId(e.target.value)}
              />
            </div>
            <button type="submit" className="btn btn-primary w-100">
              Login
            </button>
            <button
              type="button"
              className="btn btn-link w-100 mt-2"
              onClick={() => setRoleChoice(null)}
            >
              Back
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

export default AuthPage;
