import React from 'react';

function AzimuthSlider({ azimuth, onAzimuthChange }) {
  const handleChange = (event) => {
	onAzimuthChange(Number(event.target.value));
  };

  return (
	<div>
	  <h2>Set Azimuth</h2>
	  <input
		type="range"
		min="0"
		max="360"
		step="1"
		value={azimuth}
		onChange={handleChange}
	  />
	  <p>Current Azimuth: {azimuth}°</p>
	</div>
  );
}

export default AzimuthSlider;