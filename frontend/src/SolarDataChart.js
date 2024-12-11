// src/SolarForecastChart.js

import React, { useRef } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  TimeScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import 'chartjs-adapter-date-fns';
import { Line } from 'react-chartjs-2';

// Import the CSS file
import './SolarDataChart.css';

// Register Chart.js components and plugins
ChartJS.register(
  CategoryScale,
  LinearScale,
  TimeScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const SolarForecastChart = ({ data, tilt, azimuth }) => {
  // Reference to the chart instance
  const chartRef = useRef(null);

  // Extract labels and datasets from the data prop
  const labels = data.map((entry) => new Date(entry.period_end));
  const acData = data.map((entry) => entry.ac_value);
  const poaData = data.map((entry) => entry.poa_value);

  // Define the maximum Y-axis value for a bit of headroom
  const maxY = Math.max(...acData, ...poaData, 1) * 1.2;

  const chartData = {
	labels,
	datasets: [
	  {
		label: 'AC Monthly',
		data: acData,
		borderColor: 'rgba(75, 192, 192, 1)',
		backgroundColor: 'rgba(75, 192, 192, 0.2)',
		fill: true,
		tension: 0.4,
		pointRadius: 0,
	  },
	  {
		label: 'POA Monthly',
		data: poaData,
		borderColor: 'rgba(153, 102, 255, 1)',
		backgroundColor: 'rgba(153, 102, 255, 0.2)',
		fill: true,
		tension: 0.4,
		pointRadius: 0,
	  },
	],
  };

  const chartOptions = {
	responsive: true,
	interaction: {
	  mode: 'index',
	  intersect: false,
	},
	scales: {
	  x: {
		type: 'time',
		time: {
		  unit: 'month',
		  tooltipFormat: 'MMM yyyy',
		  displayFormats: {
			month: 'MMM yyyy',
		  },
		},
		title: {
		  display: true,
		  text: 'Month',
		},
	  },
	  y: {
		beginAtZero: true,
		max: maxY,
		title: {
		  display: true,
		  text: 'Value',
		},
	  },
	},
	plugins: {
	  legend: {
		position: 'top',
	  },
	  title: {
		display: true,
		text: `Solar Data (Tilt: ${tilt}°, Azimuth: ${azimuth}°)`,
	  },
	  tooltip: {
		enabled: true,
		mode: 'nearest',
		intersect: false,
	  },
	},
  };

  return (
	<div className="chart-container">
	  <Line ref={chartRef} options={chartOptions} data={chartData} />
	</div>
  );
};

export default SolarForecastChart;