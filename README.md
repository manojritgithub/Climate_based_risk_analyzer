🌍 Climate Risk Analyzer

A smart web application that analyzes environmental and weather data to assess **climate risks** such as temperature, humidity, air quality, and weather conditions — helping users make informed outdoor decisions.

---

## 🚀 Features

- 🌦️ Real-time weather and air quality data  
- 📍 Location-based analysis using geolocation  
- 🧠 AI-powered **Climate Chatbot** for user interaction  
- 🗺️ Interactive map visualization (Leaflet.js)  
- ⚠️ Dynamic risk level detection (Low, Moderate, High)  
- 💡 Helpful safety recommendations based on AQI and temperature  

---

## 🧰 Tech Stack

| Layer | Technologies Used |
|-------|--------------------|
| **Frontend** | HTML, CSS, JavaScript, Bootstrap |
| **Backend** | Flask (Python) |
| **APIs** | OpenWeatherMap API, AQI Data API |
| **Mapping** | Leaflet.js (for interactive maps) |
| **Chatbot** | Custom JavaScript chatbot integration |
| **Version Control** | Git & GitHub |

---

## 🖼️ Preview

![App Screenshot]<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/26f4a22a-c321-454d-8dcc-9dbfe53d37b7" />


> *The Climate Risk Analyzer showing temperature, humidity, AQI, and risk level for a given location.*

---

## ⚙️ Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/manojritgithub/Climate_based_risk_analyzer.git
   cd Climate_based_risk_analyzer

    Create and activate a virtual environment

python -m venv venv
venv\Scripts\activate   # On Windows
# source venv/bin/activate   # On macOS/Linux

Install dependencies

pip install -r requirements.txt

Run the Flask app

python app.py

Open in browser

    http://127.0.0.1:5000/

🔑 API Keys

    Create a free account at OpenWeatherMap

.

Generate an API key and add it to your .env file:

    WEATHER_API_KEY=your_api_key_here

🧩 Folder Structure

Climate_based_risk_analyzer/
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   └── index.html
│
├── app.py
├── requirements.txt
└── README.md

📊 Risk Levels
Level	Description	Advice
🟢 Low	Safe for outdoor activity	Enjoy the weather!
🟡 Moderate	Mild discomfort	Stay hydrated, avoid long exposure
🔴 High	Poor conditions	Limit outdoor activities
🧠 Future Enhancements

    Add user authentication and history tracking

    Integrate satellite-based pollution data

    Implement AI-based predictive risk analysis

🧑‍💻 Author

Manoj Kumar
📧 manojkumar20030316@gmail.com
🔗 GitHub Profile https://github.com/manojritgithub
📜 License

This project is open-source and available under the MIT License
