import React, { useEffect, useState } from "react";
import "./SmartHouse.css";

function SmartHouse() {
  const [temperature, setTemperature] = useState(22);
  const [motion, setMotion] = useState(false);
  const [energyUsage, setEnergyUsage] = useState(3.5);
  const [prevEnergyUsage, setPrevEnergyUsage] = useState(3.5); // FIXED: missing declaration
  const [userName] = useState("Ioana Vasilescu"); 
  const [pointsMessage, setPointsMessage] = useState("");

  // ADDED: Manual toggles for AC and Lights
  const [air_conditioner, setAcOn] = useState(false);
  const [lights, setLightsOn] = useState(false);


  const [prevThermostat, setPrevThermostat] = useState(temperature < 20 );
  // helper to POST an updated status object to the server
  const postStatusObject = async (updated) => {
    try {
      await fetch("http://localhost:4000/api/status", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updated),
      });
    } catch (e) {
      console.warn("Failed to POST status", e);
    }
  };

  // helper to fetch current status from server and apply to component state
  const fetchStatus = async () => {
    try {
      const res = await fetch("http://localhost:4000/api/status");
      const data = await res.json();
      setTemperature(data.temperature);
      setMotion(data.motion);
      setEnergyUsage(Number(data.energyUsage));
      return data;
    } catch (e) {
      console.warn("Failed to fetch status", e);
      return null;
    }
  };

  /*useEffect(() => {
    let cancelled = false;
    const run = async () => {
      const initial = await fetchStatus();
      if (cancelled || !initial) return;

      const startTemp = Number(initial.temperature);
      const startEnergy = Number(initial.energyUsage);
      const targetTemp = 19;
      const targetEnergy = 5.2;
      const targetMotion = true;

      const durationMs = 60 * 1000;
      const steps = 60;
      const intervalMs = Math.floor(durationMs / steps);

      let step = 0;
      const id = setInterval(async () => {
        if (cancelled) return;
        step += 1;
        const t = Math.min(step / steps, 1);
        const newTemp = startTemp + (targetTemp - startTemp) * t;
        const newEnergy = startEnergy + (targetEnergy - startEnergy) * t;
        const updated = {
          temperature: Number(newTemp.toFixed(2)),
          motion: targetMotion,
          energyUsage: Number(newEnergy.toFixed(2)),
        };

        await postStatusObject(updated);
        await fetchStatus();

        if (step >= steps) {
          clearInterval(id);
        }
      }, intervalMs);
    };

    run();
    return () => { cancelled = true; };
  }, []); */

  const updateServer = async (field, value) => {
    const updated = {
      temperature,
      motion,
      energyUsage,
      [field]: value,
    };

    if (field === "energyUsage") {
      setPrevEnergyUsage(energyUsage); // Track previous usage
    }

    if (field === "temperature") {
      const newThermostat = value < 20;
      if (newThermostat !== prevThermostat) {
        setPrevThermostat(newThermostat);
      }
    }

    setTemperature(updated.temperature);
    setMotion(updated.motion);
    setEnergyUsage(updated.energyUsage);

    await fetch("http://localhost:4000/api/status", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updated),
    });

    const payload = {
      user: userName,
      energy_usage: updated.energyUsage,
      previous_energy_usage: prevEnergyUsage,
      thermostat: updated.temperature < 20,
      air_conditioner,
      lights,
      energy_saving_mode: updated.energyUsage > 5,
    };

    try {
      const res = await fetch("http://localhost:5000/calculate/smart_house_points", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (data.earned_points !== 0) {
        const earnedLabel = Math.abs(data.earned_points) === 1 ? "point" : "points";
        const totalLabel = data.total_points === 1 ? "point" : "points";
        const verb = data.earned_points < 0 ? "lost" : "earned";
        setPointsMessage(`You ${verb} ${Math.abs(data.earned_points)} ${earnedLabel}! Total: ${data.total_points} ${totalLabel}`);
      } else {
        setPointsMessage("");
      }
    } catch (err) {
      console.warn("Failed to calculate points", err);
    }
  };

  const thermostatOn = temperature < 20;
  const energySaverOn = energyUsage > 5;

  return (
    <div className="smart-house-container">
      <h2>Smart House IoT (with Server)</h2>

      <div className="controls">
        <div>
          <label>Temperature (°C): </label>
          <input
            type="number"
            value={temperature}
            onChange={(e) => updateServer("temperature", Number(e.target.value))}
          />
        </div>

        <div>
          <label>Energy usage (kWh): </label>
          <input
            type="number"
            step="0.1"
            value={energyUsage}
            onChange={(e) => updateServer("energyUsage", Number(e.target.value))}
          />
        </div>

        <div>
          <label>Motion detected: </label>
          <input
            type="checkbox"
            checked={motion}
            onChange={(e) => updateServer("motion", e.target.checked)}
          />
        </div>

        {/* Manual toggles for AC and Lights */}
        <div>
          <label>Air Conditioner: </label>
          <input
            type="checkbox"
            checked={air_conditioner}
            onChange={(e) => setAcOn(e.target.checked)}
          />
        </div>

        <div>
          <label>Lights: </label>
          <input
            type="checkbox"
            checked={lights}
            onChange={(e) => setLightsOn(e.target.checked)}
          />
        </div>
      </div>

      {/* Display points message */}
      {pointsMessage && (
        <div className="points-box">
          <p className={`points-message ${pointsMessage.includes("lost") ? "negative" : "positive"}`}>
            {pointsMessage}
          </p>
        </div>
      )}

      <div className="devices-grid">
        <div className="device-card">
          <div className={`bulb ${thermostatOn ? "on" : "off"}`} />
          <p>Thermostat: {thermostatOn ? "On" : "Off"}</p>
        </div>
        <div className="device-card">
          <div className={`bulb ${air_conditioner ? "on" : "off"}`} />
          <p>Air Conditioner: {air_conditioner ? "On" : "Off"}</p>
        </div>
        <div className="device-card">
          <div className={`bulb ${lights ? "on" : "off"}`} />
          <p>Lights: {lights ? "On" : "Off"}</p>
        </div>
        <div className="device-card">
          <div className={`bulb ${energySaverOn ? "on" : "off"}`} />
          <p>Energy Saver Mode: {energySaverOn ? "Active" : "Normal"}</p>
        </div>
      </div>
      <div className="note">
        <p>🌡️ Thermostat <b>On</b> if temperature is below 20°C.</p>
        <p>❄️ Air Conditioner <b>On</b> if temperature is above 25°C.</p>
        <p>💡 Lights <b>On</b> if motion is detected.</p>
        <p>⚡ Energy Saver Mode <b>On</b> if usage is above 5 kWh.</p>
      </div>
    </div>
  );
}

export default SmartHouse;
