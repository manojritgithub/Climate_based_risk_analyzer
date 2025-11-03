import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify, send_file
import requests
import sqlite3
from datetime import datetime
import matplotlib
import csv
from io import StringIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

matplotlib.use('Agg')

app = Flask(__name__)


API_KEY = "a994fa3a4c09ff4e1d2f0261028cf057"
DB_PATH = "climate_data.db"

# ---------------- Safety Tips ----------------
SAFETY_TIPS = {
    "Delhi": [
        "Avoid exercising outdoors when AQI is high.",
        "Keep windows closed during heavy pollution.",
        "Use air purifiers indoors if possible.",
        "Prefer N95 masks near traffic zones.",
        "Stay hydrated and wash hands/face thoroughly."
    ],
    "Chennai": [
        "Drink water frequently to avoid dehydration.",
        "Wear light, breathable clothing in heatwaves.",
        "Avoid going outdoors in heavy rainfall.",
        "Monitor local weather for UV and rain alerts.",
        "Use sunscreen when outside."
    ],
    "Mumbai": [
        "Humidity spikes: Carry a water bottle.",
        "Heat & humidity: Choose shade during midday.",
        "AQI moderate: Sensitive groups should consider masking.",
        "Check monsoon advisories daily."
    ],
    "default": [
        "Limit outdoor activity in poor AQI.",
        "Wear a mask if AQI is over 100.",
        "Stay hydrated in hot weather.",
        "Monitor local advisories about pollution, UV, and heat.",
        "Check for weather and pollution alerts."
    ]
}


def get_safety_tips(city, risk_level):
    base_city = city.title() if city else "default"
    tips = SAFETY_TIPS.get(base_city, SAFETY_TIPS["default"]).copy()
    if risk_level == "High":
        tips.append("High Risk: Stay indoors whenever possible.")
        tips.append("Sensitive groups should avoid all outdoor exposure.")
    elif risk_level == "Medium":
        tips.append(
            "Moderate Risk: Asthmatics and elderly should minimize time outdoors.")
    return tips


# ---------------- Database Init ----------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            city TEXT,
            lat REAL,
            lon REAL,
            temperature REAL,
            humidity REAL,
            aqi INTEGER,
            condition TEXT,
            risk_level TEXT
        )
        """
    )
    conn.commit()
    conn.close()


# ---------------- Risk Calculation ----------------
def score_and_level(temp, humidity, aqi):
    score = 0
    if aqi is not None:
        if aqi > 300:
            score += 3
        elif aqi > 200:
            score += 2
        elif aqi > 100:
            score += 1
    if temp is not None and humidity is not None:
        if temp > 38 and humidity > 60:
            score += 2
        if temp < 10:
            score += 1
    if score == 0:
        return score, "Low"
    elif score <= 2:
        return score, "Medium"
    else:
        return score, "High"


def save_record(city, lat, lon, temp, humidity, aqi, condition, risk_level):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO records (ts, city, lat, lon, temperature, humidity, aqi, condition, risk_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (datetime.utcnow().isoformat(), city, lat, lon,
         temp, humidity, aqi, condition, risk_level),
    )
    conn.commit()
    conn.close()


# ---------------- AQI Fetch ----------------
def fetch_aqi(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    r = requests.get(url).json()
    try:
        data = r['list'][0]
        ow_aqi_idx = data['main']['aqi']
        mapping = {1: 50, 2: 100, 3: 150, 4: 200, 5: 300}
        return mapping.get(ow_aqi_idx, None), float(lat), float(lon)
    except Exception:
        return None, float(lat), float(lon)


# ---------------- Routes ----------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get_weather")
def get_weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    if not lat or not lon:
        return jsonify({"error": "Missing coordinates"}), 400
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    response = requests.get(url).json()
    if response.get("cod") != 200:
        return jsonify({"error": response.get("message", "Unable to fetch weather")})
    temp = response['main']['temp']
    humidity = response['main']['humidity']
    condition = response['weather'][0]['description']
    city = response.get('name') or ""
    aqi, lat_f, lon_f = fetch_aqi(lat, lon)
    score, risk_level = score_and_level(temp, humidity, aqi)
    save_record(city, lat_f, lon_f, temp, humidity, aqi, condition, risk_level)
    tips = get_safety_tips(city, risk_level)
    return jsonify({
        "city": city,
        "temperature": temp,
        "humidity": humidity,
        "condition": condition,
        "aqi": aqi,
        "risk_level": risk_level,
        "tips": tips,
        "lat": lat_f,
        "lon": lon_f
    })


@app.route("/get_weather_manual")
def get_weather_manual():
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"error": "City is required"}), 400
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url).json()
    if response.get("cod") != 200:
        return jsonify({"error": "City not found. Please try again."})
    temp = response['main']['temp']
    humidity = response['main']['humidity']
    condition = response['weather'][0]['description']
    lat = response['coord']['lat']
    lon = response['coord']['lon']
    city_name = response.get('name') or city
    aqi, lat_f, lon_f = fetch_aqi(lat, lon)
    score, risk_level = score_and_level(temp, humidity, aqi)
    save_record(city_name, lat_f, lon_f, temp,
                humidity, aqi, condition, risk_level)
    tips = get_safety_tips(city_name, risk_level)
    return jsonify({
        "city": city_name,
        "temperature": temp,
        "humidity": humidity,
        "condition": condition,
        "aqi": aqi,
        "risk_level": risk_level,
        "tips": tips,
        "lat": lat_f,
        "lon": lon_f
    })


@app.route("/download_report")
def download_report():
    city = request.args.get("city", "").strip()
    fmt = request.args.get("format", "csv").lower()
    if not city:
        return jsonify({"error": "City is required"}), 400

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT ts, city, lat, lon, temperature, humidity, aqi, condition, risk_level FROM records WHERE city=? ORDER BY ts DESC LIMIT 50",
        (city.title(),)
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return jsonify({"error": "No records found for this city."}), 404

    if fmt == "pdf":
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        pdf.setTitle(f"{city} Climate Report")
        pdf.drawString(30, 750, f"Climate Report for {city.title()}")
        pdf.drawString(
            30, 735, "Timestamp, Temperature, Humidity, AQI, Condition, Risk Level")
        y = 720
        for r in rows:
            line = f"{r[0][:19]}, {r[4]}°C, {r[5]}%, {r[6]}, {r[7]}, {r[8]}"
            pdf.drawString(30, y, line)
            y -= 15
            if y < 50:
                pdf.showPage()
                y = 750
        pdf.save()
        buffer.seek(0)
        return send_file(
            buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"{city}_climate_report.pdf"
        )
    else:
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Timestamp", "City", "Latitude", "Longitude",
                        "Temperature", "Humidity", "AQI", "Condition", "Risk Level"])
        writer.writerows(rows)
        output.seek(0)
        return send_file(
            output,
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"{city}_climate_report.csv"
        )


# ---------------- Chatbot ----------------
CHATBOT_RESPONSES = {
    "hello": "Hello! 👋 I'm your Climate Health Assistant. You can ask me about AQI, weather, or health tips.",
    "tips": "Try asking like 'tips for Delhi' or 'tips for hot weather'.",
    "aqi": "AQI (Air Quality Index) tells you how clean or polluted the air is. 0-50 is good, 51-100 is moderate, 101+ can be risky.",
    "heat": "🥵 Heat Safety: Stay hydrated, wear light clothes, avoid direct sunlight during noon.",
    "cold": "❄️ Cold Safety: Wear warm clothes, cover your ears/hands, and avoid long exposure outdoors.",
    "pollution": "😷 Pollution Safety: Use N95 masks outside, close windows during high AQI, and use air purifiers indoors if possible.",
    "default": "I'm not sure 🤔. You can ask me about AQI, heat, cold, pollution, or city safety tips."
}


@app.route("/chatbot", methods=["POST"])
def chatbot():
    user_msg = request.json.get("message", "").lower()
    reply = CHATBOT_RESPONSES["default"]
    for key, response in CHATBOT_RESPONSES.items():
        if key in user_msg:
            reply = response
            break
    return jsonify({"reply": reply})


# ---------------- Init DB + Run ----------------
init_db()

if __name__ == "__main__":
    app.run(debug=True)
