import React, { useEffect, useState } from "react";
import "./HomePage.css";
import { fetchWithAuth } from '../utils/api';

/**
 * Expected backend payloads (any of these work):
 *   1) [currentUsage, smartHouses]
 *   2) { currentUsage: 123.4, smartHouses: 11871 }
 *   3) { current_usage: 123.4, smart_houses: 11871 }  // snake_case also supported
 *   4) Plain text "123.4 11871" or "123.4,11871"
 */

const GREEN_ENERGY = 34;
const CO2_REDUCTION = 12;

function HomePage({ openMenu }) {
  const [currentUsage, setCurrentUsage] = useState(null);
  const [smartHouses, setSmartHouses] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    (async () => {
      try {
        const res = await fetchWithAuth("/general_info");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const contentType = res.headers.get("content-type") || "";

        let usageVal = null;
        let housesVal = null;

        if (contentType.includes("application/json")) {
          const data = await res.json();

          if (Array.isArray(data)) {
            // Expecting [currentUsage, smartHouses]
            [usageVal, housesVal] = data;
            usageVal /= 1000000;
            usageVal = Math.round(usageVal);
          } else if (data && typeof data === "object") {
            // Handles camelCase or snake_case keys
            usageVal =
              data.currentUsage ??
              data.current_usage ??
              data.usage ??
              data.value ??
              null;

            housesVal =
              data.smartHouses ??
              data.smart_houses ??
              data.smartHomes ??
              data.houses ??
              null;
          }
        } else {
          // Fallback: text "a b" or "a,b"
          const text = await res.text();
          const [a, b] = text.split(/[,\s]+/);
          usageVal = a !== undefined ? Number(a) : null;
          housesVal = b !== undefined ? Number(b) : null;
        }

        if (isMounted) {
          setCurrentUsage(
            typeof usageVal === "number" && !Number.isNaN(usageVal) ? usageVal : null
          );
          setSmartHouses(
            typeof housesVal === "number" && !Number.isNaN(housesVal) ? housesVal : null
          );
          setLoading(false);
        }

        // Fire-and-forget log using the dynamic values
        const line = `The current usage of electricity in Moldova is: ${usageVal} MW
Number of houses with smart meters connected: ${housesVal}
Percentage of green energy used: ${GREEN_ENERGY}%
Percentage of CO₂ reduction achieved: ${CO2_REDUCTION}%`;

          fetchWithAuth("/simple_log", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ line }),
        }).catch((err) => console.warn("Failed to send simple_log", err));
      } catch (err) {
        console.warn("Failed to fetch /general_info", err);
        if (isMounted) setLoading(false);
      }
    })();

    return () => {
      isMounted = false;
    };
  }, []);

  const nf = new Intl.NumberFormat("en-US");
  const displayUsage = loading ? "Loading..." : currentUsage ?? "N/A";
  const displaySmartHouses = loading
    ? "Loading..."
    : smartHouses != null
    ? nf.format(smartHouses)
    : "N/A";

  return (
    <div className="HomePage">
      {/* HERO */}
      <div className="hero d-flex align-items-center text-center text-white">
        <div className="container">
          <h1 className="display-3 fw-bold mb-3 animate-fadeDown">
            <i className="bi bi-lightning-charge-fill me-2"></i>
            Smart Energy App
          </h1>
          <p className="lead mb-4 animate-fadeUp">
            Turning energy data into smart actions for a sustainable future
          </p>
          {/* Example: a button that could open a menu if you pass openMenu */}
          {typeof openMenu === "function" && (
            <button className="btn btn-outline-light" onClick={openMenu}>
              <i className="bi bi-list me-1" /> Menu
            </button>
          )}
        </div>
      </div>

      {/* STATS */}
      <section className="stats py-5">
        <div className="container">
          <div className="row g-4 text-center">
            <div className="col-md-3">
              <div className="stat-card shadow-sm p-4">
                <i className="bi bi-lightning-charge text-primary mb-2"></i>
                <h3 className="fw-bold">
                  {displayUsage}{" "}
                  {displayUsage !== "Loading..." && displayUsage !== "N/A" ? "MW" : ""}
                </h3>
                <p>Current Usage</p>
              </div>
            </div>

            <div className="col-md-3">
              <div className="stat-card shadow-sm p-4">
                <i className="bi bi-house text-success mb-2"></i>
                <h3 className="fw-bold">{displaySmartHouses}</h3>
                <p>Smart Homes Connected</p>
              </div>
            </div>

            <div className="col-md-3">
              <div className="stat-card shadow-sm p-4">
                <i className="bi bi-tree text-warning mb-2"></i>
                <h3 className="fw-bold">{GREEN_ENERGY}%</h3>
                <p>Green Energy</p>
              </div>
            </div>

            <div className="col-md-3">
              <div className="stat-card shadow-sm p-4">
                <i className="bi bi-cloud-snow text-info mb-2"></i>
                <h3 className="fw-bold">{CO2_REDUCTION}%</h3>
                <p>CO₂ Reduction</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SOLUTION */}
      <section className="solution py-5 bg-light">
        <div className="container">
          <div className="row align-items-center">
            <div className="col-lg-6 mb-4 mb-lg-0">
              <h2 className="display-5 fw-bold mb-4 text-primary">Our Innovative Solution</h2>
              <p className="lead mb-4">
                We provide a complete system for monitoring and forecasting energy consumption,
                helping both providers and consumers make smarter decisions.
              </p>
              <ul className="list-unstyled features">
                <li>
                  <i className="bi bi-activity text-primary me-2"></i> Real-time Monitoring
                </li>
                <li>
                  <i className="bi bi-bar-chart-line text-success me-2"></i> Accurate Forecasts
                </li>
                <li>
                  <i className="bi bi-person-check text-warning me-2"></i> Personalized Recommendations
                </li>
                <li>
                  <i className="bi bi-bell text-danger me-2"></i> Early Alerts
                </li>
                <li>
                  <i className="bi bi-diagram-3 text-info me-2"></i> Different scenarios simulations
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default HomePage;
