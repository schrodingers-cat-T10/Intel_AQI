export const fetchAQIData = async (city) => {
    try {
      const response = await fetch('http://localhost:8000/predict/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ city }),
      });
  
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching AQI data:', error);
      return null;
    }
  };
  