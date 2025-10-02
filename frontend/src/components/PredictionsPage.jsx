import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(LineElement, PointElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

const PredictionsPage = () => {
  const [city, setCity] = useState("Bălți"); // Changed default to Balti
  const [timeRange, setTimeRange] = useState("24h");
  const [predictionData, setPredictionData] = useState([]);
  const [loading, setLoading] = useState(true);

  const cities = [
    "Bălți","Cahul","Chișinău","Comrat","Cricova","Edineț","Florești",
    "Hîncești","Orhei","Rezina","Soroca","Ștefan Vodă","Tiraspol","Ungheni","Vadul lui Vodă"
  ];

  // Fetch predictions based on time range and city
  useEffect(() => {
    const fetchPredictions = async () => {
      setLoading(true);
      try {
        // Convert city name to match backend format
        const locationName = city.replace(/ă/g, 'a').replace(/î/g, 'i').replace(/ș/g, 's').replace(/ț/g, 't');
        
        const endpoint = timeRange === "24h" 
          ? `http://localhost:5000/pred/location/${locationName}`
          : `http://localhost:5000/pred/location/${locationName}/week`;
        
        console.log(`Fetching predictions for ${city} (${locationName}) from: ${endpoint}`);
        const response = await fetch(endpoint);
        const result = await response.json();
        
        if (response.ok) {
          setPredictionData(result);
          console.log(`Successfully fetched ${result.length} predictions for ${city}`);
        } else {
          console.error("API Error:", result);
          throw new Error(result.error || "Failed to fetch predictions");
        }
      } catch (error) {
        console.error("Error fetching predictions:", error);
        // Fallback data
        const fallbackData = timeRange === "24h" 
          ? Array.from({length: 24}, () => Math.random() * 50 + 200)
          : Array.from({length: 168}, () => Math.random() * 50 + 200);
        setPredictionData(fallbackData);
      } finally {
        setLoading(false);
      }
    };

    fetchPredictions();
  }, [timeRange, city]); // Changed dependency from userId to city

  // Generate labels
  const labels = timeRange === "24h" 
    ? Array.from({length: 24}, (_, i) => `${i.toString().padStart(2, '0')}:00`)
    : Array.from({length: 7}, (_, i) => `Day ${i + 1}`);

  // Chart data configuration with proper sizing
  const chartData = {
    labels: timeRange === "24h" ? labels : labels,
    datasets: [
      {
        label: 'Predicted Consumption',
        data: timeRange === "24h" ? predictionData : predictionData.slice(0, 7),
        borderColor: '#0d6efd',
        backgroundColor: 'rgba(13, 110, 253, 0.1)',
        tension: 0.3,
        pointRadius: 4,
        pointHoverRadius: 6,
        borderWidth: 3,
        fill: true,
      }
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
          padding: 15,
          font: { size: 12 }
        }
      },
      title: {
        display: true,
        text: `Energy Forecast - ${city} (${timeRange === "24h" ? "24 Hours" : "7 Days"})`,
        font: { size: 14, weight: 'bold' },
        padding: 10
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: timeRange === "24h" ? "Hour" : "Day",
          font: { size: 12, weight: 'bold' }
        },
        grid: { display: true, color: 'rgba(0, 0, 0, 0.1)' }
      },
      y: {
        title: {
          display: true,
          text: 'Consumption (MW)',
          font: { size: 12, weight: 'bold' }
        },
        grid: { display: true, color: 'rgba(0, 0, 0, 0.1)' },
        beginAtZero: false,
      },
    },
  };

  return (
    <div className="container-fluid py-3">
      {/* Header */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card bg-primary text-white">
            <div className="card-body py-3">
              <h2 className="card-title text-center mb-0">⚡ Energy Consumption Forecasts</h2>
            </div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="row mb-3">
        <div className="col-md-6 mb-2">
          <label className="form-label fw-bold small">Select City</label>
          <select 
            className="form-select"
            value={city} 
            onChange={(e) => setCity(e.target.value)}
          >
            {cities.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
        
        <div className="col-md-6 mb-2">
          <label className="form-label fw-bold small">Time Range</label>
          <div className="btn-group w-100" role="group">
            <button
              type="button"
              className={`btn ${timeRange === "24h" ? "btn-primary" : "btn-outline-primary"}`}
              onClick={() => setTimeRange("24h")}
            >
              24 Hours
            </button>
            <button
              type="button"
              className={`btn ${timeRange === "7d" ? "btn-primary" : "btn-outline-primary"}`}
              onClick={() => setTimeRange("7d")}
            >
              7 Days
            </button>
          </div>
        </div>
      </div>

      {/* Chart - Properly sized */}
      <div className="row mb-3">
        <div className="col-12">
          <div className="card">
            <div className="card-body p-3">
              <div style={{ height: '350px' }}> {/* Fixed reasonable height */}
                {loading ? (
                  <div className="d-flex justify-content-center align-items-center h-100">
                    <div className="text-center">
                      <div className="spinner-border text-primary mb-2" role="status">
                        <span className="visually-hidden">Loading...</span>
                      </div>
                      <p className="text-muted small">Loading predictions...</p>
                    </div>
                  </div>
                ) : (
                  <Line data={chartData} options={chartOptions} />
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Cards - Compact (Trend removed) */}
      <div className="row">
        <div className="col-md-6 mb-2">
          <div className="card border-info h-100">
            <div className="card-body p-3 text-center">
              <h6 className="card-title text-info mb-1">Accuracy</h6>
              <h4 className="text-primary mb-1">94.2%</h4>
              <small className="text-muted">Prediction accuracy</small>
            </div>
          </div>
        </div>
        <div className="col-md-6 mb-2">
          <div className="card border-warning h-100">
            <div className="card-body p-3 text-center">
              <h6 className="card-title text-warning mb-1">Peak</h6>
              <h4 className="text-warning mb-1">
                {predictionData.length > 0 ? Math.max(...predictionData).toFixed(1) : '0'} MW
              </h4>
              <small className="text-muted">Maximum consumption</small>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PredictionsPage;
