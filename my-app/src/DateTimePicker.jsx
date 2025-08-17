import React, { useState, useEffect } from 'react';
import './DateTimePicker.css';

const DateTimePicker = ({ value, onChange }) => {
  const [year, setYear] = useState(value.getFullYear());
  const [month, setMonth] = useState(value.getMonth() + 1);
  const [day, setDay] = useState(value.getDate());
  const [hour, setHour] = useState(value.getHours());
  const [minute, setMinute] = useState(value.getMinutes());


  useEffect(() => {
    const selectedDate = new Date(year, month - 1, day, hour, minute);
    onChange(selectedDate);
  }, [year, month, day, hour, minute]); 

  const increment = (value, setter, max) => setter(value < max ? value + 1 : 1);
  const decrement = (value, setter, min, max) => setter(value > min ? value - 1 : max);

  const incrementYear = () => setYear((prevYear) => prevYear + 1);
  const decrementYear = () => setYear((prevYear) => (prevYear > 1930 ? prevYear - 1 : 1930));

  const incrementMonth = () => setMonth((prevMonth) => (prevMonth < 12 ? prevMonth + 1 : 1));
  const decrementMonth = () => setMonth((prevMonth) => (prevMonth > 1 ? prevMonth - 1 : 12));

  const incrementDay = () => setDay((prevDay) => (prevDay < 31 ? prevDay + 1 : 1));
  const decrementDay = () => setDay((prevDay) => (prevDay > 1 ? prevDay - 1 : 31));

  const incrementHour = () => setHour((prevHour) => (prevHour < 23 ? prevHour + 1 : 0));
  const decrementHour = () => setHour((prevHour) => (prevHour > 0 ? prevHour - 1 : 23));

  const incrementMinute = () => setMinute((prevMinute) => (prevMinute < 59 ? prevMinute + 1 : 0));
  const decrementMinute = () => setMinute((prevMinute) => (prevMinute > 0 ? prevMinute - 1 : 7));

  return (
    <div className="picker-container">
      <div className="picker">
        <div className="picker-column">
          <div className="picker-label">Year</div>
          <button className="picker-arrow" onClick={incrementYear}>&#9650;</button>
          <div className="picker-item">{year}</div>
          <button className="picker-arrow" onClick={decrementYear}>&#9660;</button>
        </div>
        <div className="picker-column">
          <div className="picker-label">Month</div>
          <button className="picker-arrow" onClick={incrementMonth}>&#9650;</button>
          <div className="picker-item">{month}</div>
          <button className="picker-arrow" onClick={decrementMonth}>&#9660;</button>
        </div>
        <div className="picker-column">
          <div className="picker-label">Day</div>
          <button className="picker-arrow" onClick={incrementDay}>&#9650;</button>
          <div className="picker-item">{day}</div>
          <button className="picker-arrow" onClick={decrementDay}>&#9660;</button>
        </div>
        <div className="picker-column">
          <div className="picker-label">Hour</div>
          <button className="picker-arrow" onClick={incrementHour}>&#9650;</button>
          <div className="picker-item">{hour}</div>
          <button className="picker-arrow" onClick={decrementHour}>&#9660;</button>
        </div>
        <div className="picker-column">
          <div className="picker-label">Minute</div>
          <button className="picker-arrow" onClick={incrementMinute}>&#9650;</button>
          <div className="picker-item">{minute.toString().padStart(2, '0')}</div>
          <button className="picker-arrow" onClick={decrementMinute}>&#9660;</button>
        </div>
      </div>
    </div>
  );
};

export default DateTimePicker;
