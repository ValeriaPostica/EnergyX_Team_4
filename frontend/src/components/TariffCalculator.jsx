import React, { useState, useEffect } from "react";
import { Line } from "react-chartjs-2";
import "./TariffCalculator.css";
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
import { useRef, useCallback } from "react";

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

  const [isDragging, setIsDragging] = useState(false);
  const sliderRef = useRef(null);
  const animationFrameRef = useRef(null);

  const previousCost = 1200;

  const updateHour = useCallback((newHour) => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    
    animationFrameRef.current = requestAnimationFrame(() => {
      setHour(Math.min(24, Math.max(0, newHour)));
    });
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
          const resp = await fetch(`http://localhost:5000/tariff`, { signal: controller.signal });
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
    if (currentCost === null) return;

    let mounted = true;
    (async () => {
      try {
        await fetch("http://localhost:5000/simple_log", {
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

  useEffect(() => {
    const slider = sliderRef.current;
    if (!slider) return;

    const handleMouseDown = (e) => {
      setIsDragging(true);
      updateHourFromEvent(e);
    };

    const handleMouseMove = (e) => {
      if (!isDragging) return;
      updateHourFromEvent(e);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    const handleTouchStart = (e) => {
      setIsDragging(true);
      updateHourFromEvent(e.touches[0]);
      e.preventDefault();
    };

    const handleTouchMove = (e) => {
      if (!isDragging) return;
      updateHourFromEvent(e.touches[0]);
      e.preventDefault();
    };

    const handleTouchEnd = () => {
      setIsDragging(false);
    };

    const updateHourFromEvent = (event) => {
      const rect = slider.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const percentage = x / rect.width;
      const newHour = Math.round(percentage * 24);
      updateHour(newHour);
    };

    // Event listeners
    slider.addEventListener('mousedown', handleMouseDown);
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    slider.addEventListener('touchstart', handleTouchStart);
    document.addEventListener('touchmove', handleTouchMove);
    document.addEventListener('touchend', handleTouchEnd);

    return () => {
      // Cleanup
      slider.removeEventListener('mousedown', handleMouseDown);
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      slider.removeEventListener('touchstart', handleTouchStart);
      document.removeEventListener('touchmove', handleTouchMove);
      document.removeEventListener('touchend', handleTouchEnd);
      
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isDragging, updateHour]);

  const handleInputChange = (e) => {
  const newHour = Number(e.target.value);
    updateHour(newHour);
  };

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
          ref={sliderRef}
          id="hourRange"
          type="range"
          min="0"
          max="24"
          value={hour}
          onChange={handleInputChange}
          className="smooth-slider" 
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
