import React, { useState, useEffect } from "react";
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
import { Line } from "react-chartjs-2";
import "./ProviderDashboard.css";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const ProviderDashboard = ({ setCurrentPage }) => {
  const [region, setRegion] = useState("Balti");
  const [consumptionData, setConsumptionData] = useState([]);
  const [loading, setLoading] = useState(true);

  const regions = [
    "Balti",
    "Cahul",
    "Chisinau",
    "Comrat",
    "Cricova",
    "Edinet",
    "Floresti",
    "Hincesti",
    "Orhei",
    "Rezina",
    "Soroca",
    "Stefan Voda",
    "Tiraspol",
    "Ungheni",
    "Vadul lui Voda",
  ];

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await fetch(`http://localhost:5000/region/all`);
        const result = await response.json();
        console.log(result)

        // Extract data for the selected region
        const regionData = result[0][region] || {};
        console.log(regionData)

        // Convert object with timestamps to array of Export values
        const dataArray = Object.entries(regionData)
          // Optional: filter to full hours (MM:SS = "00:00")
          .filter(([timestamp]) => timestamp.slice(14, 19) === "00:00")
          .map(([timestamp, values]) => ({
            timestamp,
            export: values.Export,
            import: values.Import,
          }));
        console.log(dataArray)
        setConsumptionData(dataArray);
      } catch (error) {
        console.error("Error fetching region data:", error);
        setConsumptionData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [region]);

  // Use timestamps as labels
  const labels = consumptionData.map((d) => d.timestamp);

  const data = {
    labels,
    datasets: [
      {
        label: `${region} Export (KW)`,
        data: consumptionData.map((d) => d.export),
        borderColor: "#004aad",
        backgroundColor: "rgba(0, 74, 173, 0.2)",
        tension: 0.3,
        fill: true,
      },
      {
        label: `${region} Import (KW)`,
        data: consumptionData.map((d) => d.import),
        borderColor: "#ff5a5f",
        backgroundColor: "rgba(255, 90, 95, 0.2)",
        tension: 0.3,
        fill: true,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: "top" },
      title: { display: true, text: "Region Energy Flow" },
    },
    scales: {
      y: { title: { display: true, text: "KW" }, beginAtZero: true },
      x: { title: { display: true, text: "Time" } },
    },
  };

  return (
    <div className="container py-4">
      <h2 className="mb-4">Dashboard</h2>

      <div className="dashboard-grid">
        <div
          className="card dashboard-card clickable"
          onClick={() => setCurrentPage("search")}
        >
          <i className="bi bi-map display-6 text-primary"></i>
          <h5>Interactive Map</h5>
          <p className="text-muted">Click to view localities</p>
        </div>

        <div className="card dashboard-card">
          <i className="bi bi-lightning-charge display-6 text-warning"></i>
          <h5>Current Export</h5>
          <p className="fw-bold">
            {consumptionData.length > 0
              ? `${consumptionData[consumptionData.length - 1].export} KW`
              : "N/A"}
          </p>
        </div>

        <div className="card dashboard-card">
          <i className="bi bi-lightning-charge-fill display-6 text-danger"></i>
          <h5>Current Import</h5>
          <p className="fw-bold">
            {consumptionData.length > 0
              ? `${consumptionData[consumptionData.length - 1].import} KW`
              : "N/A"}
          </p>
        </div>
      </div>

      <div className="mt-5">
        <label className="form-label fw-bold">Select Region</label>
        <select
          className="form-select mb-3"
          value={region}
          onChange={(e) => setRegion(e.target.value)}
        >
          {regions.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>

        <div className="chart-container">
          {loading ? <p>Loading data...</p> : <Line data={data} options={options} />}
        </div>
      </div>
    </div>
  );
};

export default ProviderDashboard;
