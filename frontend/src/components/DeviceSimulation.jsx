import React, { useCallback, useMemo, useState, useEffect } from "react";
import { Line } from "react-chartjs-2";
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
import "./DeviceSimulation.css";
import { fetchWithAuth } from "../utils/api";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const DEVICE_OPTIONS = [
  {
    value: "thermostat",
    label: "Thermostat",
    hint: "Adds heating load (~10.6 units / h)",
  },
  {
    value: "conditioner",
    label: "Air Conditioner",
    hint: "Adds cooling load (~20 units / h)",
  },
  { value: "light", label: "Lights", hint: "Adds lighting load (~3 units / h)" },
  {
    value: "energy_saving",
    label: "Energy Saver",
    hint: "Reduces usage (~25 units / h)",
  },
];

const HOURS = Array.from({ length: 24 }, (_, i) => i);
const COST_PER_UNIT = 0.32; // Approximated MDL cost per forecast unit
const CURRENCY = "MDL";
const TARGET_LEN = 24;

const formatHour = (value) => value.toString().padStart(2, "0");

const normalizeSeries = (data, length = TARGET_LEN) => {
  if (!Array.isArray(data)) {
    return [];
  }
  const numeric = data.map((val) => {
    const num = Number(val);
    return Number.isFinite(num) ? num : 0;
  });

  if (numeric.length === length) {
    return numeric;
  }

  if (numeric.length === 0) {
    return Array(length).fill(0);
  }

  if (numeric.length > length) {
    return numeric.slice(0, length);
  }

  const last = numeric[numeric.length - 1] ?? 0;
  return numeric.concat(Array(length - numeric.length).fill(last));
};

const DeviceSimulation = ({ userId: propUserId }) => {
  const userId = propUserId || localStorage.getItem("userId");
  const [rows, setRows] = useState(() => [
    { id: 1, device: "thermostat", start: 11, end: 18 },
  ]);
  const [baseline, setBaseline] = useState([]);
  const [simulated, setSimulated] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [error, setError] = useState(null);
  const [nextId, setNextId] = useState(2);

  const fetchBaseline = useCallback(
    async ({ showSpinner = true } = {}) => {
      if (!userId) {
        return [];
      }

      if (showSpinner) {
        setLoading(true);
        setStatusMessage("Loading baseline forecast…");
      }

      try {
        const resp = await fetchWithAuth(`http://localhost:5000/pred/${userId}`);
        if (!resp.ok) {
          throw new Error(`Baseline forecast failed (HTTP ${resp.status})`);
        }
        const json = await resp.json();
        const normalized = normalizeSeries(json, TARGET_LEN);
        setBaseline(normalized);
        if (showSpinner) {
          setStatusMessage("");
        }
        setError(null);
        return normalized;
      } catch (err) {
        console.error("Failed to fetch baseline forecast", err);
        const message = err instanceof Error ? err.message : "Failed to load baseline forecast.";
        setError(message);
        if (showSpinner) {
          setStatusMessage("");
        }
        return [];
      } finally {
        if (showSpinner) {
          setLoading(false);
        }
      }
    },
    [userId]
  );

  useEffect(() => {
    if (!userId) {
      setError("Missing user information. Please sign in again.");
      return;
    }
    fetchBaseline();
  }, [userId, fetchBaseline]);

  const handleRowChange = (id, field, value) => {
    setRows((prev) =>
      prev.map((row) =>
        row.id === id
          ? {
              ...row,
              [field]: field === "device" ? value : Number(value),
            }
          : row
      )
    );
  };

  const handleAddRow = () => {
    setRows((prev) => [
      ...prev,
      { id: nextId, device: "light", start: 9, end: 11 },
    ]);
    setNextId((prev) => prev + 1);
  };

  const handleRemoveRow = (id) => {
    setRows((prev) => (prev.length === 1 ? prev : prev.filter((row) => row.id !== id)));
  };

  const handleSimulate = async () => {
    setError(null);
    setStatusMessage("");

    if (!userId) {
      setError("Missing user information. Please sign in again.");
      return;
    }

    const sanitized = rows
      .map((row) => ({
        device: row.device,
        start: Number(row.start),
        end: Number(row.end),
      }))
      .filter((row) => {
        if (!DEVICE_OPTIONS.some((opt) => opt.value === row.device)) {
          return false;
        }
        if (!Number.isInteger(row.start) || !Number.isInteger(row.end)) {
          return false;
        }
        if (row.start < 0 || row.end < 0 || row.start > row.end || row.end > 23) {
          return false;
        }
        return true;
      });

    if (sanitized.length === 0) {
      setError("Please add at least one valid device interval (0-23 hours, end ≥ start).");
      return;
    }

    setLoading(true);
    setStatusMessage("Running simulation…");

    try {
      const baselineSeries = baseline.length > 0 ? baseline : await fetchBaseline({ showSpinner: false });
      if (baselineSeries.length === 0) {
        throw new Error("Baseline forecast is unavailable. Try again later.");
      }

      const payload = sanitized.map((row) => [row.device, row.start, row.end]);
      const scheduleParam = encodeURIComponent(JSON.stringify(payload));

      const resp = await fetchWithAuth(
        `http://localhost:5000/pred/simulate/${userId}/${scheduleParam}`
      );
      if (!resp.ok) {
        throw new Error(`Simulation failed (HTTP ${resp.status})`);
      }
      const simulatedJson = await resp.json();
      const simulatedSeries = normalizeSeries(simulatedJson, baselineSeries.length);
      setSimulated(simulatedSeries);

      const baselineAligned = normalizeSeries(baselineSeries, simulatedSeries.length);
      const baseTotal = baselineAligned.reduce((sum, value) => sum + value, 0);
      const simTotal = simulatedSeries.reduce((sum, value) => sum + value, 0);
      const baseCost = baseTotal * COST_PER_UNIT;
      const simCost = simTotal * COST_PER_UNIT;
      const diff = simCost - baseCost;
      const message =
        diff <= 0
          ? `Great! This schedule saves about ${Math.abs(diff).toFixed(2)} ${CURRENCY}.`
          : `Heads-up: this schedule adds roughly ${diff.toFixed(2)} ${CURRENCY}.`;

      setAnalysis({
        baseTotal,
        simTotal,
        baseCost,
        simCost,
        diff,
        schedule: sanitized,
        message,
      });

      setStatusMessage("Simulation ready.");
    } catch (err) {
      console.error("Device simulation failed", err);
      const message = err instanceof Error ? err.message : "Failed to run simulation.";
      setError(message);
      setAnalysis(null);
      setSimulated([]);
      setStatusMessage("");
    } finally {
      setLoading(false);
    }
  };

  const chartData = useMemo(() => {
    if (!baseline.length && !simulated.length) {
      return null;
    }
    const labels = HOURS.map((hour) => `${formatHour(hour)}:00`);
    const datasets = [
      {
        label: "Baseline forecast",
        data: baseline,
        borderColor: "#134675",
        backgroundColor: "rgba(19, 70, 117, 0.2)",
        tension: 0.3,
        pointRadius: 2,
      },
    ];

    if (simulated.length) {
      datasets.push({
        label: "With schedule",
        data: simulated,
        borderColor: "#ef476f",
        backgroundColor: "rgba(239, 71, 111, 0.2)",
        tension: 0.3,
        pointRadius: 2,
        borderDash: [6, 4],
      });
    }

    return { labels, datasets };
  }, [baseline, simulated]);

  const chartOptions = useMemo(
    () => ({
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "top" },
        title: { display: true, text: "24h demand forecast" },
      },
      scales: {
        x: {
          title: { display: true, text: "Hour" },
        },
        y: {
          title: { display: true, text: "Predicted demand" },
          beginAtZero: true,
        },
      },
    }),
    []
  );

  return (
    <div className="device-sim-page">
      <h1>Device Simulation</h1>
      <p className="page-intro">
        Build a schedule for connected devices and estimate the energy impact.
        Costs assume approximately {COST_PER_UNIT.toFixed(2)} {CURRENCY} per forecast
        unit.
      </p>

      <div className="schedule-card">
        <h2 className="section-title">Schedule</h2>
        {rows.map((row) => (
          <div key={row.id} className="schedule-row">
            <div className="field device-field">
              <label>Device</label>
              <select
                value={row.device}
                onChange={(e) => handleRowChange(row.id, "device", e.target.value)}
              >
                {DEVICE_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <span className="hint">
                {DEVICE_OPTIONS.find((opt) => opt.value === row.device)?.hint}
              </span>
            </div>
            <div className="field">
              <label>Start hour</label>
              <select
                value={row.start}
                onChange={(e) => handleRowChange(row.id, "start", e.target.value)}
              >
                {HOURS.map((hour) => (
                  <option key={hour} value={hour}>
                    {formatHour(hour)}:00
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label>End hour</label>
              <select
                value={row.end}
                onChange={(e) => handleRowChange(row.id, "end", e.target.value)}
              >
                {HOURS.map((hour) => (
                  <option key={hour} value={hour}>
                    {formatHour(hour)}:00
                  </option>
                ))}
              </select>
            </div>
            <button
              type="button"
              className="remove-btn"
              onClick={() => handleRemoveRow(row.id)}
              disabled={rows.length === 1}
            >
              Remove
            </button>
          </div>
        ))}

        <div className="schedule-actions">
          <button type="button" className="secondary-btn" onClick={handleAddRow}>
            + Add device
          </button>
          <button
            type="button"
            className="primary-btn"
            onClick={handleSimulate}
            disabled={loading}
          >
            {loading ? "Working…" : "Simulate"}
          </button>
        </div>
      </div>

      {statusMessage && <p className="status-message">{statusMessage}</p>}
      {error && <div className="error-box">{error}</div>}

      {analysis && (
        <div className="analysis-card">
          <h2 className="section-title">Results</h2>
          <div className="analysis-grid">
            <div>
              <span className="label">Baseline demand</span>
              <strong>{analysis.baseTotal.toFixed(1)} units</strong>
            </div>
            <div>
              <span className="label">Scheduled demand</span>
              <strong>{analysis.simTotal.toFixed(1)} units</strong>
            </div>
            <div>
              <span className="label">Baseline cost</span>
              <strong>{analysis.baseCost.toFixed(2)} {CURRENCY}</strong>
            </div>
            <div>
              <span className="label">Simulated cost</span>
              <strong>{analysis.simCost.toFixed(2)} {CURRENCY}</strong>
            </div>
          </div>
          <p className={`recommendation ${analysis.diff <= 0 ? "good" : "bad"}`}>
            {analysis.message}
          </p>
        </div>
      )}

      {chartData ? (
        <div className="chart-wrapper">
          <Line data={chartData} options={chartOptions} />
        </div>
      ) : (
        <div className="chart-placeholder">No forecast data available yet.</div>
      )}
    </div>
  );
};

export default DeviceSimulation;
