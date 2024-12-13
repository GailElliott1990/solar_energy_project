const express = require('express');
const cors = require('cors');
const axios = require('axios');

// Log at startup to confirm environment variable availability
console.log("Starting application...");
console.log("NREL_API_KEY:", process.env.NREL_API_KEY);

const NREL_API_KEY = process.env.NREL_API_KEY;

// If NREL_API_KEY isn't set by the environment, log an error and exit
if (!NREL_API_KEY) {
  console.error("NREL_API_KEY is not set in environment variables.");
  process.exit(1);
}

const app = express();

// Configure CORS as needed. If your frontend is deployed elsewhere, update origins accordingly.
app.use(cors({
  origin: ['http://localhost:3000'] // Update this if your frontend is hosted elsewhere
}));

// NREL PVWatts API configuration
const LAT = 51.20578;
const LON = 3.47789;
const SYSTEM_CAPACITY = 4;
const DEFAULT_AZIMUTH = 180;
const DEFAULT_TILT = 40;
const ARRAY_TYPE = 1;
const MODULE_TYPE = 1;
const LOSSES = 10;
const NREL_API_URL = "https://developer.nrel.gov/api/pvwatts/v6.json";

app.get('/api/pvwatts', async (req, res) => {
  console.log("Received request to /api/pvwatts");
  try {
	const tilt_param = parseFloat(req.query.tilt) || DEFAULT_TILT;
	const azimuth_param = parseFloat(req.query.azimuth) || DEFAULT_AZIMUTH;

	const params = {
	  api_key: NREL_API_KEY,
	  lat: LAT,
	  lon: LON,
	  system_capacity: SYSTEM_CAPACITY,
	  azimuth: azimuth_param,
	  tilt: tilt_param,
	  array_type: ARRAY_TYPE,
	  module_type: MODULE_TYPE,
	  losses: LOSSES
	};

	console.log("Requesting PVWatts data from NREL with params:", params);

	const response = await axios.get(NREL_API_URL, { params, timeout: 15000 });
	const data = response.data;

	if (!data.outputs) {
	  console.warn("Unexpected data format received from NREL API.");
	  return res.status(502).json({ error: "Unexpected data format from NREL API" });
	}

	console.info("Data fetched successfully from NREL PVWatts API.");
	return res.status(200).json(data);

  } catch (error) {
	if (error.response) {
	  console.error("Failed to fetch data from NREL PVWatts API:", error.response.statusText);
	} else {
	  console.error("Unexpected error:", error.message);
	}
	return res.status(502).json({ error: "Failed to fetch data from NREL PVWatts API" });
  }
});

app.get('/', (req, res) => {
  console.log("Received request to /");
  res.send('Welcome to the Solar Energy Project API!');
});

// Use PORT from environment variables or default to 8080
const port = process.env.PORT || 8080;
app.listen(port, '0.0.0.0', () => {
  console.log(`Server running on port ${port}`);
});