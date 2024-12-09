import React from 'react';

function MultiplierSlider({ multiplier, onMultiplierChange }) {
  const handleChange = (event) => {
	const newMultiplier = Number(event.target.value);
	onMultiplierChange(newMultiplier);
  };

  return (
	<div>
	  <h2>Set Multiplier</h2>
	  <input
		type="range"
		min="1"
		max="10"
		step="0.1"
		value={multiplier}
		onChange={handleChange}
	  />
	  <p>Current Multiplier: {multiplier}</p>
	</div>
  );
}

export default MultiplierSlider;