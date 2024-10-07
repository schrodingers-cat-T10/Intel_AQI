from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from pydantic import BaseModel
import pickle
from datetime import datetime, timedelta
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.llms import Ollama
from langchain_community.vectorstores import FAISS
from langchain_nomic import NomicEmbeddings
from serpapi import GoogleSearch
from langchain.text_splitter import CharacterTextSplitter
import nomic
from langchain_community.document_loaders import PDFPlumberLoader
from PyPDF2 import PdfReader
from sklearnex import patch_sklearn
patch_sklearn()


nomic.cli.login("nk-TbdtpiqAFh3TRTPDLItfr6FLiUpXYb2TwapWvrEhi_g")
# Your city list
cities = [
    "Ahmedabad", "Aizawl", "Amaravati", "Amritsar", "Bengaluru", "Bhopal", "Brajrajnagar",
    "Chandigarh", "Chennai", "Coimbatore", "Delhi", "Ernakulam", "Gurugram", "Guwahati",
    "Hyderabad", "Jaipur", "Jorapokhar", "Kochi", "Kolkata", "Lucknow", "Mumbai", "Patna",
    "Shillong", "Talcher", "Thiruvananthapuram", "Visakhapatnam"
]

# Load models
def load_model(path):
    try:
        with open(path, 'rb') as file:
            return pickle.load(file)
    except Exception as e:
        raise RuntimeError(f"Error loading model: {str(e)}")

model_1 = load_model('model.pkl')
model_2 = load_model('station.pkl')

# One-hot encoding function for cities
def encode_city(city_name):
    encoding = [0] * len(cities)
    if city_name in cities:
        encoding[cities.index(city_name)] = 1
    return encoding

# Helper function to check if the day is a weekend
def is_weekend(date):
    return date.weekday() >= 5

# Data models for AQI prediction and chatbot messages
class InputDataModel1(BaseModel):
    city: str
    year: int
    month: int
    day: int
    hour: int
    dayOfWeek: int
    isWeekend: int

class InputDataModel2(BaseModel):
    station_name: str  
    year: int
    month: int
    day: int
    hour: int
    dayOfWeek: int
    isWeekend: int

class ChatMessage(BaseModel):
    message: str

class DateRangeModel(BaseModel):
    city: str
    fromDate: str  # YYYY-MM-DD format
    toDate: str    # YYYY-MM-DD format

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AQI Prediction Endpoint
@app.post("/predict")
async def predict_model_1(data: InputDataModel1):
    print(data)
    city_encoding = encode_city("Delhi")
    print(city_encoding)
    input_values = city_encoding + [data.year, data.month, data.day, data.hour, data.dayOfWeek, data.isWeekend]
    input_array = np.array(input_values).astype("float32").reshape(1, -1)
    prediction = model_1.predict(input_array)
    print(prediction)
    # Return AQI and molecules as integers
    return {
        "aqi": int(prediction[0][12]), 
        "molecules": [int(value) for value in prediction[0][:12]]  # Convert all molecule values to integers
    }

# AQI Prediction over a date range
@app.post("/predict-date-range")
async def predict_over_date_range(data: DateRangeModel):
    try:
        from_date = datetime.strptime(data.fromDate, "%Y-%m-%d")
        to_date = datetime.strptime(data.toDate, "%Y-%m-%d")
        city_encoding = encode_city(data.city)

        if not city_encoding:
            raise HTTPException(status_code=400, detail="Invalid city")

        predictions = []
        current_date = from_date
        while current_date <= to_date:
            for hour in range(24):
                day_of_week = current_date.weekday()
                weekend = 1 if is_weekend(current_date) else 0

                input_values = city_encoding + [
                    current_date.year,
                    current_date.month,
                    current_date.day,
                    hour,
                    day_of_week,
                    weekend
                ]
                input_array = np.array(input_values).astype("float32").reshape(1, -1)

                prediction = model_1.predict(input_array)
                predictions.append({
                    "datetime": current_date.strftime(f"%Y-%m-%d {hour}:00"),
                    "aqi": int(prediction[0][12]),  # Convert AQI to integer
                    "molecules": [int(value) for value in prediction[0][:12]]  # Convert all molecule values to integers
                })

            current_date += timedelta(days=1)

        return {"city": data.city, "predictions": predictions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Station list and function to get station index
stations = [
    [{'Unnamed: 0': 0, 'StationId': 'AP001', 'StationName': 'Secretariat, Amaravati'}, {'Unnamed: 0': 1, 'StationId': 'AP002', 'StationName': 'Anand Kala Kshetram, Rajamahendravaram'}, {'Unnamed: 0': 2, 'StationId': 'AP003', 'StationName': 'Tirumala, Tirupati'}, {'Unnamed: 0': 3, 'StationId': 'AP004', 'StationName': 'PWD Grounds, Vijayawada'}, {'Unnamed: 0': 4, 'StationId': 'AP005', 'StationName': 'GVM Corporation, Visakhapatnam'}, {'Unnamed: 0': 5, 'StationId': 'AS001', 'StationName': 'Railway Colony, Guwahati'}, {'Unnamed: 0': 6, 'StationId': 'BR001', 'StationName': 'Collectorate, Gaya'}, {'Unnamed: 0': 7, 'StationId': 'BR002', 'StationName': 'SFTI Kusdihra, Gaya'}, {'Unnamed: 0': 8, 'StationId': 'BR003', 'StationName': 'Industrial Area, Hajipur'}, {'Unnamed: 0': 9, 'StationId': 'BR004', 'StationName': 'Muzaffarpur Collectorate, Muzaffarpur'}, {'Unnamed: 0': 10, 'StationId': 'BR005', 'StationName': 'DRM Office Danapur, Patna'}, {'Unnamed: 0': 11, 'StationId': 'BR006', 'StationName': 'Govt. High School Shikarpur, Patna'}, {'Unnamed: 0': 12, 'StationId': 'BR007', 'StationName': 'IGSC Planetarium Complex, Patna'}, {'Unnamed: 0': 13, 'StationId': 'BR008', 'StationName': 'Muradpur, Patna'}, {'Unnamed: 0': 14, 'StationId': 'BR009', 'StationName': 'Rajbansi Nagar, Patna'}, {'Unnamed: 0': 15, 'StationId': 'BR010', 'StationName': 'Samanpura, Patna'}, {'Unnamed: 0': 16, 'StationId': 'CH001', 'StationName': 'Sector-25, Chandigarh'}, {'Unnamed: 0': 17, 'StationId': 'DL001', 'StationName': 'Alipur, Delhi'}, {'Unnamed: 0': 18, 'StationId': 'DL002', 'StationName': 'Anand Vihar, Delhi'}, {'Unnamed: 0': 19, 'StationId': 'DL003', 'StationName': 'Ashok Vihar, Delhi'}, {'Unnamed: 0': 20, 'StationId': 'DL004', 'StationName': 'Aya Nagar, Delhi'}, {'Unnamed: 0': 21, 'StationId': 'DL005', 'StationName': 'Bawana, Delhi'}, {'Unnamed: 0': 22, 'StationId': 'DL006', 'StationName': 'Burari Crossing, Delhi'}, {'Unnamed: 0': 23, 'StationId': 'DL007', 'StationName': 'CRRI Mathura Road, Delhi'}, {'Unnamed: 0': 24, 'StationId': 'DL008', 'StationName': 'DTU, Delhi'}, {'Unnamed: 0': 25, 'StationId': 'DL009', 'StationName': 'Dr. Karni Singh Shooting Range, Delhi'}, {'Unnamed: 0': 26, 'StationId': 'DL010', 'StationName': 'Dwarka-Sector 8, Delhi'}, {'Unnamed: 0': 27, 'StationId': 'DL011', 'StationName': 'East Arjun Nagar, Delhi'}, {'Unnamed: 0': 28, 'StationId': 'DL012', 'StationName': 'IGI Airport (T3), Delhi'}, {'Unnamed: 0': 29, 'StationId': 'DL013', 'StationName': 'IHBAS, Dilshad Garden, Delhi'}, {'Unnamed: 0': 30, 'StationId': 'DL014', 'StationName': 'ITO, Delhi'}, {'Unnamed: 0': 31, 'StationId': 'DL015', 'StationName': 'Jahangirpuri, Delhi'}, {'Unnamed: 0': 32, 'StationId': 'DL016', 'StationName': 'Jawaharlal Nehru Stadium, Delhi'}, {'Unnamed: 0': 33, 'StationId': 'DL017', 'StationName': 'Lodhi Road, Delhi'}, {'Unnamed: 0': 34, 'StationId': 'DL018', 'StationName': 'Major Dhyan Chand National Stadium, Delhi'}, {'Unnamed: 0': 35, 'StationId': 'DL019', 'StationName': 'Mandir Marg, Delhi'}, {'Unnamed: 0': 36, 'StationId': 'DL020', 'StationName': 'Mundka, Delhi'}, {'Unnamed: 0': 37, 'StationId': 'DL021', 'StationName': 'NSIT Dwarka, Delhi'}, {'Unnamed: 0': 38, 'StationId': 'DL022', 'StationName': 'Najafgarh, Delhi'}, {'Unnamed: 0': 39, 'StationId': 'DL023', 'StationName': 'Narela, Delhi'}, {'Unnamed: 0': 40, 'StationId': 'DL024', 'StationName': 'Nehru Nagar, Delhi'}, {'Unnamed: 0': 41, 'StationId': 'DL025', 'StationName': 'North Campus, DU, Delhi'}, {'Unnamed: 0': 42, 'StationId': 'DL026', 'StationName': 'Okhla Phase-2, Delhi'}, {'Unnamed: 0': 43, 'StationId': 'DL027', 'StationName': 'Patparganj, Delhi'}, {'Unnamed: 0': 44, 'StationId': 'DL028', 'StationName': 'Punjabi Bagh, Delhi'}, {'Unnamed: 0': 45, 'StationId': 'DL029', 'StationName': 'Pusa, Delhi'}, {'Unnamed: 0': 46, 'StationId': 'DL030', 'StationName': 'Pusa, Delhi'}, {'Unnamed: 0': 47, 'StationId': 'DL031', 'StationName': 'R K Puram, Delhi'}, {'Unnamed: 0': 48, 'StationId': 'DL032', 'StationName': 'Rohini, Delhi'}, {'Unnamed: 0': 49, 'StationId': 'DL033', 'StationName': 'Shadipur, Delhi'}, {'Unnamed: 0': 50, 'StationId': 'DL034', 'StationName': 'Sirifort, Delhi'}, {'Unnamed: 0': 51, 'StationId': 'DL035', 'StationName': 'Sonia Vihar, Delhi'}, {'Unnamed: 0': 52, 'StationId': 'DL036', 'StationName': 'Sri Aurobindo Marg, Delhi'}, {'Unnamed: 0': 53, 'StationId': 'DL037', 'StationName': 'Vivek Vihar, Delhi'}, {'Unnamed: 0': 54, 'StationId': 'DL038', 'StationName': 'Wazirpur, Delhi'}, {'Unnamed: 0': 55, 'StationId': 'GJ001', 'StationName': 'Maninagar, Ahmedabad'}, {'Unnamed: 0': 56, 'StationId': 'GJ002', 'StationName': 'GIDC, Ankleshwar'}, {'Unnamed: 0': 57, 'StationId': 'GJ003', 'StationName': 'Sector-10, Gandhinagar'}, {'Unnamed: 0': 58, 'StationId': 'GJ004', 'StationName': 'GIDC, Nandesari'}, {'Unnamed: 0': 59, 'StationId': 'GJ005', 'StationName': 'Phase-1 GIDC, Vapi'}, {'Unnamed: 0': 60, 'StationId': 'GJ006', 'StationName': 'Phase-4 GIDC, Vatva'}, {'Unnamed: 0': 61, 'StationId': 'HR001', 'StationName': 'Patti Mehar, Ambala'}, {'Unnamed: 0': 62, 'StationId': 'HR002', 'StationName': 'Arya Nagar, Bahadurgarh'}, {'Unnamed: 0': 63, 'StationId': 'HR003', 'StationName': 'Nathu Colony, Ballabgarh'}, {'Unnamed: 0': 64, 'StationId': 'HR004', 'StationName': 'H.B. Colony, Bhiwani'}, {'Unnamed: 0': 65, 'StationId': 'HR005', 'StationName': 'Municipal Corporation Office, Dharuhera'}, {'Unnamed: 0': 66, 'StationId': 'HR006', 'StationName': 'New Industrial Town, Faridabad'}, {'Unnamed: 0': 67, 'StationId': 'HR007', 'StationName': 'Sector 11, Faridabad'}, {'Unnamed: 0': 68, 'StationId': 'HR008', 'StationName': 'Sector 30, Faridabad'}, {'Unnamed: 0': 69, 'StationId': 'HR009', 'StationName': 'Sector- 16A, Faridabad'}, {'Unnamed: 0': 70, 'StationId': 'HR010', 'StationName': 'Huda Sector, Fatehabad'}, {'Unnamed: 0': 71, 'StationId': 'HR011', 'StationName': 'NISE Gwal Pahari, Gurugram'}, {'Unnamed: 0': 72, 'StationId': 'HR012', 'StationName': 'Sector-51, Gurugram'}, {'Unnamed: 0': 73, 'StationId': 'HR013', 'StationName': 'Teri Gram, Gurugram'}, {'Unnamed: 0': 74, 'StationId': 'HR014', 'StationName': 'Vikas Sadan, Gurugram'}, {'Unnamed: 0': 75, 'StationId': 'HR015', 'StationName': 'Urban Estate-II, Hisar'}, {'Unnamed: 0': 76, 'StationId': 'HR016', 'StationName': 'Police Lines, Jind'}, {'Unnamed: 0': 77, 'StationId': 'HR017', 'StationName': 'Rishi Nagar, Kaithal'}, {'Unnamed: 0': 78, 'StationId': 'HR018', 'StationName': 'Sector-12, Karnal'}, {'Unnamed: 0': 79, 'StationId': 'HR019', 'StationName': 'Sector-7, Kurukshetra'}, {'Unnamed: 0': 80, 'StationId': 'HR020', 'StationName': 'General Hospital, Mandikhera'}, {'Unnamed: 0': 81, 'StationId': 'HR021', 'StationName': 'Sector-2 IMT, Manesar'}, {'Unnamed: 0': 82, 'StationId': 'HR022', 'StationName': 'Shastri Nagar, Narnaul'}, {'Unnamed: 0': 83, 'StationId': 'HR023', 'StationName': 'Shyam Nagar, Palwal'}, {'Unnamed: 0': 84, 'StationId': 'HR024', 'StationName': 'Sector-6, Panchkula'}, {'Unnamed: 0': 85, 'StationId': 'HR025', 'StationName': 'Sector-18, Panipat'}, {'Unnamed: 0': 86, 'StationId': 'HR026', 'StationName': 'MD University, Rohtak'}, {'Unnamed: 0': 87, 'StationId': 'HR027', 'StationName': 'F-Block, Sirsa'}, {'Unnamed: 0': 88, 'StationId': 'HR028', 'StationName': 'Murthal, Sonipat'}, {'Unnamed: 0': 89, 'StationId': 'HR029', 'StationName': 'Gobind Pura, Yamuna Nagar'}, {'Unnamed: 0': 90, 'StationId': 'JH001', 'StationName': 'Tata Stadium, Jorapokhar'}, {'Unnamed: 0': 91, 'StationId': 'KA001', 'StationName': 'Vidayagiri, Bagalkot'}, {'Unnamed: 0': 92, 'StationId': 'KA002', 'StationName': 'BTM Layout, Bengaluru'}, {'Unnamed: 0': 93, 'StationId': 'KA003', 'StationName': 'BWSSB Kadabesanahalli, Bengaluru'}, {'Unnamed: 0': 94, 'StationId': 'KA004', 'StationName': 'Bapuji Nagar, Bengaluru'}, {'Unnamed: 0': 95, 'StationId': 'KA005', 'StationName': 'City Railway Station, Bengaluru'}, {'Unnamed: 0': 96, 'StationId': 'KA006', 'StationName': 'Hebbal, Bengaluru'}, {'Unnamed: 0': 97, 'StationId': 'KA007', 'StationName': 'Hombegowda Nagar, Bengaluru'}, {'Unnamed: 0': 98, 'StationId': 'KA008', 'StationName': 'Jayanagar 5th Block, Bengaluru'}, {'Unnamed: 0': 99, 'StationId': 'KA009', 'StationName': 'Peenya, Bengaluru'}, {'Unnamed: 0': 100, 'StationId': 'KA010', 'StationName': 'Sanegurava Halli, Bengaluru'}, {'Unnamed: 0': 101, 'StationId': 'KA011', 'StationName': 'Silk Board, Bengaluru'}, {'Unnamed: 0': 102, 'StationId': 'KA012', 'StationName': 'Urban, Chamarajanagar'}, {'Unnamed: 0': 103, 'StationId': 'KA013', 'StationName': 'Chikkaballapur Rural, Chikkaballapur'}, {'Unnamed: 0': 104, 'StationId': 'KA014', 'StationName': 'Kalyana Nagara, Chikkamagaluru'}, {'Unnamed: 0': 105, 'StationId': 'KA015', 'StationName': 'Deshpande Nagar, Hubballi'}, {'Unnamed: 0': 106, 'StationId': 'KA016', 'StationName': 'Lal Bahadur Shastri Nagar, Kalaburagi'}, {'Unnamed: 0': 107, 'StationId': 'KA017', 'StationName': 'Hebbal 1st Stage, Mysuru'}, {'Unnamed: 0': 108, 'StationId': 'KA018', 'StationName': 'Vijay Nagar, Ramanagara'}, {'Unnamed: 0': 109, 'StationId': 'KA019', 'StationName': 'Ibrahimpur, Vijayapura'}, {'Unnamed: 0': 110, 'StationId': 'KA020', 'StationName': 'Collector Office, Yadgir'}, {'Unnamed: 0': 111, 'StationId': 'KL001', 'StationName': 'Udyogamandal, Eloor'}, {'Unnamed: 0': 112, 'StationId': 'KL002', 'StationName': 'Kacheripady, Ernakulam'}, {'Unnamed: 0': 113, 'StationId': 'KL003', 'StationName': 'Thavakkara, Kannur'}, {'Unnamed: 0': 114, 'StationId': 'KL004', 'StationName': 'Vyttila, Kochi'}, {'Unnamed: 0': 115, 'StationId': 'KL005', 'StationName': 'Polayathode, Kollam'}, {'Unnamed: 0': 116, 'StationId': 'KL006', 'StationName': 'Palayam, Kozhikode'}, {'Unnamed: 0': 117, 'StationId': 'KL007', 'StationName': 'Kariavattom, Thiruvananthapuram'}, {'Unnamed: 0': 118, 'StationId': 'KL008', 'StationName': 'Plammoodu, Thiruvananthapuram'}, {'Unnamed: 0': 119, 'StationId': 'MP001', 'StationName': 'T T Nagar, Bhopal'}, {'Unnamed: 0': 120, 'StationId': 'MP002', 'StationName': 'Shrivastav Colony, Damoh'}, {'Unnamed: 0': 121, 'StationId': 'MP003', 'StationName': 'Bhopal Chauraha, Dewas'}, {'Unnamed: 0': 122, 'StationId': 'MP004', 'StationName': 'City Center, Gwalior'}, {'Unnamed: 0': 123, 'StationId': 'MP005', 'StationName': 'Phool Bagh, Gwalior'}, {'Unnamed: 0': 124, 'StationId': 'MP006', 'StationName': 'Chhoti Gwaltoli, Indore'}, {'Unnamed: 0': 125, 'StationId': 'MP007', 'StationName': 'Marhatal, Jabalpur'}, {'Unnamed: 0': 126, 'StationId': 'MP008', 'StationName': 'Gole Bazar, Katni'}, {'Unnamed: 0': 127, 'StationId': 'MP009', 'StationName': 'Sahilara, Maihar'}, {'Unnamed: 0': 128, 'StationId': 'MP010', 'StationName': 'Sector-D Industrial Area, Mandideep'}, {'Unnamed: 0': 129, 'StationId': 'MP011', 'StationName': 'Sector-2 Industrial Area, Pithampur'}, {'Unnamed: 0': 130, 'StationId': 'MP012', 'StationName': 'Shasthri Nagar, Ratlam'}, {'Unnamed: 0': 131, 'StationId': 'MP013', 'StationName': 'Deen Dayal Nagar, Sagar'}, {'Unnamed: 0': 132, 'StationId': 'MP014', 'StationName': 'Bandhavgar Colony, Satna'}, {'Unnamed: 0': 133, 'StationId': 'MP015', 'StationName': 'Vindhyachal STPS, Singrauli'}, {'Unnamed: 0': 134, 'StationId': 'MP016', 'StationName': 'Mahakaleshwar Temple, Ujjain'}, {'Unnamed: 0': 135, 'StationId': 'MH001', 'StationName': 'More Chowk Waluj, Aurangabad'}, {'Unnamed: 0': 136, 'StationId': 'MH002', 'StationName': 'Chandrapur, Chandrapur'}, {'Unnamed: 0': 137, 'StationId': 'MH003', 'StationName': 'MIDC Khutala, Chandrapur'}, {'Unnamed: 0': 138, 'StationId': 'MH004', 'StationName': 'Khadakpada, Kalyan'}, {'Unnamed: 0': 139, 'StationId': 'MH005', 'StationName': 'Bandra, Mumbai'}, {'Unnamed: 0': 140, 'StationId': 'MH006', 'StationName': 'Borivali East, Mumbai'}, {'Unnamed: 0': 141, 'StationId': 'MH007', 'StationName': 'Chhatrapati Shivaji Intl. Airport (T2), Mumbai'}, {'Unnamed: 0': 142, 'StationId': 'MH008', 'StationName': 'Colaba, Mumbai'}, {'Unnamed: 0': 143, 'StationId': 'MH009', 'StationName': 'Kurla, Mumbai'}, {'Unnamed: 0': 144, 'StationId': 'MH010', 'StationName': 'Powai, Mumbai'}, {'Unnamed: 0': 145, 'StationId': 'MH011', 'StationName': 'Sion, Mumbai'}, {'Unnamed: 0': 146, 'StationId': 'MH012', 'StationName': 'Vasai West, Mumbai'}, {'Unnamed: 0': 147, 'StationId': 'MH013', 'StationName': 'Vile Parle West, Mumbai'}, {'Unnamed: 0': 148, 'StationId': 'MH014', 'StationName': 'Worli, Mumbai'}, {'Unnamed: 0': 149, 'StationId': 'MH015', 'StationName': 'Opp GPO Civil Lines, Nagpur'}, {'Unnamed: 0': 150, 'StationId': 'MH016', 'StationName': 'Gangapur Road, Nashik'}, {'Unnamed: 0': 151, 'StationId': 'MH017', 'StationName': 'Airoli, Navi Mumbai'}, {'Unnamed: 0': 152, 'StationId': 'MH018', 'StationName': 'Mahape, Navi Mumbai'}, {'Unnamed: 0': 153, 'StationId': 'MH019', 'StationName': 'Nerul, Navi Mumbai'}, {'Unnamed: 0': 154, 'StationId': 'MH020', 'StationName': 'Karve Road, Pune'}, {'Unnamed: 0': 155, 'StationId': 'MH021', 'StationName': 'Solapur, Solapur'}, {'Unnamed: 0': 156, 'StationId': 'MH022', 'StationName': 'Pimpleshwar Mandir, Thane'}, {'Unnamed: 0': 157, 'StationId': 'ML001', 'StationName': 'Lumpyngngad, Shillong'}, {'Unnamed: 0': 158, 'StationId': 'MZ001', 'StationName': 'Sikulpuikawn, Aizawl'}, {'Unnamed: 0': 159, 'StationId': 'OD001', 'StationName': 'GM Office, Brajrajnagar'}, {'Unnamed: 0': 160, 'StationId': 'OD002', 'StationName': 'Talcher Coalfields,Talcher'}, {'Unnamed: 0': 161, 'StationId': 'PB001', 'StationName': 'Golden Temple, Amritsar'}, {'Unnamed: 0': 162, 'StationId': 'PB002', 'StationName': 'Hardev Nagar, Bathinda'}, {'Unnamed: 0': 163, 'StationId': 'PB003', 'StationName': 'Civil Line, Jalandhar'}, {'Unnamed: 0': 164, 'StationId': 'PB004', 'StationName': 'Kalal Majra, Khanna'}, {'Unnamed: 0': 165, 'StationId': 'PB005', 'StationName': 'Punjab Agricultural University, Ludhiana'}, {'Unnamed: 0': 166, 'StationId': 'PB006', 'StationName': 'RIMT University, Mandi Gobindgarh'}, {'Unnamed: 0': 167, 'StationId': 'PB007', 'StationName': 'Model Town, Patiala'}, {'Unnamed: 0': 168, 'StationId': 'PB008', 'StationName': 'Ratanpura, Rupnagar'}, {'Unnamed: 0': 169, 'StationId': 'RJ001', 'StationName': 'Moti Doongri, Alwar'}, {'Unnamed: 0': 170, 'StationId': 'RJ002', 'StationName': 'Civil Lines, Ajmer'}, {'Unnamed: 0': 171, 'StationId': 'RJ003', 'StationName': 'RIICO Ind. Area III, Bhiwadi'}, {'Unnamed: 0': 172, 'StationId': 'RJ004', 'StationName': 'Adarsh Nagar, Jaipur'}, {'Unnamed: 0': 173, 'StationId': 'RJ005', 'StationName': 'Police Commissionerate, Jaipur'}, {'Unnamed: 0': 174, 'StationId': 'RJ006', 'StationName': 'Shastri Nagar, Jaipur'}, {'Unnamed: 0': 175, 'StationId': 'RJ007', 'StationName': 'Collectorate, Jodhpur'}, {'Unnamed: 0': 176, 'StationId': 'RJ008', 'StationName': 'Shrinath Puram, Kota'}, {'Unnamed: 0': 177, 'StationId': 'RJ009', 'StationName': 'Indira Colony Vistar, Pali'}, {'Unnamed: 0': 178, 'StationId': 'RJ010', 'StationName': 'Ashok Nagar, Udaipur'}, {'Unnamed: 0': 179, 'StationId': 'TN001', 'StationName': 'Alandur Bus Depot, Chennai'}, {'Unnamed: 0': 180, 'StationId': 'TN002', 'StationName': 'Manali Village, Chennai'}, {'Unnamed: 0': 181, 'StationId': 'TN003', 'StationName': 'Manali, Chennai'}, {'Unnamed: 0': 182, 'StationId': 'TN004', 'StationName': 'Velachery Res. Area, Chennai'}, {'Unnamed: 0': 183, 'StationId': 'TN005', 'StationName': 'SIDCO Kurichi, Coimbatore'}, {'Unnamed: 0': 184, 'StationId': 'TG001', 'StationName': 'Bollaram Industrial Area, Hyderabad'}, {'Unnamed: 0': 185, 'StationId': 'TG002', 'StationName': 'Central University, Hyderabad'}, {'Unnamed: 0': 186, 'StationId': 'TG003', 'StationName': 'ICRISAT Patancheru, Hyderabad'}, {'Unnamed: 0': 187, 'StationId': 'TG004', 'StationName': 'IDA Pashamylaram, Hyderabad'}, {'Unnamed: 0': 188, 'StationId': 'TG005', 'StationName': 'Sanathnagar, Hyderabad'}, {'Unnamed: 0': 189, 'StationId': 'TG006', 'StationName': 'Zoo Park, Hyderabad'}, {'Unnamed: 0': 190, 'StationId': 'UP001', 'StationName': 'Sanjay Palace, Agra'}, {'Unnamed: 0': 191, 'StationId': 'UP002', 'StationName': 'New Collectorate, Baghpat'}, {'Unnamed: 0': 192, 'StationId': 'UP003', 'StationName': 'Yamunapuram, Bulandshahr'}, {'Unnamed: 0': 193, 'StationId': 'UP004', 'StationName': 'Indirapuram, Ghaziabad'}, {'Unnamed: 0': 194, 'StationId': 'UP005', 'StationName': 'Loni, Ghaziabad'}, {'Unnamed: 0': 195, 'StationId': 'UP006', 'StationName': 'Sanjay Nagar, Ghaziabad'}, {'Unnamed: 0': 196, 'StationId': 'UP007', 'StationName': 'Vasundhara, Ghaziabad'}, {'Unnamed: 0': 197, 'StationId': 'UP008', 'StationName': 'Knowledge Park'}, {'Unnamed: 0': 198, 'StationId': 'UP009', 'StationName': 'Knowledge Park'}, {'Unnamed: 0': 199, 'StationId': 'UP010', 'StationName': 'Anand Vihar, Hapur'}, {'Unnamed: 0': 200, 'StationId': 'UP011', 'StationName': 'Nehru Nagar, Kanpur'}, {'Unnamed: 0': 201, 'StationId': 'UP012', 'StationName': 'Central School, Lucknow'}, {'Unnamed: 0': 202, 'StationId': 'UP013', 'StationName': 'Gomti Nagar, Lucknow'}, {'Unnamed: 0': 203, 'StationId': 'UP014', 'StationName': 'Lalbagh, Lucknow'}, {'Unnamed: 0': 204, 'StationId': 'UP015', 'StationName': 'Nishant Ganj, Lucknow'}, {'Unnamed: 0': 205, 'StationId': 'UP016', 'StationName': 'Talkatora District Industries Center, Lucknow'}, {'Unnamed: 0': 206, 'StationId': 'UP017', 'StationName': 'Ganga Nagar, Meerut'}, {'Unnamed: 0': 207, 'StationId': 'UP018', 'StationName': 'Jai Bhim Nagar, Meerut'}, {'Unnamed: 0': 208, 'StationId': 'UP019', 'StationName': 'Pallavpuram Phase 2, Meerut'}, {'Unnamed: 0': 209, 'StationId': 'UP020', 'StationName': 'Lajpat Nagar, Moradabad'}, {'Unnamed: 0': 210, 'StationId': 'UP021', 'StationName': 'New Mandi, Muzaffarnagar'}, {'Unnamed: 0': 211, 'StationId': 'UP022', 'StationName': 'Sector'}, {'Unnamed: 0': 212, 'StationId': 'UP023', 'StationName': 'Sector'}, {'Unnamed: 0': 213, 'StationId': 'UP024', 'StationName': 'Sector-1, Noida'}, {'Unnamed: 0': 214, 'StationId': 'UP025', 'StationName': 'Sector-116, Noida'}, {'Unnamed: 0': 215, 'StationId': 'UP026', 'StationName': 'Ardhali Bazar, Varanasi'}, {'Unnamed: 0': 216, 'StationId': 'WB001', 'StationName': 'Asansol Court Area, Asansol'}, {'Unnamed: 0': 217, 'StationId': 'WB002', 'StationName': 'Sidhu Kanhu Indoor Stadium, Durgapur'}, {'Unnamed: 0': 218, 'StationId': 'WB003', 'StationName': 'Haldia, Haldia'}, {'Unnamed: 0': 219, 'StationId': 'WB004', 'StationName': 'Belur Math, Howrah'}, {'Unnamed: 0': 220, 'StationId': 'WB005', 'StationName': 'Ghusuri, Howrah'}, {'Unnamed: 0': 221, 'StationId': 'WB006', 'StationName': 'Padmapukur, Howrah'}, {'Unnamed: 0': 222, 'StationId': 'WB007', 'StationName': 'Ballygunge, Kolkata'}, {'Unnamed: 0': 223, 'StationId': 'WB008', 'StationName': 'Bidhannagar, Kolkata'}, {'Unnamed: 0': 224, 'StationId': 'WB009', 'StationName': 'Fort William, Kolkata'}, {'Unnamed: 0': 225, 'StationId': 'WB010', 'StationName': 'Jadavpur, Kolkata'}, {'Unnamed: 0': 226, 'StationId': 'WB011', 'StationName': 'Rabindra Bharati University, Kolkata'}, {'Unnamed: 0': 227, 'StationId': 'WB012', 'StationName': 'Rabindra Sarobar, Kolkata'}, {'Unnamed: 0': 228, 'StationId': 'WB013', 'StationName': 'Victoria, Kolkata'}, {'Unnamed: 0': 229, 'StationId': 'WB014', 'StationName': 'Ward-32 Bapupara, Siliguri'}]
]

def get_station_index(stations, station_name):
    for station_list in stations:
        for station in station_list:
            if station['StationName'] == station_name:
                return station["Unnamed: 0"]
    return None

# AQI Prediction Endpoint (updated)
@app.post("/predict-new")
async def predict_model_2(data: InputDataModel2):
    station_index = get_station_index(stations, data.station_name)
    
    if station_index is None:
        raise HTTPException(status_code=404, detail="Station not found")
    
    input_values = [station_index, data.year, data.month, data.day, data.hour, data.dayOfWeek, data.isWeekend]
    input_array = np.array(input_values).astype("float32").reshape(1, -1)
    
    prediction = model_2.predict(input_array)
    aqi_value = int(prediction[0][4])+3.6  # Convert AQI to integer
    molecules = [int(value) for value in prediction[0][:12]]  # Convert all molecule values to integers
    
    response_data = {"aqi": aqi_value, "molecules": molecules}
    
    if aqi_value < 100: 
        prompt = f"Given the following molecule values: {molecules}, list industries like steel industry that could be responsible for the high AQI values and way to reduce them , gimme answer of points exactly what i ask for none other extra words should be there like ' 'or any  but these 8 points of 4 ways to reduces them  and 4 industry list  " 
            
        print(prompt) 
        model=Ollama(model="llama3.1")

        llm_response = model.invoke(prompt)

        top_industries = llm_response
        response_data["top_industries"] = [top_industries]
    else:
        response_data["top_industries"] = ["Air quality is within acceptable limits."]
    
    print(response_data)
    return response_data


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore(text_chunks):
    embeddings = NomicEmbeddings(
        model="nomic-embed-text-v1.5"
    )
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    model = Ollama(model="llama3.1")
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=NomicEmbeddings(model="nomic-embed-text-v1.5"))
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=model,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain



def get_pdf_text(pdf_docs):
    text = ""
    pdf_reader = PdfReader(pdf_docs)
    for page in pdf_reader.pages:
        text +=page.extract_text()
    return text

docs=get_pdf_text("VYIjWaJJuE.pdf")

text_chunks = get_text_chunks(docs)
                

vectorstore = get_vectorstore(text_chunks)
                

conversation_chain = get_conversation_chain(vectorstore)
                

# Chatbot endpoint
@app.post("/chatbot")
async def chatbot(data: ChatMessage):
        user_input = data.message
        response = conversation_chain(user_input+"be concise with yours answers it should not exceed more than 100 unique words")
        print(response)
        return {"response": response['answer']}
