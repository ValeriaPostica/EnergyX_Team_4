import React from "react";
import "./HomePage.css";

function HomePage({ openMenu }) {
  return (
    <div className="HomePage">
      <div className="hero d-flex align-items-center text-center text-white">
        <div className="container">
          <h1 className="display-3 fw-bold mb-3 animate-fadeDown">
            <i className="bi bi-lightning-charge-fill me-2"></i>
            Smart Energy App
          </h1>
          <p className="lead mb-4 animate-fadeUp">
            Turning energy data into smart actions for a sustainable future
          </p>
          
        </div>
        
      </div>

      <section className="stats py-5">
        <div className="container">
          <div className="row g-4 text-center">
            <div className="col-md-3">
              <div className="stat-card shadow-sm p-4">
                <i className="bi bi-lightning-charge text-primary mb-2"></i>
                <h3 className="fw-bold">11,756 MW</h3>
                <p>Current Usage</p>
              </div>
            </div>
            <div className="col-md-3">
              <div className="stat-card shadow-sm p-4">
                <i className="bi bi-house text-success mb-2"></i>
                <h3 className="fw-bold">11,871</h3>
                <p>Smart Homes Connected</p>
              </div>
            </div>
            <div className="col-md-3">
              <div className="stat-card shadow-sm p-4">
                <i className="bi bi-tree text-warning mb-2"></i>
                <h3 className="fw-bold">34%</h3>
                <p>Green Energy</p>
              </div>
            </div>
            <div className="col-md-3">
              <div className="stat-card shadow-sm p-4">
                <i className="bi bi-cloud-snow text-info mb-2"></i>
                <h3 className="fw-bold">12%</h3>
                <p>CO₂ Reduction</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="solution py-5 bg-light">
        <div className="container">
          <div className="row align-items-center">
            <div className="col-lg-6 mb-4 mb-lg-0">
              <h2 className="display-5 fw-bold mb-4 text-primary">
                Our Innovative Solution
              </h2>
              <p className="lead mb-4">
                We provide a complete system for monitoring and forecasting energy
                consumption, helping both providers and consumers make smarter decisions.
              </p>
              <ul className="list-unstyled features">
                <li><i className="bi bi-activity text-primary me-2"></i> Real-time Monitoring</li>
                <li><i className="bi bi-bar-chart-line text-success me-2"></i> Accurate Forecasts</li>
                <li><i className="bi bi-person-check text-warning me-2"></i> Personalized Recommendations</li>
                <li><i className="bi bi-bell text-danger me-2"></i> Early Alerts</li>
              </ul>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default HomePage;
