# Air Quality Monitoring and Prediction System

# BEFORE ANYTHING PLEASE KINDLY CHECK OUR DOCUMENTATION : https://drive.google.com/file/d/1NPIaVT1hvtYQqYWvUATc1DTbIZJo1irb/view?usp=drive_link
## Overview

This project is designed to provide a comprehensive **Air Quality Monitoring and Prediction System**. The solution leverages deep learning models and large language models to predict the Air Quality Index (AQI) and identify potential pollution sources. It includes a real-time AQI monitoring system, pollutant-level analysis, and an intelligent chatbot for industry regulation queries and pollution mitigation strategies. The system is built using a robust tech stack, combining React for the frontend, FastAPI for the backend, and Intel-optimized machine learning libraries for enhanced performance.

## Tech Stack and Architecture

- **Frontend**:  
  - React  
  - HTML  
  - CSS  

- **Backend**:  
  - FastAPI  

- **Models**:  
  - Bidirectional Long Short-Term Memory (BiLSTM)  
  - Large Language Model (LLM) - Llama 3.1  

- **Deep Learning Libraries**:  
  - TensorFlow  

- **Intel Optimization Tools**:  
  - `modin` - High-performance alternative to pandas  
  - `intel-extension-for-tensorflow`  
  - `intel-extension-for-keras`  
  - `optimum`
  
- **Other Libraries**:  
  - Matplotlib  
  - NumPy  

## Dataset

The project utilizes the **Air Quality Data in India (2015 - 2020)** dataset, which includes hourly and daily air quality data from various stations across multiple cities in India. The following files were used:

- `city_day.csv`: Daily air quality data at the city level.
- `city_hour.csv`: Hourly air quality data at the city level.
- `station_day.csv`: Daily air quality data at the station level.
- `station_hour.csv`: Hourly air quality data at the station level.
- `stations.csv`: Metadata for stations.

For this project, the `city_hour.csv` and `station_day.csv` files were primarily used for data preparation and model training.

## Application Features

The system consists of four main pages with distinct functionalities:

1. **Home Page**:  
   - Provides a slider to toggle between live and dynamic AQI predictions. The AQI value is displayed at the top, and individual molecule values are shown inside dynamic bubbles.

2. **Cloud Page**:  
   - Predicts AQI values for a selected station. If values exceed moderate levels, it lists the industries that might be responsible and suggests ways to reduce pollution based on molecule analysis using an LLM which was qlora finetuned.

3. **Graph Page**:  
   - Allows visualization of AQI trends over a selected date range using bar graphs. This page helps track the city's air quality performance over time.

4. **Chatbot Page**:  
   - A chatbot interface where users can inquire about pollution laws, industry regulations, and steps to lower AQI based on the industry act provided by the Indian government.

## Model Training and Evaluation

After preparing the dataset, various machine learning models were developed and evaluated to predict AQI values:

- **Initial Model**:  
  - A basic Artificial Neural Network (ANN) was built, resulting in a Mean Absolute Error (MAE) of 42%.

- **Second Attempt**:  
  - A Convolutional Neural Network (CNN) was implemented, achieving an improved MAE of 37%.

- **Final Model**:  
  - A Bidirectional LSTM (BiLSTM) network with 4 layers, Batch Normalization, and Dropout layers was constructed. This configuration successfully captured long-term dependencies and resulted in a remarkable MAE of 7.0%.

The models were optimized using Intel's machine learning extensions (`intel-extension-for-tensorflow` and `modin`), which significantly improved training speed and overall efficiency.

## Installation and Setup

### Prerequisites

- **Node.js and npm**: Required for frontend development.
- **Python 3.8+**: Required for backend development and model training.
- **Intel-optimized libraries**: Recommended for enhanced performance.

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/air-quality-monitoring.git
cd air-quality-monitoring

```

# Air Quality Monitoring Application

## Installation and Setup

### Step 2: Install Backend Dependencies

```bash
pip install -r requirements.txt
```

``` bash
uvicorn main.py:app --reload

```
### then 

```bash
cd my-app

npm start

```
