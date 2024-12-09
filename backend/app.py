from flask import Flask, jsonify, request
from flask_caching import Cache
from flask_cors import CORS
import requests
import logging
import traceback
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from the environment
NREL_API_KEY = os.environ.get("NREL_API_KEY")

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000"]}})

# Configure caching (in-memory cache)
cache = Cache(config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})
cache.init_app(app)

logging.basicConfig(
	level=logging.DEBUG,
	format="%(asctime)s %(levelname)s %(message)s",
	datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# NREL PVWatts API configuration
LAT = 51.20578
LON = 3.47789
SYSTEM_CAPACITY = 4
DEFAULT_AZIMUTH = 180
DEFAULT_TILT = 40
ARRAY_TYPE = 1
MODULE_TYPE = 1
LOSSES = 10
NREL_API_URL = "https://developer.nrel.gov/api/pvwatts/v6.json"

@app.route('/api/pvwatts', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_pvwatts_data():
	try:
		# Get tilt and azimuth from query parameters, fallback to defaults if not provided
		tilt_param = request.args.get('tilt', DEFAULT_TILT, type=float)
		azimuth_param = request.args.get('azimuth', DEFAULT_AZIMUTH, type=float)

		params = {
			"api_key": NREL_API_KEY,
			"lat": LAT,
			"lon": LON,
			"system_capacity": SYSTEM_CAPACITY,
			"azimuth": azimuth_param,
			"tilt": tilt_param,
			"array_type": ARRAY_TYPE,
			"module_type": MODULE_TYPE,
			"losses": LOSSES
		}

		logger.debug(f"Requesting PVWatts data from NREL with params: {params}")
		
		response = requests.get(NREL_API_URL, params=params, timeout=15)
		response.raise_for_status()
		data = response.json()

		if "outputs" not in data:
			logger.warning("Unexpected data format received from NREL API.")
			return jsonify({"error": "Unexpected data format from NREL API"}), 502

		logger.info("Data fetched successfully from NREL PVWatts API.")
		return jsonify(data), 200

	except requests.exceptions.RequestException as e:
		logger.error(f"Failed to fetch data from NREL PVWatts API: {e}")
		return jsonify({"error": "Failed to fetch data from NREL PVWatts API"}), 502
	except Exception as e:
		logger.error(f"Unexpected error: {e}\n{traceback.format_exc()}")
		return jsonify({"error": "An unexpected error occurred."}), 500

if __name__ == '__main__':
	# Make sure you run this from the directory where app.py and .env are located.
	app.run(debug=True, host="0.0.0.0", port=5001)