import React, { useState, useEffect } from "react";
import { Line } from "react-chartjs-2";
import "./TariffCalculator.css";
import { fetchWithAuth } from '../utils/api';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function gaussian(x, mean, sigma = 2) {
  return Math.exp(-0.5 * Math.pow((x - mean) / sigma, 2));
}

function TariffCalculator() {
  const [hour, setHour] = useState(18);
  const [currentCost, setCurrentCost] = useState(null);
  const [loading, setLoading] = useState(false);
const [currentUser, setCurrentUser] = useState(null);

  const previousCost = 1200;
  const [pointsMessage, setPointsMessage] = useState("");
  
  // Get current user from authentication
    useEffect(() => {
    const getCurrentUser = async () => {
      try {
        const response = await fetchWithAuth('http://localhost:5000/auth/verify');
        if (response.ok) {
          const data = await response.json();
          setCurrentUser(data.user.username);
        }
      } catch (error) {
        console.error("Error getting current user:", error);
      }
    };

    getCurrentUser();
  }, []);

  // Fetch current cost from backend
  useEffect(() => {
    // Debounce the fetch so quick slider moves don't trigger many requests.
    // Also use AbortController to cancel an in-flight request when hour changes.
    const controller = new AbortController();
    const debounceMs = 200; // tweak for responsiveness vs requests

    const id = setTimeout(() => {
      const fetchTariff = async () => {
        setLoading(true);
        try {
          const resp = await fetchWithAuth(`http://localhost:5000/tariff`, { signal: controller.signal });
          if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
          const json = await resp.json();
          // Compute estimated cost using the returned distribution value for the selected hour
          const computed = Math.round(json[hour] * previousCost * 0.15 + previousCost * 0.85);
          setCurrentCost(computed);
        } catch (err) {
          if (err.name === "AbortError") {
            // Request was aborted because user changed the hour quickly; ignore
            console.log("Tariff fetch aborted");
            return;
          }
          console.error("Error fetching tariff:", err);
          setCurrentCost(null);
        } finally {
          setLoading(false);
        }
      };

      fetchTariff();
    }, debounceMs);

    return () => {
      clearTimeout(id);
      controller.abort();
    };
  }, [hour]);


  // Send a simple log each time the computed cost updates (debounced fetch sets currentCost)
  useEffect(() => {
    if (currentCost === null || !currentUser) return;

    let mounted = true;
    (async () => {
      try {
        const response = await fetch("http://localhost:5000/calculate/tariff_points", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            user: currentUser, 
            previous_cost: previousCost,
            estimated_cost: currentCost
          }),
        });

        const data = await response.json();
        if (mounted) {
          const earnedLabel = data.earned_points === 1 ? "point" : "points";
          const totalLabel = data.total_points === 1 ? "point" : "points";
          setPointsMessage(`You earned ${data.earned_points} ${earnedLabel}! Total: ${data.total_points} ${totalLabel}`);
        }
      } catch (err) {
        console.warn("Failed to update leaderboard", err);
      }
    })();

    return () => {
      mounted = false;
    };
  }, [currentCost, currentUser]);


    // Send a simple log each time the computed cost updates (debounced fetch sets currentCost)
  useEffect(() => {
    if (currentCost === null) return;

    let mounted = true;
    (async () => {
      try {
        await fetchWithAuth("http://localhost:5000/simple_log", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ line: `2)The previous cost of the tariff the user was charged is: ${previousCost} MDL; The current estimated cost is: ${currentCost} MDL` }),
        });
        if (mounted) console.log("Sent simple_log");
      } catch (err) {
        console.warn("Failed to send simple_log", err);
      }
    })();

    return () => {
      mounted = false;
    };
  }, [currentCost]);

  // Chart data
  const labels = Array.from({ length: 25 }, (_, i) =>
    i.toString().padStart(2, "0")
  );

  // Two Gaussian peaks: morning (center ~9h), evening (center ~19h)
  const values = labels.map((h) => {
    const x = parseInt(h);
    const morningPeak = gaussian(x, 9, 2);  // 7–11
    const eveningPeak = gaussian(x, 19, 2.5); // 17–22
    return morningPeak + eveningPeak;
  });

  const maxVal = Math.max(...values);
  const scaledValues = values.map((v) => (v / maxVal) * 100);

  const data = {
    labels,
    datasets: [
      {
        label: "Consumption distribution (two peaks)",
        data: scaledValues,
        borderColor: "#004aad",
        backgroundColor: "rgba(0, 74, 173, 0.2)",
        tension: 0.3,
        pointRadius: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: true },
      title: { display: false },
    },
    scales: {
      y: {
        title: { display: true, text: "MW (scaled)" },
        beginAtZero: true,
      },
      x: {
        title: { display: true, text: "Hour (00–24)" },
      },
    },
  };

  return (
    <div className="tariff-container">
      <h2 className="tariff-title">Tariff Calculator</h2>

      <div className="chart-box chart-container">
        <Line data={data} options={options} />
      </div>

      <div className="slider-box">
        <label htmlFor="hourRange" className="fw-bold">
          Select peak hour: {hour}:00
        </label>
        <input
          id="hourRange"
          type="range"
          min="0"
          max="24"
          value={hour}
          onChange={(e) => setHour(Number(e.target.value))}
        />
      </div>

      <div className="cost-box">
        <p>
          <strong>Previous Cost:</strong> {previousCost} MDL
        </p>
        <p>
          <strong>Estimated Current Cost:</strong>{" "}
          {loading
            ? "Loading..."
            : currentCost !== null
            ? `${currentCost} MDL`
            : "Error fetching"}
        </p>
      </div>

      {/* Feedback message for earned points */}
      {pointsMessage && (
        <div className="points-box">
          <p className="points-message">{pointsMessage}</p>
        </div>
      )}


      <div className="description-box">
        <h4>How to read this chart</h4>
        <p>
          The blue curve shows daily electricity consumption with{" "}
          <b>two peaks</b>: one in the <b>morning (7–11)</b> and another in the{" "}
          <b>evening (17–22)</b>. These are modeled with Gaussian distributions.  
          The slider still fetches the estimated cost for the selected{" "}
          <b>hour</b> from the backend.
        </p>
      </div>
    </div>
  );
}

export default TariffCalculator;
