import React, { useState, useEffect } from 'react';
import './pageone.css';
import lowAqiImage from './cloudyy.jpg'; // Ensure the correct image path

const PageOne = () => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [inputValue, setInputValue] = useState(''); // For the input in box1
  const [aqi, setAqi] = useState(null); // Store the AQI value
  const [molecules, setMolecules] = useState([]); // Store the gas molecule predictions
  const [industries, setIndustries] = useState([]); // Store the industry predictions
  const [chatbotResponse, setChatbotResponse] = useState(''); // Store the chatbot response

  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer); // Clean up on unmount
  }, []);

  // Handle form submission for AQI prediction
  const handleAqiSubmit = async (e) => {
    e.preventDefault();

    if (!inputValue.trim()) {
      alert("Please enter a city name");
      return;
    }

    // Extracting date and time values
    const year = currentTime.getFullYear();
    const month = currentTime.getMonth() + 1; // Months are 0-indexed
    const day = currentTime.getDate();
    const hour = currentTime.getHours();
    const dayOfWeek = currentTime.getDay(); // Sunday is 0
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6 ? 1 : 0; // 1 for weekend, 0 otherwise

    try {
      // Make a POST request to the backend
      const response = await fetch('http://localhost:8000/predict-new', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          station_name: inputValue, // Send the user's input as the station name
          year,
          month,
          day,
          hour,
          dayOfWeek,
          isWeekend,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch AQI prediction');
      }

      const result = await response.json();

      // Update the AQI value and molecules
      setAqi(result.aqi);
      setMolecules(result.molecules);

      // Capture industries list if available
      if (result.top_industries) {
        setIndustries(result.top_industries);
      }

      // Update the chatbot response based on the AQI
      if (result.aqi < 80) {
        setChatbotResponse(
          `The predicted AQI is ${result.aqi}. Here are the top contributing industries: 
          ${result.top_industries.join(', ')}.`
        );
      } else {
        setChatbotResponse(
          `The predicted AQI is ${result.aqi}. Everything is good!`
        );
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to fetch prediction. Please try again.');
    }
  };

  return (
    <div className="page-layout">
      {/* Column 1 */}
      <div className="column">
        {/* Box 1 - Input and DateTime */}
        <div className="box box1">
          <form onSubmit={handleAqiSubmit}>
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Enter city..."
            />
            <button type="submit">Submit</button> {/* Submit button to trigger prediction */}
          </form>
          <p>Current Time: {currentTime.toLocaleString()}</p>
        </div>

        {/* Box 2 - AQI Label and 12 Bubbles */}
        <div className="box box2">
          <p className="aqi-label">AQI: {aqi !== null ? aqi : 'N/A'}</p> {/* Show AQI */}
          <div className="bubbles-container">
            {Array.from({ length: 12 }).map((_, index) => (
              <div key={index} className="bubble">
                {molecules[index] !== undefined ? molecules[index] : index + 1} {/* Fill bubbles with molecule values */}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Column 2 */}
      <div className="column">
        {/* Box 3 - Chatbot Area */}
        <div className="box box3">
          {/* Display image when AQI is less than 100 or no city is entered */}
          {(!inputValue || (aqi === null && aqi < 100)) ? (
            <img src={lowAqiImage} alt="Low AQI Indicator" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          ) : (
            <p>{chatbotResponse || "Enter a city and submit to see predictions here."}</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default PageOne;
