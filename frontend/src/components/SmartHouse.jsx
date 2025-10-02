import React, { useEffect, useState } from "react";
import "./SmartHouse.css";

function SmartHouse() {
  const [temperature, setTemperature] = useState(22);
  const [motion, setMotion] = useState(false);
  const [energyUsage, setEnergyUsage] = useState(3.5);

  useEffect(() => {
    fetch("http://localhost:4000/api/status")
      .then((res) => res.json())
      .then((data) => {
        setTemperature(data.temperature);
        setMotion(data.motion);
        setEnergyUsage(Number(data.energyUsage));
      });
  }, []);

  const updateServer = async (field, value) => {
    const updated = {
      temperature,
      motion,
      energyUsage,
      [field]: value,
    };
    setTemperature(updated.temperature);
    setMotion(updated.motion);
    setEnergyUsage(updated.energyUsage);

    await fetch("http://localhost:4000/api/status", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updated),
    });
  };

  const thermostatOn = temperature < 20;
  const acOn = temperature > 25;
  const lightsOn = motion;
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
      </div>

      <div className="devices-grid">
        <div className="device-card">
          <div className={`bulb ${thermostatOn ? "on" : "off"}`} />
          <p>Thermostat: {thermostatOn ? "On" : "Off"}</p>
        </div>
        <div className="device-card">
          <div className={`bulb ${acOn ? "on" : "off"}`} />
          <p>Air Conditioner: {acOn ? "On" : "Off"}</p>
        </div>
        <div className="device-card">
          <div className={`bulb ${lightsOn ? "on" : "off"}`} />
          <p>Lights: {lightsOn ? "On" : "Off"}</p>
        </div>
        <div className="device-card">
          <div className={`bulb ${energySaverOn ? "on" : "off"}`} />
          <p>Energy Saver Mode: {energySaverOn ? "Active" : "Normal"}</p>
        </div>
      </div>
      <div className="note">
        <p>
          🌡️ Thermostat <b>On</b> if temperature is below 20°C.  
        </p>
        <p>
          ❄️ Air Conditioner <b>On</b> if temperature is above 25°C.  
        </p>
        <p>
          💡 Lights <b>On</b> if motion is detected.  
        </p>
        <p>
          ⚡ Energy Saver Mode <b>On</b> if usage is above 5 kWh.  
        </p>
      </div>
    </div>
  );
}

export default SmartHouse;
