# data_processor.py

import os
import pandas as pd
import adjust_pv_module  # Your compiled C++ module
import json
import logging
from datetime import datetime

def load_config(config_path='config.json'):
	try:
		with open(config_path, 'r') as f:
			config = json.load(f)
	except FileNotFoundError:
		logging.error(f"Configuration file '{config_path}' not found. Please ensure it exists in the directory.")
		exit(1)
	except json.JSONDecodeError:
		logging.error(f"Configuration file '{config_path}' is not a valid JSON.")
		exit(1)
	
	# Validate required fields
	required_fields = ['SOLCAST_API_KEY', 'ROOFTOP_SITE_ID', 'OUTPUT_CSV', 'LATITUDE', 'LONGITUDE']
	missing_fields = [field for field in required_fields if field not in config]
	if missing_fields:
		logging.error(f"Missing configuration fields: {', '.join(missing_fields)}")
		exit(1)
	
	return config

def load_data(path):
	try:
		df = pd.read_csv(path)
		# Clean column names by stripping leading/trailing spaces
		df.columns = df.columns.str.strip()
		# Replace 'N/A' with NaN
		df.replace('N/A', pd.NA, inplace=True)
		# Convert relevant columns to numeric
		numeric_columns = ['PV Estimate', 'GHI', 'DNI', 'DHI', 'Temperature (C)', 
						   'Humidity (%)', 'Wind Speed (m/s)', 'Wind Direction (deg)', 'Cloud Cover (%)']
		for col in numeric_columns:
			if col in df.columns:
				df[col] = pd.to_numeric(df[col], errors='coerce')
		return df
	except FileNotFoundError:
		logging.error(f"The file '{path}' does not exist.")
		exit(1)
	except pd.errors.EmptyDataError:
		logging.error(f"The file '{path}' is empty.")
		exit(1)
	except Exception as e:
		logging.error(f"An error occurred while loading the data: {e}")
		exit(1)

def adjust_pv(df, column, multiplier):
	try:
		df[f'Adjusted_{column}'] = df.apply(
			lambda row: adjust_pv_module.adjust_pv_estimate(row[column] * multiplier) if pd.notnull(row[column]) else None,
			axis=1
		)
		return df
	except Exception as e:
		logging.error(f"An error occurred while adjusting PV estimates: {e}")
		exit(1)

def save_adjusted_data(df, original_csv_path, output_path=None):
	if not output_path:
		base, ext = os.path.splitext(os.path.basename(original_csv_path))  # Use only the base filename
		output_path = f"adjusted_{base}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
	
	try:
		df.to_csv(output_path, index=False)
		return output_path
	except Exception as e:
		logging.error(f"Failed to save adjusted data to CSV: {e}")
		exit(1)