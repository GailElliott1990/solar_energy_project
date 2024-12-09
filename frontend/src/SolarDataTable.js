// src/SolarForecastTable.js

import React from 'react';
import './SolarDataTable.css'; // Import the CSS for table styling

function SolarForecastTable({ data }) {
  // Helper function to determine if a value is numeric and non-zero
  const isNumericAndNonZero = (value) => {
	return typeof value === 'number' && value !== 0;
  };

  return (
	<div className="table-container">
	  <table>
		<thead>
		  <tr>
			<th>Period End</th>
			<th>AC Monthly</th>
			<th>POA Monthly</th>
			<th>SOLRAD Monthly</th>
		  </tr>
		</thead>
		<tbody>
		  {data.map((entry, index) => (
			<tr key={index}>
			  <td>{new Date(entry.period_end).toLocaleString()}</td>
			  <td
				className={
				  isNumericAndNonZero(entry.ac_value)
					? 'highlight'
					: ''
				}
			  >
				{entry.ac_value.toFixed(2)}
			  </td>
			  <td
				className={
				  isNumericAndNonZero(entry.poa_value)
					? 'highlight'
					: ''
				}
			  >
				{entry.poa_value.toFixed(2)}
			  </td>
			  <td
				className={
				  isNumericAndNonZero(entry.solrad_value)
					? 'highlight'
					: ''
				}
			  >
				{entry.solrad_value.toFixed(2)}
			  </td>
			</tr>
		  ))}
		</tbody>
	  </table>
	</div>
  );
}

export default SolarForecastTable;