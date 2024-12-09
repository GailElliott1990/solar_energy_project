# app.py

import os
import pandas as pd
import adjust_pv_module  # Your compiled C++ module
import json
import argparse
import logging
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Configure logging
logging.basicConfig(
	level=logging.INFO,
	format='%(levelname)s: %(message)s'
)

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

class PVAdjusterGUI:
	def __init__(self, root):
		self.root = root
		self.root.title("PV Estimate Adjuster")
		self.root.geometry("1000x700")
		
		# Initialize variables
		self.config = load_config()
		self.csv_path = self.config.get('OUTPUT_CSV', '/Users/jasonnewton/Documents/python/solar_energy_project/backend/data_fetching/solar_forecasts.csv')
		self.multiplier = tk.DoubleVar(value=1.0)
		self.column_to_adjust = tk.StringVar()
		self.df_original = load_data(self.csv_path)
		self.df_adjusted = self.df_original.copy()
		
		# Create UI components
		self.create_widgets()
	
	def create_widgets(self):
		# Frame for Multiplier Slider
		slider_frame = ttk.LabelFrame(self.root, text="Multiplier Adjustment")
		slider_frame.pack(pady=10, padx=10, fill='x')
		
		ttk.Label(slider_frame, text="Adjust Multiplier:").pack(side='left', padx=(10, 10))
		multiplier_slider = ttk.Scale(
			slider_frame,
			from_=0.5,
			to=2.0,
			orient='horizontal',
			variable=self.multiplier,
			command=self.update_multiplier_label
		)
		multiplier_slider.pack(side='left', fill='x', expand=True, padx=(0, 10))
		
		self.multiplier_label = ttk.Label(slider_frame, text="1.00")
		self.multiplier_label.pack(side='left', padx=(10, 10))
		
		# Frame for Column Selection
		column_frame = ttk.LabelFrame(self.root, text="Column Selection")
		column_frame.pack(pady=10, padx=10, fill='x')
		
		ttk.Label(column_frame, text="Select Column to Adjust:").pack(side='left', padx=(10, 10))
		column_options = [col for col in self.df_original.columns if pd.api.types.is_numeric_dtype(self.df_original[col])]
		if 'PV Estimate' in column_options:
			default_column = 'PV Estimate'
		elif column_options:
			default_column = column_options[0]
		else:
			default_column = None
		
		if not default_column:
			messagebox.showerror("Error", "No numeric columns available for adjustment.")
			self.root.destroy()
			return
		
		self.column_to_adjust.set(default_column)
		column_menu = ttk.OptionMenu(column_frame, self.column_to_adjust, default_column, *column_options, command=self.on_column_change)
		column_menu.pack(side='left', fill='x', expand=True, padx=(0, 10))
		
		# Frame for Buttons
		button_frame = ttk.Frame(self.root)
		button_frame.pack(pady=10, padx=10, fill='x')
		
		adjust_button = ttk.Button(button_frame, text="Adjust PV Estimates", command=self.adjust_pv_estimates)
		adjust_button.pack(side='left', padx=(10, 10))
		
		save_button = ttk.Button(button_frame, text="Save Adjusted CSV", command=self.save_adjusted_csv)
		save_button.pack(side='left', padx=(10, 10))
		
		load_button = ttk.Button(button_frame, text="Load CSV", command=self.load_new_csv)
		load_button.pack(side='left', padx=(10, 10))
		
		# Frame for Plotting
		plot_frame = ttk.LabelFrame(self.root, text="PV Estimates Comparison")
		plot_frame.pack(pady=10, padx=10, fill='both', expand=True)
		
		self.figure, self.ax = plt.subplots(figsize=(10, 5))
		self.canvas = FigureCanvasTkAgg(self.figure, master=plot_frame)
		self.canvas.get_tk_widget().pack(fill='both', expand=True)
		
		# Initial Plot
		self.plot_data()
	
	def update_multiplier_label(self, event):
		self.multiplier_label.config(text=f"{self.multiplier.get():.2f}")
	
	def on_column_change(self, event):
		self.plot_data()
	
	def adjust_pv_estimates(self):
		column = self.column_to_adjust.get()
		multiplier = self.multiplier.get()
		
		if not column:
			messagebox.showerror("Error", "No column selected for adjustment.")
			return
		
		try:
			self.df_adjusted = adjust_pv(self.df_original.copy(), column, multiplier)
			messagebox.showinfo("Success", f"PV estimates adjusted with multiplier {multiplier:.2f}.")
			self.plot_data()
		except Exception as e:
			messagebox.showerror("Error", f"An error occurred: {e}")
	
	def save_adjusted_csv(self):
		if 'Adjusted_' not in self.df_adjusted.columns:
			messagebox.showwarning("Warning", "No adjusted data to save. Please adjust PV estimates first.")
			return
		
		output_path = filedialog.asksaveasfilename(
			defaultextension=".csv",
			filetypes=[("CSV files", "*.csv")],
			initialfile=f"adjusted_{os.path.basename(self.csv_path)}"
		)
		
		if output_path:
			try:
				self.df_adjusted.to_csv(output_path, index=False)
				messagebox.showinfo("Success", f"Adjusted data saved to '{output_path}'.")
			except Exception as e:
				messagebox.showerror("Error", f"Failed to save adjusted data: {e}")
	
	def load_new_csv(self):
		file_path = filedialog.askopenfilename(
			filetypes=[("CSV files", "*.csv")],
			title="Select CSV File"
		)
		if file_path:
			try:
				self.df_original = load_data(file_path)
				self.df_adjusted = self.df_original.copy()
				self.csv_path = file_path
				logging.info(f"Loaded new CSV file: {file_path}")
				
				# Update column options
				column_menu = [child for child in self.root.winfo_children() if isinstance(child, ttk.LabelFrame) and child['text'] == "Column Selection"]
				if column_menu:
					column_menu = column_menu[0]
					menu = column_menu.winfo_children()[1]['menu']
					menu.delete(0, 'end')
					column_options = [col for col in self.df_original.columns if pd.api.types.is_numeric_dtype(self.df_original[col])]
					for col in column_options:
						menu.add_command(label=col, command=lambda value=col: self.column_to_adjust.set(value))
					if 'PV Estimate' in column_options:
						default_column = 'PV Estimate'
					elif column_options:
						default_column = column_options[0]
					else:
						default_column = None
					
					if default_column:
						self.column_to_adjust.set(default_column)
					else:
						messagebox.showerror("Error", "No numeric columns available for adjustment.")
						return
				self.plot_data()
				messagebox.showinfo("Success", f"Loaded new CSV file: {file_path}")
			except Exception as e:
				messagebox.showerror("Error", f"Failed to load CSV file: {e}")
	
	def plot_data(self):
		column = self.column_to_adjust.get()
		if not column:
			return
		
		self.ax.clear()
		self.ax.plot(self.df_original['Period End'], self.df_original[column], label='Original', color='blue')
		
		if f'Adjusted_{column}' in self.df_adjusted.columns:
			self.ax.plot(self.df_adjusted['Period End'], self.df_adjusted[f'Adjusted_{column}'], label='Adjusted', color='orange')
		
		self.ax.set_xlabel('Period End')
		self.ax.set_ylabel(column)
		self.ax.set_title(f"{column} Comparison")
		self.ax.legend()
		self.figure.autofmt_xdate()
		self.canvas.draw()

def main():
	root = tk.Tk()
	app = PVAdjusterGUI(root)
	root.mainloop()

if __name__ == "__main__":
	main()