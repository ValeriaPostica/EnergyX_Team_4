import React, { useState, useEffect } from "react";
import { Line } from "react-chartjs-2";
import { fetchWithAuth } from '../utils/api';

import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import "./HourlyConsumption.css";

ChartJS.register(LineElement, PointElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

const HourlyConsumption = () => {
  const [day, setDay] = useState("Today");
  const [userId] = useState(() => localStorage.getItem("userId") || null); // ia ID-ul salvat
  const [consumptionData, setConsumptionData] = useState({
    Yesterday: [],
    Today: [],
    Tomorrow: [],
  });

  const hours = Array.from({ length: 24 }, (_, i) => (i < 10 ? `0${i}` : `${i}`));

  useEffect(() => {
    const fetchData = async () => {
      if (!userId) {
        console.warn("No userId found in localStorage.");
        return;
      }

      try {

        let yesterday = 6;
        let today = 7;
        const y_res = await fetchWithAuth(`http://localhost:5000/diff/${userId}/${yesterday}`);
        const t_res = await fetchWithAuth(`http://localhost:5000/diff/${userId}/${today}`);
        
        // to delete
        const example_schedule = [
          ["thermostat", 12, 15],
          ["conditioner", 13, 16],
          ["light", 8, 20],
          ["energy_saving", 18, 21]
        ];
        const scheduleParam = encodeURIComponent(JSON.stringify(example_schedule));
        const pred_res = await fetchWithAuth(`http://localhost:5000/pred/simulate/${userId}/${scheduleParam}`);
        const pred_json = await pred_res.json();
        console.log("AAAA");
        console.log(pred_json);
        // end to delete
        let y_arr = await y_res.json();
        let t_arr = await t_res.json();

        // Fetch real predictions using the user ID
        let result2;
        try {

          const response2 = await fetchWithAuth(`http://localhost:5000/pred/${userId}`);
          result2 = await response2.json();
          console.log("Fetched prediction data:", result2);
        } catch (predError) {
          console.warn("Failed to fetch predictions, using fallback data:", predError);
          // Fallback to random data if prediction fails
          result2 = Array.from({ length: 24 }, () => Math.random() * 50 + 20);
        }

        // Ensure arrays are valid and pad to 24 values if needed
        if (!Array.isArray(y_arr)) y_arr = [];
        if (!Array.isArray(t_arr)) t_arr = [];
        const targetLen = 24;
        if (y_arr.length === 0) {
          // no data: fill with zeros
          y_arr = Array(targetLen).fill(0);
        } else if (y_arr.length < targetLen) {
          const last = Number(y_arr[y_arr.length - 1]) || 0;
          y_arr = y_arr.concat(Array(targetLen - y_arr.length).fill(last + 1));
        } else if (y_arr.length > targetLen) {
          y_arr = y_arr.slice(0, targetLen);
        }
        if (t_arr.length === 0) {
          t_arr = Array(targetLen).fill(0);
        } else if (t_arr.length < targetLen) {
          const lastT = Number(t_arr[t_arr.length - 1]) || 0;
          t_arr = t_arr.concat(Array(targetLen - t_arr.length).fill(lastT));
        } else if (t_arr.length > targetLen) {
          t_arr = t_arr.slice(0, targetLen);
        }

        console.log("Fetched consumption data:", t_arr, y_arr);

        const fmtHour = (i) => {
          const hour = Number(i);
          const hour12 = hour % 12 === 0 ? 12 : hour % 12;
          const ampm = hour < 12 ? 'am' : 'pm';
          return `${hour12} ${ampm}`;
        };

        const formatHourlyArray = (arr) => {
          return arr
            .map((val, idx) => `${fmtHour(idx)} = ${Math.round(Number(val) || 0)} kW`)
            .join(', ');
        };

        const today_str = formatHourlyArray(t_arr);
        const yesterday_str = formatHourlyArray(y_arr);
        const tomorrow_str = Array.isArray(result2) ? formatHourlyArray(result2) : String(result2); 

        (async () => {
      try {
        await fetchWithAuth("http://localhost:5000/simple_log", {
          method: "POST",
          headers: { "Content-Type": "application/json" },

          body: JSON.stringify({ line: `1) Hourly consumption for yesterday: ${yesterday_str}; today: ${today_str}; tomorrow: ${tomorrow_str}` }),
        });
        console.log("Sent simple_log");
      } catch (err) {
        console.warn("Failed to send simple_log", err);
      }
    })();

        // Asum că backend-ul întoarce:
        // { yesterday: [...], today: [...], tomorrow: [...] }
       
      setConsumptionData({
        Yesterday: y_arr,
        Today: t_arr,
        Tomorrow: result2, // keep empty until you add backend logic for it
      });

      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, [userId]); // refetch dacă userId se schimbă

  const data = {
    labels: hours,
    datasets: [
      {
        label: `Consumption (${day})`,
        data: consumptionData[day],
        borderColor: "#134675",
        backgroundColor: "rgba(19, 70, 117, 0.3)",
        tension: 0.3,
        pointRadius: 3,
        borderDash: day === "Tomorrow" ? [6, 6] : [],
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: true, position: "top" },
      title: { display: true, text: `Hourly Consumption - ${day}` },
    },
    scales: {
      y: {
        title: { display: true, text: "MW" },
        beginAtZero: true,
      },
      x: {
        title: { display: true, text: "Hour (00 - 24)" },
      },
    },
  };

  return (
    <div className="hourly-page">
      <h1>Hourly Consumption</h1>

      <div className="button-group">
        <button
          className={day === "Yesterday" ? "active" : ""}
          onClick={() => setDay("Yesterday")}
        >
          Yesterday
        </button>
        <button
          className={day === "Today" ? "active" : ""}
          onClick={() => setDay("Today")}
        >
          Today
        </button>
        <button
          className={day === "Tomorrow" ? "active" : ""}
          onClick={() => setDay("Tomorrow")}
        >
          Tomorrow
        </button>
      </div>

      <div className="chart-container">
        {consumptionData[day].length > 0 ? (
          <Line data={data} options={options} />
        ) : (
          <p>Loading data...</p>
        )}
      </div>

      <p className="description">
        This chart shows the amount of electricity consumed every hour in{" "}
        <b>megawatts (MW)</b>. The horizontal axis represents the hours of the
        day (00–24), while the vertical axis shows the energy demand in MW.
      </p>
    </div>
  );
};

export default HourlyConsumption;