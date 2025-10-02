import React, { useEffect, useState } from "react";
import "./DashboardandConsumers.css";

const TopConsumers = () => {
  const [consumers, setConsumers] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchConsumers = async () => {
      try {
        const response = await fetch("http://localhost:5000/consumptions");
        const result = await response.json();
        setConsumers(result || {});
      } catch (error) {
        console.error("Error fetching consumptions:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchConsumers();
  }, []);

  const sortedConsumers = Object.entries(consumers).sort((a, b) => b[1] - a[1]);

  return (
    <div className="container py-4">
      <h2 className="mb-4">Regional Consumptions</h2>

      {loading ? (
        <p>Loading data...</p>
      ) : (
        <ul className="list-group top-consumers-list">
          {sortedConsumers.map(([region, value], i) => (
            <li
              key={i}
              className="list-group-item d-flex justify-content-between align-items-center p-4 fs-5"
              style={{ borderRadius: "12px", marginBottom: "12px" }}
            >
              <span>
                <i className="bi bi-geo-alt text-primary me-3 fs-4"></i>
                {region}
              </span>
              <span className="badge bg-danger rounded-pill fs-5 px-4 py-2">
                {value } kW
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default TopConsumers;
