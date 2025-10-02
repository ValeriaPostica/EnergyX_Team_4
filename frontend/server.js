import express from "express";
import cors from "cors";

const app = express();
app.use(cors());
app.use(express.json()); 

let status = {
  temperature: 22,
  motion: false,
  energyUsage: 3.5
};

app.get("/api/status", (req, res) => {
  res.json(status);
});

app.post("/api/status", (req, res) => {
  const { temperature, motion, energyUsage } = req.body;
  if (temperature !== undefined) status.temperature = temperature;
  if (motion !== undefined) status.motion = motion;
  if (energyUsage !== undefined) status.energyUsage = energyUsage;
  res.json({ success: true, status });
});

app.listen(4000, () => {
  console.log("IoT server running at http://localhost:4000");
});
