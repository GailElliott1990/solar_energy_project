import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.dates as mdates
import tkinter.font as tkFont
import seaborn as sns
import logging
import pandas as pd
from datetime import datetime
import adjust_pv_module  # Ensure this is correctly placed in the simulation/ directory

# Configure logging
logging.basicConfig(filename='gui_debug.log',
					level=logging.DEBUG,
					format='%(asctime)s:%(levelname)s:%(message)s')

def adjust_pv(df, column, multiplier, azimuth, tilt, log_widget=None):
	"""
	Adjusts the PV estimates in the DataFrame based on the multiplier, azimuth, and tilt.
	Logs each adjustment to the provided log_widget.
	"""
	logging.debug(f"Adjusting PV for column '{column}' with multiplier={multiplier}, azimuth={azimuth}, and tilt={tilt}")
	try:
		adjusted_values = []
		for index, value in df[column].items():
			adjusted = adjust_pv_module.adjust_pv_estimate(value, multiplier, azimuth, tilt)
			adjusted_values.append(adjusted)
			if log_widget:
				log_widget.config(state='normal')  # Enable the widget to insert text
				log_widget.insert(tk.END, f"Row {index}: Original = {value}, Adjusted = {adjusted}\n")
				log_widget.see(tk.END)  # Auto-scroll to the end
				log_widget.config(state='disabled')  # Disable the widget again
		df[f'Adjusted_{column}'] = adjusted_values
		logging.debug("PV adjustment successful.")
	except Exception as e:
		logging.error(f"Error adjusting PV: {e}")
		if log_widget:
			log_widget.config(state='normal')  # Enable the widget to insert text
			log_widget.insert(tk.END, f"Error adjusting PV: {e}\n")
			log_widget.see(tk.END)  # Auto-scroll to the end
			log_widget.config(state='disabled')  # Disable the widget again
	return df

class PVAdjusterGUI:
	def __init__(self, root):
		self.root = root
		self.root.title("PV Estimate Adjuster")
		self.root.geometry("1200x800")
		
		# Set up custom font
		self.custom_font = tkFont.Font(family="Helvetica", size=14)
		
		# Initialize variables
		self.multiplier = tk.DoubleVar(value=1.0)  # Initial multiplier value
		self.azimuth = tk.DoubleVar(value=180.0)    # Initial azimuth value
		self.tilt = tk.DoubleVar(value=30.0)         # Initial tilt value
		self.column_to_adjust = tk.StringVar()
		
		# Load data
		try:
			self.df_original = pd.read_csv('solar_forecasts.csv', parse_dates=['Period End'])
			self.df_adjusted = self.df_original.copy()
			logging.debug("Data loaded successfully.")
		except Exception as e:
			logging.error(f"Failed to load data: {e}")
			messagebox.showerror("Error", f"Failed to load data: {e}")
			self.root.destroy()
			return
		
		# Create GUI widgets
		self.create_widgets()
	
	def create_widgets(self):
		"""Create and layout all GUI widgets."""
		# Frame for controls
		controls_frame = ttk.Frame(self.root)
		controls_frame.pack(pady=10, padx=10, fill='x')
		
		# Multiplier Adjustment Frame
		multiplier_frame = ttk.LabelFrame(controls_frame, text="Multiplier Adjustment")
		multiplier_frame.pack(side='left', padx=(0, 10), fill='x', expand=True)
		
		ttk.Label(multiplier_frame, text="Adjust Multiplier:", font=self.custom_font).pack(side='left', padx=(10, 10))
		multiplier_slider = ttk.Scale(
			multiplier_frame,
			from_=0.5,
			to=2.0,
			orient='horizontal',
			variable=self.multiplier,
			command=self.update_adjustments  # Handler for slider movement
		)
		multiplier_slider.pack(side='left', fill='x', expand=True, padx=(0, 10))
		
		self.multiplier_label = ttk.Label(multiplier_frame, text="1.00", font=self.custom_font)
		self.multiplier_label.pack(side='left', padx=(10, 10))
		
		# Azimuth Adjustment Frame
		azimuth_frame = ttk.LabelFrame(controls_frame, text="Azimuth Adjustment")
		azimuth_frame.pack(side='left', padx=(10, 0), fill='x', expand=True)
		
		ttk.Label(azimuth_frame, text="Adjust Azimuth (degrees):", font=self.custom_font).pack(side='left', padx=(10, 10))
		azimuth_slider = ttk.Scale(
			azimuth_frame,
			from_=0.0,
			to=360.0,
			orient='horizontal',
			variable=self.azimuth,
			command=self.update_adjustments  # Handler for slider movement
		)
		azimuth_slider.pack(side='left', fill='x', expand=True, padx=(0, 10))
		
		self.azimuth_label = ttk.Label(azimuth_frame, text="180.00°", font=self.custom_font)
		self.azimuth_label.pack(side='left', padx=(10, 10))
		
		# Tilt Adjustment Frame
		tilt_frame = ttk.LabelFrame(controls_frame, text="Tilt Adjustment")
		tilt_frame.pack(side='left', padx=(10, 0), fill='x', expand=True)
		
		ttk.Label(tilt_frame, text="Adjust Tilt (degrees):", font=self.custom_font).pack(side='left', padx=(10, 10))
		tilt_slider = ttk.Scale(
			tilt_frame,
			from_=0.0,
			to=90.0,
			orient='horizontal',
			variable=self.tilt,
			command=self.update_adjustments  # Handler for slider movement
		)
		tilt_slider.pack(side='left', fill='x', expand=True, padx=(0, 10))
		
		self.tilt_label = ttk.Label(tilt_frame, text="30.00°", font=self.custom_font)
		self.tilt_label.pack(side='left', padx=(10, 10))
		
		# Column Selection Frame
		column_frame = ttk.LabelFrame(controls_frame, text="Column Selection")
		column_frame.pack(side='left', padx=(10, 0), fill='x', expand=True)
		
		ttk.Label(column_frame, text="Select Column to Adjust:", font=self.custom_font).pack(side='left', padx=(10, 10))
		column_options = [col for col in self.df_original.columns if pd.api.types.is_numeric_dtype(self.df_original[col])]
		logging.debug(f"Numeric columns available: {column_options}")
		if 'PV Estimate' in column_options:
			default_column = 'PV Estimate'
		elif column_options:
			default_column = column_options[0]
		else:
			default_column = None
		
		if not default_column:
			logging.error("No numeric columns available for adjustment.")
			messagebox.showerror("Error", "No numeric columns available for adjustment.")
			self.root.destroy()
			return
		
		self.column_to_adjust.set(default_column)
		column_menu = ttk.OptionMenu(column_frame, self.column_to_adjust, default_column, *column_options, command=self.on_column_change)
		column_menu.pack(side='left', fill='x', expand=True, padx=(0, 10))
	
		# Create PanedWindow to separate log and plot
		paned_window = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
		paned_window.pack(pady=10, padx=10, fill='both', expand=True)
	
		# Frame for Real-Time Adjustment Log (Summary)
		log_frame = ttk.LabelFrame(paned_window, text="Real-Time PV Adjustments Summary")
		
		# Add Scrollbar to Text Widget
		scrollbar = ttk.Scrollbar(log_frame, orient='vertical')
		self.log_text = tk.Text(log_frame, height=35, wrap='word', font=('Helvetica', 14), state='disabled', yscrollcommand=scrollbar.set)
		self.log_text.pack(side='left', fill='both', expand=True)
		scrollbar.config(command=self.log_text.yview)
		scrollbar.pack(side='right', fill='y')
	
		# Optional: Add a Clear Log button
		clear_log_button = ttk.Button(log_frame, text="Clear Log", command=self.clear_log)
		clear_log_button.pack(side='right', padx=5, pady=5)
	
		# Add log_frame to PanedWindow
		paned_window.add(log_frame, weight=1)  # Weight determines the relative size
	
		# Frame for Plotting
		plot_frame = ttk.LabelFrame(paned_window, text="PV Estimates Comparison")
		
		self.figure, self.ax = plt.subplots(figsize=(16, 8))  # Increased figure size
		self.canvas = FigureCanvasTkAgg(self.figure, master=plot_frame)
		self.canvas.get_tk_widget().pack(fill='both', expand=True)
		
		# Add Navigation Toolbar
		toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
		toolbar.update()
		self.canvas._tkcanvas.pack(fill='both', expand=True)
		
		# Add plot_frame to PanedWindow
		paned_window.add(plot_frame, weight=3)  # Adjust weight as needed for initial sizes

		# Initial Plot
		self.plot_data()
		logging.debug("GUI widgets created successfully.")

	def clear_log(self):
		"""Clear the Real-Time PV Adjustments Summary Text widget."""
		if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear the log?"):
			self.log_text.config(state='normal')  # Make the widget editable
			self.log_text.delete('1.0', tk.END)  # Delete all content
			self.log_text.config(state='disabled')  # Make the widget read-only again

	def update_adjustments(self, event):
		"""Update the multiplier, azimuth, and tilt labels and adjust the PV estimates in real-time."""
		current_multiplier = self.multiplier.get()
		current_azimuth = self.azimuth.get()
		current_tilt = self.tilt.get()
		self.multiplier_label.config(text=f"{current_multiplier:.2f}")
		self.azimuth_label.config(text=f"{current_azimuth:.2f}°")
		self.tilt_label.config(text=f"{current_tilt:.2f}°")
		
		# Perform real-time adjustment
		column = self.column_to_adjust.get()
		if column:
			logging.debug(f"Real-time adjusting PV estimates for column '{column}' with multiplier {current_multiplier}, azimuth {current_azimuth}, and tilt {current_tilt}")
			self.df_adjusted = adjust_pv(
				self.df_original.copy(),
				column,
				current_multiplier,
				current_azimuth,
				current_tilt,  # Pass tilt
				log_widget=self.log_text
			)
			self.plot_data()  # Update the plot with new adjusted values
			self.save_adjusted_csv(overwrite=True)  # Automatically save the adjusted data

	def on_column_change(self, event):
		"""Handle changes in the column selection dropdown."""
		self.plot_data()

	def save_adjusted_csv(self, overwrite=False):
		"""Automatically save the adjusted CSV."""
		if not any(col.startswith('Adjusted_') for col in self.df_adjusted.columns):
			logging.warning("No adjusted data to save.")
			return
		
		output_path = 'adjusted_solar_forecasts.csv' if not overwrite else 'solar_forecasts.csv'  # Overwrite original
		try:
			self.df_adjusted.to_csv(output_path, index=False)
			logging.debug(f"Adjusted data saved to {output_path if not overwrite else 'solar_forecasts.csv'}")
			if overwrite:
				# Reload data to reflect saved changes
				self.reload_data()
		except Exception as e:
			logging.error(f"Failed to save adjusted data: {e}")

	def plot_data(self):
		"""Plot the original and adjusted PV estimates."""
		column = self.column_to_adjust.get()
		if not column:
			logging.warning("No column selected for plotting.")
			return
		
		logging.debug(f"Plotting data for column '{column}'")
		
		self.ax.clear()
		
		# Plot Original Data
		self.ax.plot(
			self.df_original['Period End'], 
			self.df_original[column], 
			label='Original', 
			color='blue'
		)
		
		# Plot Adjusted Data if available
		adjusted_column = f'Adjusted_{column}'
		if adjusted_column in self.df_adjusted.columns:
			self.ax.plot(
				self.df_adjusted['Period End'], 
				self.df_adjusted[adjusted_column], 
				label='Adjusted', 
				color='orange'
			)
		
		# Formatting the x-axis with date formats
		self.ax.set_xlabel('Period End', fontsize=16, fontweight='bold')  # Increased font size
		self.ax.set_ylabel(column, fontsize=16, fontweight='bold')  # Increased font size
		self.ax.set_title(f"{column} Comparison", fontsize=18, fontweight='bold')  # Increased font size
		self.ax.legend(fontsize=14)  # Increased legend font size
		
		date_format = mdates.DateFormatter('%Y-%m-%d\n%H:%M')
		self.ax.xaxis.set_major_formatter(date_format)
		
		locator = mdates.AutoDateLocator()
		self.ax.xaxis.set_major_locator(locator)
		
		self.figure.autofmt_xdate(rotation=45, ha='right')
		self.figure.tight_layout()
		
		self.canvas.draw()
		logging.debug("Data plotted successfully.")

	def reload_data(self):
		"""Reload the CSV data and update the GUI."""
		logging.debug("Reloading data from CSV.")
		try:
			# Reload the original data
			self.df_original = pd.read_csv('solar_forecasts.csv', parse_dates=['Period End'])
			self.df_adjusted = self.df_original.copy()
			
			# Re-apply any existing adjustments
			current_multiplier = self.multiplier.get()
			current_azimuth = self.azimuth.get()
			current_tilt = self.tilt.get()
			column = self.column_to_adjust.get()
			if column:
				logging.debug(f"Re-applying multiplier {current_multiplier}, azimuth {current_azimuth}, and tilt {current_tilt} to column '{column}'.")
				self.df_adjusted = adjust_pv(
					self.df_original.copy(),
					column,
					current_multiplier,
					current_azimuth,
					current_tilt,
					log_widget=self.log_text
				)
			
			# Update the plot with the new data
			self.plot_data()
			
			logging.debug("Data reloaded and GUI updated successfully.")
		except Exception as e:
			logging.error(f"Failed to reload data: {e}")
			messagebox.showerror("Error", f"Failed to reload data: {e}")

	def on_close(self):
		"""Handle the closing of the application."""
		logging.debug("Closing application.")
		self.root.destroy()

def main():
	logging.debug("Starting GUI application.")
	root = tk.Tk()
	app = PVAdjusterGUI(root)
	root.protocol("WM_DELETE_WINDOW", app.on_close)
	root.mainloop()
	logging.debug("GUI application closed.")

if __name__ == "__main__":
	main()