import React, { useState } from 'react';
import './DateTimePicker.css';

const DateTimePicker = () => {
  const currentYear = new Date().getFullYear();
  const [year, setYear] = useState(currentYear);
  const [month, setMonth] = useState(1);
  const [day, setDay] = useState(1);
  const [hour, setHour] = useState(0); // Changed to 0-based for 24-hour format
  const [minute, setMinute] = useState(0); // Changed to 0-based for 60-minute format
  const [yesNo, setYesNo] = useState('Yes');

  const increment = (value, setter, max) => setter(value < max ? value + 1 : 1);
  const decrement = (value, setter, min, max) => setter(value > min ? value - 1 : max);
  
  const incrementYear = () => setYear(year + 1);
  const decrementYear = () => setYear(year > 1930 ? year - 1 : 1930);
  const toggleYesNo = () => setYesNo(yesNo === 'Yes' ? 'No' : 'Yes');

  return (
    <div className="picker-container">
      <div className="picker">
        {/* Year Picker */}
        <div className="picker-column">
          <div className="picker-label">Year</div>
          <button className="picker-arrow" onClick={incrementYear}>&#9650;</button>
          <div className="picker-item">{year}</div>
          <button className="picker-arrow" onClick={decrementYear}>&#9660;</button>
        </div>

        {/* Month Picker */}
        <div className="picker-column">
          <div className="picker-label">Month</div>
          <button className="picker-arrow" onClick={() => increment(month, setMonth, 12)}>&#9650;</button>
          <div className="picker-item">{month}</div>
          <button className="picker-arrow" onClick={() => decrement(month, setMonth, 1, 12)}>&#9660;</button>
        </div>

        {/* Day Picker */}
        <div className="picker-column">
          <div className="picker-label">Day</div>
          <button className="picker-arrow" onClick={() => increment(day, setDay, 31)}>&#9650;</button>
          <div className="picker-item">{day}</div>
          <button className="picker-arrow" onClick={() => decrement(day, setDay, 1, 31)}>&#9660;</button>
        </div>

        {/* Hour Picker (24-hour format) */}
        <div className="picker-column">
          <div className="picker-label">Hour</div>
          <button className="picker-arrow" onClick={() => increment(hour, setHour, 23)}>&#9650;</button>
          <div className="picker-item">{hour}</div>
          <button className="picker-arrow" onClick={() => decrement(hour, setHour, 0, 23)}>&#9660;</button>
        </div>

        {/* Minute Picker (60-minute format) */}
        <div className="picker-column">
          <div className="picker-label">Minute</div>
          <button className="picker-arrow" onClick={() => increment(minute, setMinute, 59)}>&#9650;</button>
          <div className="picker-item">{minute.toString().padStart(2, '0')}</div>
          <button className="picker-arrow" onClick={() => decrement(minute, setMinute, 0, 59)}>&#9660;</button>
        </div>

        {/* Yes/No Picker */}
        <div className="picker-column">
          <div className="picker-label">Yes/No</div>
          <button className="picker-arrow" onClick={toggleYesNo}>&#9650;</button>
          <div className="picker-item">{yesNo}</div>
          <button className="picker-arrow" onClick={toggleYesNo}>&#9660;</button>
        </div>
      </div>
    </div>
  );
};

export default DateTimePicker;
