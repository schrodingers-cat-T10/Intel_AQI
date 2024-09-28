import React, { useState, useEffect } from 'react';
import './Home.css';
import DateTimePicker from './DateTimePicker';
import axios from 'axios';

function Home() {
  const [activeTab, setActiveTab] = useState('live'); // Keep track of the active tab
  const [currentDateTime, setCurrentDateTime] = useState(''); // Live date-time display
  const [selectedCity, setSelectedCity] = useState(''); // For dynamic tab city selection
  const [liveCity, setLiveCity] = useState('Fetching location...'); // For live tab location
  const [aqi, setAqi] = useState(null);
  const [gasMolecules, setGasMolecules] = useState([]);
  const [dynamicDateTime, setDynamicDateTime] = useState(new Date()); // For dynamic tab date-time

  let hourlySubmitInterval;

  // Update date-time display for "live" tab every minute
  const updateDateTime = () => {
    const now = new Date();
    const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    setCurrentDateTime(now.toLocaleString('en-US', options));
  };

  // Handle city selection for dynamic tab
  const handleCityChange = (event) => {
    setSelectedCity(event.target.value);
  };

  // Get user location for "live" tab
  const getUserLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          fetchCityFromCoordinates(latitude, longitude);
        },
        () => {
          setLiveCity('Unable to fetch location');
        }
      );
    } else {
      setLiveCity('Geolocation not supported');
    }
  };

  // Fetch city name based on coordinates (for live tab)
  const fetchCityFromCoordinates = async (latitude, longitude) => {
    try {
      const response = await fetch(`https://api.opencagedata.com/geocode/v1/json?q=${latitude}+${longitude}&key=9b3469920f3942e1b34b59196e4fe94c`);
      const data = await response.json();
      if (data.results && data.results.length > 0) {
        const components = data.results[0].components;
        let location = components.city || components.town || components.village || components.state || components.country;
        setLiveCity("Chennai" || 'Unknown location');
      } else {
        setLiveCity('City not found');
      }
    } catch (error) {
      setLiveCity('Error fetching city');
    }
  };

  // Handle date-time change for dynamic tab
  const handleDateTimeChange = (date) => {
    setDynamicDateTime(date); // Update dynamic date-time picker value
    console.log(date);
  };

  // Switch between live and dynamic tabs
  const handleTabSwitch = (tab) => {
    setActiveTab(tab); // Update active tab
    if (tab === 'dynamic') {
      setSelectedCity(''); // Clear selected city for dynamic tab
      clearInterval(hourlySubmitInterval); // Stop hourly submission when not in live tab
    }
  };

  // Handle form submission for both tabs
  const handleSubmit = async () => {
    // Determine which city and date to use based on the active tab
    const city = activeTab === 'live' ? liveCity : selectedCity;
    const date = activeTab === 'live' ? new Date() : dynamicDateTime; // Use dynamic date-time or live

    // Validation for city and date
    if (!city || city === 'Fetching location...' || city === 'Unable to fetch location' || city === 'City not found') {
      alert('Please select a valid city or wait for the location to be detected!');
      return;
    }

    const year = date.getFullYear();
    const month = date.getMonth() + 1; // `getMonth()` returns 0-11, so add 1 to get 1-12
    const day = date.getDate();
    const hour = date.getHours();
    const dayOfWeek = date.getDay(); // `getDay()` returns 0 (Sunday) to 6 (Saturday)
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6 ? 1 : 0; // `isWeekend` is 1 if it's a weekend, else 0

    const inputData = {
      city: city.trim(),
      year,
      month,
      day,
      hour,
      dayOfWeek,
      isWeekend,
    };

    try {
      const response = await axios.post('http://localhost:8000/predict', inputData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.data && response.data.aqi !== undefined && response.data.molecules) {
        const { aqi, molecules } = response.data;
        setAqi(aqi);
        setGasMolecules(molecules);
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      console.error('Error during prediction:', error);
      alert(`Error getting prediction: ${error.response?.data?.detail || error.message}`);
    }
  };

  // Set up hourly submission when "live" tab is active
  useEffect(() => {
    if (activeTab === 'live') {
      // Delay first submission by 3 seconds, then set up hourly submission
      const timeoutId = setTimeout(() => {
        handleSubmit(); // First submit after 3 seconds
        hourlySubmitInterval = setInterval(handleSubmit, 3600000); // Submit every hour (3600000 ms)
      }, 3000); // 3-second delay before first submission

      return () => {
        clearTimeout(timeoutId); // Clean up timeout on unmount or tab switch
        clearInterval(hourlySubmitInterval); // Clean up interval on unmount or tab switch
      };
    }
  }, [activeTab]); // Run effect when activeTab changes

  // Run every minute to update the date-time display
  useEffect(() => {
    updateDateTime();
    const intervalId = setInterval(updateDateTime, 60000);
    return () => clearInterval(intervalId);
  }, []);

  // Run on mount to fetch user location for live tab
  useEffect(() => {
    getUserLocation();
  }, []);

  return (
    <div className="home-container">
      <div className="navbar">
        <ul className="menu">
          <li onClick={() => handleTabSwitch('live')} className={activeTab === 'live' ? 'active' : ''}>Live</li>
          <li onClick={() => handleTabSwitch('dynamic')} className={activeTab === 'dynamic' ? 'active' : ''}>Dynamic</li>
        </ul>
        <div className={`slider ${activeTab}`}></div>
      </div>

      <div className="content-wrapper">
        <div className="content">
          {activeTab === 'live' && (
            <div className="live-section">
              <div className="current-time">
                <h1>Current Date and Time</h1>
                <p>{currentDateTime}</p>
                <h2>Live Location: {liveCity}</h2>
              </div>
            </div>
          )}

          {activeTab === 'dynamic' && (
            <div className="dynamic-section">
              <div className="dropdown-container">
                <select value={selectedCity} onChange={handleCityChange} className="city-dropdown">
                  <option value="" disabled>Select a City</option>
                  <option value="Ahmedabad">Ahmedabad</option>
                  <option value="Aizawl">Aizawl</option>
                  <option value="Amaravati">Amaravati</option>
                  <option value="Amritsar">Amritsar</option>
                  <option value="Bengaluru">Bengaluru</option>
                  <option value="Bhopal">Bhopal</option>
                  <option value="Brajrajnagar">Brajrajnagar</option>
                  <option value="Chandigarh">Chandigarh</option>
                  <option value="Chennai">Chennai</option>
                  <option value="Coimbatore">Coimbatore</option>
                  <option value="Delhi">Delhi</option>
                  <option value="Ernakulam">Ernakulam</option>
                  <option value="Gurugram">Gurugram</option>
                  <option value="Guwahati">Guwahati</option>
                  <option value="Hyderabad">Hyderabad</option>
                  <option value="Jaipur">Jaipur</option>
                  <option value="Jorapokhar">Jorapokhar</option>
                  <option value="Kochi">Kochi</option>
                  <option value="Kolkata">Kolkata</option>
                  <option value="Lucknow">Lucknow</option>
                  <option value="Mumbai">Mumbai</option>
                  <option value="Patna">Patna</option>
                  <option value="Shillong">Shillong</option>
                  <option value="Talcher">Talcher</option>
                  <option value="Thiruvananthapuram">Thiruvananthapuram</option>
                  <option value="Visakhapatnam">Visakhapatnam</option>
                </select>
              </div>
              <DateTimePicker value={dynamicDateTime} onChange={handleDateTimeChange} />
              <button className='submit' onClick={handleSubmit}>Submit</button>
            </div>
          )}
        </div>

        <div className="right-content">
          <div className="box-right-1">
            <h2>AQI: {aqi !== null ? aqi : 'N/A'}</h2>
          </div>
          <div className="box-right-2">
            <div className="bubbles-container">
              {gasMolecules.length > 0 ? (
                ['PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'NH3', 'CO', 'SO2', 'O3', 'Benzene', 'Toluene', 'Xylene'].map((molecule, index) => (
                  <div key={index} className="bubble">
                    <strong>{molecule}</strong>: {gasMolecules[index] !== undefined ? gasMolecules[index] : 'N/A'}
                  </div>
                ))
              ) : (
                ['PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'NH3', 'CO', 'SO2', 'O3', 'Benzene', 'Toluene', 'Xylene'].map((molecule, index) => (
                  <div key={index} className="bubble">
                    <strong>{molecule}</strong>: N/A
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;
