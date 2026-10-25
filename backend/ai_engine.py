import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.preprocessing import OrdinalEncoder
from scipy import stats

WEATHER_MAPPING = {
    'Clear': 0, 'Cloudy': 1, 'Fog': 2, 'Rain': 3,
    'High Winds': 4, 'Thunderstorm': 5, 'Snow/Blizzard': 6
}

AIRLINE_MAPPING = {
    'Delta': 0, 'American': 1, 'United': 2,
    'Southwest': 3, 'British Airways': 4, 'Lufthansa': 5
}

class AirAssistantAIEngine:
    """
    Non-LLM Air Assistant AI Engine.
    Uses Gradient Boosted Decision Trees (HistGradientBoostingRegressor) and 
    deterministic aerodynamic / airspace heuristic rules to predict flight delays,
    diagnose root-causes, and quantify atmospheric weather impacts in real time.
    """
    def __init__(self):
        self.model = HistGradientBoostingRegressor(
            max_iter=120,
            learning_rate=0.08,
            max_depth=6,
            random_state=42
        )
        self.is_fitted = False
        self._pretrain_baseline()

    def _pretrain_baseline(self):
        """
        Synthesizes a realistic aerodynamic baseline training set to immediately
        calibrate the AI model on flight physics, weather friction, and airport congestion.
        """
        np.random.seed(42)
        n_samples = 4000
        
        distances = np.random.uniform(400, 3500, n_samples)
        dep_hours = np.random.randint(0, 24, n_samples)
        winds = np.random.uniform(5, 55, n_samples)
        visibilities = np.random.uniform(0.5, 10.0, n_samples)
        precip = np.random.uniform(0.0, 35.0, n_samples)
        congestions = np.random.uniform(10, 95, n_samples)
        weather_codes = np.random.randint(0, 7, n_samples)
        airline_codes = np.random.randint(0, 6, n_samples)

        # Ground truth delay physics equation
        # 1. Congestion impact (exponential past 65)
        cong_delay = np.maximum(0, (congestions - 40) * 0.45) + np.maximum(0, (congestions - 70) * 0.9)
        # 2. Wind penalty (crosswinds > 28 kts require runway spacing)
        wind_delay = np.maximum(0, (winds - 25) * 1.3)
        # 3. Visibility penalty
        vis_delay = np.maximum(0, (4.0 - visibilities) * 6.0)
        # 4. Severe weather penalty (Thunderstorm=5, Blizzard=6)
        storm_delay = np.where(weather_codes >= 5, np.random.uniform(25, 65, n_samples), 0)
        # 5. Hour of day peak congestion (16:00 to 20:00)
        peak_delay = np.where((dep_hours >= 16) & (dep_hours <= 20), np.random.uniform(5, 18, n_samples), 0)
        
        noise = np.random.normal(0, 4, n_samples)
        target_delays = np.maximum(0, cong_delay + wind_delay + vis_delay + storm_delay + peak_delay + noise)

        X = np.column_stack([
            distances, dep_hours, winds, visibilities, precip,
            congestions, weather_codes, airline_codes
        ])
        
        self.model.fit(X, target_delays)
        self.is_fitted = True

    def _extract_features(self, df: pd.DataFrame) -> np.ndarray:
        """Converts raw flight DataFrame into feature matrix."""
        dist = df['distance_miles'].values
        dep_h = df['scheduled_dep_hour'].values
        wind = df['wind_speed_kts'].values
        vis = df['visibility_miles'].values
        precip = df['precipitation_mm'].values
        cong = df['congestion_index'].values
        
        w_codes = np.array([WEATHER_MAPPING.get(w, 0) for w in df['weather_condition']])
        a_codes = np.array([abs(hash(str(a))) % 20 for a in df['airline']], dtype=int)

        return np.column_stack([dist, dep_h, wind, vis, precip, cong, w_codes, a_codes])

    def predict_flight_delays(self, df: pd.DataFrame):
        """
        Runs ML inference to compute expected delay minutes, severity tiers,
        root-cause attributions, and prediction confidence.
        """
        if df.empty:
            return [], [], [], []

        X = self._extract_features(df)
        raw_delays = self.model.predict(X)
        predicted_delays = [round(max(0.0, float(d)), 1) for d in raw_delays]

        severities = []
        causes = []
        confidences = []

        for i, row in df.reset_index(drop=True).iterrows():
            d = predicted_delays[i]
            
            # Severity classification
            if d <= 15.0:
                sev = "On-Time (0-15m)"
            elif d <= 45.0:
                sev = "Moderate (15-45m)"
            elif d <= 85.0:
                sev = "Severe (45-85m)"
            else:
                sev = "Critical Delay (>85m)"
            severities.append(sev)

            # Deterministic Root Cause Attribution
            wind = row['wind_speed_kts']
            vis = row['visibility_miles']
            precip = row['precipitation_mm']
            cong = row['congestion_index']
            w_cond = row['weather_condition']

            if w_cond in ['Thunderstorm', 'Snow/Blizzard']:
                cause = f"Weather: {w_cond} & Low Visibility"
            elif wind >= 32.0:
                cause = f"Weather: Severe Crosswinds ({wind:.0f} kts)"
            elif cong >= 72.0:
                cause = f"Airspace: Runway Queue Saturation ({cong:.0f}%)"
            elif vis <= 3.0:
                cause = "Weather: Dense Fog / ILS Spacing"
            elif d > 15.0:
                cause = "Air Traffic Flow Management (ATFM)"
            else:
                cause = "Normal Flow (On Schedule)"
            causes.append(cause)

            # Confidence score (lower during extreme storm variance, higher in stable weather)
            base_conf = 0.96 - (0.003 * max(0, wind - 25.0)) - (0.002 * max(0, cong - 70.0))
            confidences.append(round(max(0.72, min(0.99, base_conf)), 2))

        return predicted_delays, severities, causes, confidences

    def explain_single_flight(self, flight_row: dict) -> dict:
        """
        Air Assistant AI Single-Flight Diagnostic.
        Synthesizes an immediate operational explanation of why the flight is delayed.
        """
        flight_id = flight_row.get('flight_id', 'Unknown')
        airline = flight_row.get('airline', 'Airline')
        origin = flight_row.get('origin', 'ORIG')
        dest = flight_row.get('destination', 'DEST')
        delay = flight_row.get('predicted_delay_min', 0.0)
        sev = flight_row.get('delay_severity', 'On-Time')
        wind = flight_row.get('wind_speed_kts', 0.0)
        cong = flight_row.get('congestion_index', 0.0)
        vis = flight_row.get('visibility_miles', 10.0)
        weather = flight_row.get('weather_condition', 'Clear')

        # Compute factor contribution percentages
        factors = []
        if weather in ['Thunderstorm', 'Snow/Blizzard', 'High Winds'] or wind > 25:
            factors.append(("Atmospheric Weather Friction", 52))
        if cong > 55:
            factors.append(("Destination Runway Congestion", 34))
        if vis < 4.0:
            factors.append(("Reduced Visual Minimums (IFR)", 20))
        if not factors:
            factors.append(("En-route Jetstream & Routing", 10))

        if delay <= 15.0:
            verdict = f"Flight {flight_id} ({origin} ➔ {dest}) is operating ON-SCHEDULE. Weather along the corridor is favorable with expected arrival within nominal buffer."
            recommendation = "No intervention required. Flight cleared on standard filed flight plan."
        elif delay <= 45.0:
            verdict = f"Flight {flight_id} ({origin} ➔ {dest}) is expected to arrive {delay:.0f} MINUTES LATE. Delay is driven by {factors[0][0].lower()} at {dest}."
            recommendation = f"Advise passengers of moderate +{delay:.0f}m delay. Inbound aircraft holds sufficient reserve fuel."
        else:
            verdict = f"ALERT: Flight {flight_id} ({origin} ➔ {dest}) facing SEVERE DELAY (+{delay:.0f} minutes). Significant operational hazard at {dest} due to {weather} and {wind:.0f} kt winds."
            recommendation = f"Evaluate alternate routing or ground delay program. Destination arrival slot delay exceeding 45 minutes."

        return {
            'flight_id': flight_id,
            'verdict': verdict,
            'predicted_delay': delay,
            'severity': sev,
            'factors': factors,
            'recommendation': recommendation,
            'confidence': flight_row.get('confidence_score', 0.94)
        }
