import React, { useState } from "react";
import "./AuthPage.css";

function AuthPage({ setCurrentPage, setRole, setUserId }) {
    const [roleChoice, setRoleChoice] = useState(null);
    const [isRegistering, setIsRegistering] = useState(false);

    // Form fields
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [smartMeterId, setSmartMeterId] = useState("");
    const [errorMessage, setErrorMessage] = useState("");

    const handleLogin = async (e) => {
        e.preventDefault();
        setErrorMessage("");

        try {
            const response = await fetch("/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    username: username,
                    password: password,
                }),
            });



            const data = await response.json();

            if (response.ok) {
                // Login successful - store token
                localStorage.setItem('token', data.token);
                localStorage.setItem('user', JSON.stringify(data.user));

                setRole(data.user.role);
                // Use the smart meter id as the domain identifier for energy data for ALL roles
                // (consumer and provider views query energy by contour/smart-meter id)
                setUserId(data.user.smart_meter_id);
                setCurrentPage("home");

                // Clear simple_log on login
                if (data.user.role === "consumer") {
                    fetch("/simple_log/clear", {
                        method: "POST",
                        headers: {
                        'Authorization': `Bearer ${data.token}`
                        }
                    }).catch((err) =>
                        console.warn("Could not clear simple_log:", err)
                    );

                    fetch("/simple_log", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            'Authorization': `Bearer ${data.token}`
                        },
                        body: JSON.stringify({
                            line: `0)The smart meter with ID ${data.user.smart_meter_id || data.user.id} has been accessed.`
                        }),
                    }).catch((err) => console.warn("Failed to send simple_log", err));
                }
            } else {
                // Login failed
                setErrorMessage(data.error || "Login failed");
            }
        } catch (err) {
            setErrorMessage("Connection error. Please try again.");
            console.error("Login error:", err);
        }
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        setErrorMessage("");

        try {
            const response = await fetch("/auth/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    username: username,
                    email: email,
                    password: password,
                    role: roleChoice,
                    smart_meter_id: smartMeterId,

                }),
            });

            const data = await response.json();

            if (response.ok) {
                // Registration successful - now log them in
                setErrorMessage("");
                alert("Registration successful! Please log in.");
                setIsRegistering(false);
                // Clear form
                setUsername("");
                setEmail("");
                setPassword("");
                setSmartMeterId("");
            } else {
                // Registration failed
                setErrorMessage(data.error || "Registration failed");
            }
        } catch (err) {
            setErrorMessage("Connection error. Please try again.");
            console.error("Registration error:", err);
        }
    };

    const resetForm = () => {
        setRoleChoice(null);
        setIsRegistering(false);
        setUsername("");
        setEmail("");
        setPassword("");
        setSmartMeterId("");
        setErrorMessage("");
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
                    <h2 className="mb-4 fw-bold text-primary">
                        Provider {isRegistering ? "Registration" : "Login"}
                    </h2>

                    {errorMessage && (
                        <div className="alert alert-danger" role="alert">
                            {errorMessage}
                        </div>
                    )}

                    <form onSubmit={isRegistering ? handleRegister : handleLogin}>
                        <div className="mb-3">
                            <label className="form-label">Username</label>
                            <input
                                type="text"
                                className="form-control"
                                required
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                            />
                        </div>

                        {isRegistering && (
                            <div className="mb-3">
                                <label className="form-label">Email</label>
                                <input
                                    type="email"
                                    className="form-control"
                                    required
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                />
                            </div>
                        )}

                        <div className="mb-3">
                            <label className="form-label">Password</label>
                            <input
                                type="password"
                                className="form-control"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </div>

                        {isRegistering && (
                            <div className="mb-3">
                                <label className="form-label">Smart Meter ID</label>
                                <input
                                    type="text"
                                    className="form-control"
                                    required
                                    value={smartMeterId}
                                    onChange={(e) => setSmartMeterId(e.target.value)}
                                />
                            </div>
                        )}

                        <button type="submit" className="btn btn-primary w-100">
                            {isRegistering ? "Register" : "Login"}
                        </button>

                        <button
                            type="button"
                            className="btn btn-link w-100 mt-2"
                            onClick={() => setIsRegistering(!isRegistering)}
                        >
                            {isRegistering ? "Already have an account? Login" : "Need an account? Register"}
                        </button>

                        <button
                            type="button"
                            className="btn btn-link w-100"
                            onClick={resetForm}
                        >
                            Back
                        </button>
                    </form>
                </div>
            )}

            {roleChoice === "consumer" && (
                <div className="auth-card">
                    <h2 className="mb-4 fw-bold text-primary">
                        Consumer {isRegistering ? "Registration" : "Login"}
                    </h2>

                    {errorMessage && (
                        <div className="alert alert-danger" role="alert">
                            {errorMessage}
                        </div>
                    )}

                    <form onSubmit={isRegistering ? handleRegister : handleLogin}>
                        <div className="mb-3">
                            <label className="form-label">Username</label>
                            <input
                                type="text"
                                className="form-control"
                                required
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                            />
                        </div>

                        {isRegistering && (
                            <div className="mb-3">
                                <label className="form-label">Email</label>
                                <input
                                    type="email"
                                    className="form-control"
                                    required
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                />
                            </div>
                        )}

                        {isRegistering && (
                            <div className="mb-3">
                                <label className="form-label">Smart Meter ID</label>
                                <input
                                    type="text"
                                    className="form-control"
                                    required
                                    value={smartMeterId}
                                    onChange={(e) => setSmartMeterId(e.target.value)}
                                />
                            </div>
                        )}

                        <div className="mb-3">
                            <label className="form-label">Password</label>
                            <input
                                type="password"
                                className="form-control"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </div>

                        <button type="submit" className="btn btn-primary w-100">
                            {isRegistering ? "Register" : "Login"}
                        </button>

                        <button
                            type="button"
                            className="btn btn-link w-100 mt-2"
                            onClick={() => setIsRegistering(!isRegistering)}
                        >
                            {isRegistering ? "Already have an account? Login" : "Need an account? Register"}
                        </button>

                        <button
                            type="button"
                            className="btn btn-link w-100"
                            onClick={resetForm}
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