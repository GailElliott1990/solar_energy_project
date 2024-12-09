import React from 'react';

function TiltSlider({ tilt, onTiltChange }) {
  const handleChange = (event) => {
	onTiltChange(Number(event.target.value));
  };

  return (
	<div>
	  <h2>Set Tilt</h2>
	  <input
		type="range"
		min="0"
		max="90"
		step="1"
		value={tilt}
		onChange={handleChange}
	  />
	  <p>Current Tilt: {tilt}°</p>
	</div>
  );
}

export default TiltSlider;