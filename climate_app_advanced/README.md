
# Climate-Based Health Risk Analyzer (Advanced)

Features:
- GPS auto-detect + manual city input
- Current weather (temp/humidity/condition) from OpenWeather (free)
- AQI via OpenWeather Air Pollution API (free)
- Rule-based health risk analysis (as messages + overall level)
- SQLite storage of each check
- Risk level trend chart (last 7 checks)

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # on Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Replace the placeholder in `app.py`:
   ```python
   API_KEY = "YOUR_OPENWEATHER_API_KEY"
   ```

3. Run:
   ```bash
   python app.py
   ```

4. Open your browser at `http://127.0.0.1:5000/`

## Notes
- The trend chart shows *risk levels only* (Low/Medium/High) over the last 7 checks.
- AQI mapping uses OpenWeather's 1..5 index mapped to ~50..300 for simplicity.
- The SQLite DB file `climate_data.db` is created in the project root automatically.
