import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './pagetwo.css'; // Updated CSS file

function PageTwo() {
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [selectedCity, setSelectedCity] = useState('');
  const [data, setData] = useState([]); // State to hold graph data

  const cities = [
    "Ahmedabad", "Aizawl", "Amaravati", "Amritsar", "Bengaluru", "Bhopal", "Brajrajnagar",
    "Chandigarh", "Chennai", "Coimbatore", "Delhi", "Ernakulam", "Gurugram", "Guwahati",
    "Hyderabad", "Jaipur", "Jorapokhar", "Kochi", "Kolkata", "Lucknow", "Mumbai", "Patna",
    "Shillong", "Talcher", "Thiruvananthapuram", "Visakhapatnam"
  ]; // Replace with actual city names

  const handleSubmit = async (event) => {
    event.preventDefault();

    // Parse fromDate and toDate
    const fromDateObj = new Date(fromDate);
    const toDateObj = new Date(toDate);

    // Validate that the from date is earlier than the to date
    if (fromDateObj > toDateObj) {
      alert("From date must be earlier than To date.");
      return;
    }

    // Prepare data for the request
    const requestData = {
      city: selectedCity,
      fromDate: fromDate, // Send the full date string
      toDate: toDate      // Send the full date string
    };

    console.log(requestData);

    // Send the request to the backend for AQI prediction
    const response = await fetch('http://localhost:8000/predict-date-range', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestData)
    });

    const result = await response.json();
    if (response.ok) {
      // Assuming the backend returns an array of predictions
      const fetchedData = result.predictions.map(prediction => ({
        name: prediction.datetime, // Assuming the backend sends this
        value: prediction.aqi       // Assuming the backend sends this
      }));
      setData(fetchedData); // Update the state with the fetched data
    } else {
      console.error("Failed to fetch prediction:", result);
    }
  };

  return (
    <div className="page-two-container">
      {/* Submit Button and Form Positioned at the Top */}
      <div className="top-controls">
        <form onSubmit={handleSubmit} className="form-controls">
          <label>
            From:
            <input
              type="date"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              required
            />
          </label>
          <label>
            To:
            <input
              type="date"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              required
            />
          </label>
          <label>
            City:
            <select
              value={selectedCity}
              onChange={(e) => setSelectedCity(e.target.value)}
              required
            >
              <option value="">Select a city</option>
              {cities.map((city) => (
                <option key={city} value={city}>
                  {city}
                </option>
              ))}
            </select>
          </label>
          <button type="submit" className="submit">Submit</button>
        </form>
      </div>

      {/* Bar Graph Section */}
      <ResponsiveContainer width="100%" height={400} className="bar-chart">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f5f5f5" />
          <XAxis dataKey="name" stroke="#333" />
          <YAxis stroke="#333" />
          <Tooltip />
          <Legend />
          <Bar dataKey="value" fill="#00C49F" barSize={50} radius={[10, 10, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default PageTwo;
