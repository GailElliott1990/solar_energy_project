import React, { useState, useEffect, useCallback } from 'react';
import SolarDataGraph from './SolarDataGraph';
import SolarDataTable from './SolarDataTable';
import MultiplierSlider from './MultiplierSlider';
import TiltSlider from './TiltSlider';
import AzimuthSlider from './AzimuthSlider';

import './App.css';

function App() {
  const [forecastData, setForecastData] = useState([]);
  const [errorMessage, setErrorMessage] = useState('');
  const [lastUpdateTime, setLastUpdateTime] = useState('');
  const [showTable, setShowTable] = useState(true);

  const [multiplier, setMultiplier] = useState(1);
  const [tilt, setTilt] = useState(30);
  const [azimuth, setAzimuth] = useState(180);

  // Replace this with your actual aws apprunner
  const baseURL = 'https://aq8fwnu9jp.eu-west-1.awsapprunner.com';
  
  // Fetch data from the NREL PVWatts API via your deployed backend
  const fetchPVWattsData = useCallback(() => {
    const apiUrl = `${baseURL}/api/pvwatts?tilt=${tilt}&azimuth=${azimuth}`;

    fetch(apiUrl)
      .then((response) => {
        if (!response.ok) {
          return response.json().then((err) => {
            throw new Error(err.error || 'Server Error');
          });
        }
        return response.json();
      })
      .then((data) => {
        if (!data.outputs || !data.outputs.ac_monthly) {
          throw new Error('Invalid data format received from server.');
        }

        const { ac_monthly, poa_monthly, solrad_monthly } = data.outputs;
        const transformedData = ac_monthly.map((acVal, index) => {
          const dateStr = `2024-${(index + 1).toString().padStart(2, '0')}-01T00:00:00Z`;
          return {
            period_end: dateStr,
            ac_value: acVal * multiplier,
            poa_value: poa_monthly[index] * multiplier,
            solrad_value: solrad_monthly[index] * multiplier,
          };
        });

        setForecastData(transformedData);
        setErrorMessage('');

        if (transformedData.length > 0) {
          setLastUpdateTime(new Date().toISOString());
        }
      })
      .catch((error) => {
        console.error('Error fetching data:', error);
        setErrorMessage(error.message || 'Failed to fetch data from the server.');
        setForecastData([]);
      });
  }, [multiplier, tilt, azimuth, baseURL]);

  useEffect(() => {
    fetchPVWattsData();
  }, [fetchPVWattsData]);

  const toggleTable = () => {
    setShowTable((prevShowTable) => !prevShowTable);
  };

  const resetValues = () => {
    setMultiplier(1);
    setTilt(30);
    setAzimuth(180);
  };

  return (
    <div className="App">
      <h1>Solar Energy Data</h1>
      {errorMessage && <p className="error-message">{errorMessage}</p>}
      {lastUpdateTime && (
        <p className="last-update">Last data update: {new Date(lastUpdateTime).toLocaleString()}</p>
      )}

      <div className="sliders-row">
        <div className="slider">
          <MultiplierSlider multiplier={multiplier} onMultiplierChange={setMultiplier} />
        </div>
        <div className="slider">
          <TiltSlider tilt={tilt} onTiltChange={setTilt} />
        </div>
        <div className="slider">
          <AzimuthSlider azimuth={azimuth} onAzimuthChange={setAzimuth} />
        </div>
      </div>

      <div className="button-container">
        <button className="toggle-button" onClick={toggleTable}>
          {showTable ? 'Hide Table' : 'Show Table'}
        </button>
        <button className="reset-button" onClick={resetValues}>
          Reset to Defaults
        </button>
      </div>

      <div className="chart-container">
        <SolarDataGraph data={forecastData} tilt={tilt} azimuth={azimuth} />
      </div>

      <div className="table-container">
        {showTable && <SolarDataTable data={forecastData} />}
      </div>
    </div>
  );
}

export default App;