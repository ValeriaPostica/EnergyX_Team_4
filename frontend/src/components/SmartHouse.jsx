import React, { useEffect, useState } from "react";
import "./SmartHouse.css";

function SmartHouse() {
  const [temperature, setTemperature] = useState(22);
  const [motion, setMotion] = useState(false);
  const [energyUsage, setEnergyUsage] = useState(3.5);

  // initial fetch + simulation will be handled in one effect below

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

  // initial fetch then simulation: smoothly change temperature -> 19, energyUsage -> 5.2, motion -> true over 60s
  useEffect(() => {
    let cancelled = false;
    const run = async () => {
      // initial fetch from server to get starting values
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

          (async () => {
      try {
        await fetch("http://localhost:5000/simple_log", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ line: `3)The current temperature is: ${temperature}°C; Motion detected: ${motion ? "Yes" : "No"}; Energy usage: ${energyUsage} kWh; The thermostat is ${thermostatOn ? "On" : "Off"}; The air conditioner is ${acOn ? "On" : "Off"}; The lights are ${lightsOn ? "On" : "Off"}; Energy saver mode is ${energySaverOn ? "On" : "Off"}` }),
        });
        console.log("Sent simple_log");
      } catch (err) {
        console.warn("Failed to send simple_log", err);
      }
    })();

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