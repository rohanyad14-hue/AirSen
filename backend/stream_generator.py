import math
import random
import numpy as np
import pandas as pd
from datetime import datetime

# Comprehensive global airport hubs spanning all continents
GLOBAL_AIRPORTS = {
    # North America
    'JFK': {'name': 'New York JFK', 'lat': 40.6413, 'lon': -73.7781, 'region': 'North America', 'country': 'USA'},
    'LAX': {'name': 'Los Angeles Intl', 'lat': 33.9416, 'lon': -118.4085, 'region': 'North America', 'country': 'USA'},
    'ORD': {'name': "Chicago O'Hare", 'lat': 41.9742, 'lon': -87.9073, 'region': 'North America', 'country': 'USA'},
    'ATL': {'name': 'Atlanta Hartsfield', 'lat': 33.6407, 'lon': -84.4277, 'region': 'North America', 'country': 'USA'},
    'DFW': {'name': 'Dallas/Fort Worth', 'lat': 32.8998, 'lon': -97.0403, 'region': 'North America', 'country': 'USA'},
    'SFO': {'name': 'San Francisco', 'lat': 37.6213, 'lon': -122.3790, 'region': 'North America', 'country': 'USA'},
    'YYZ': {'name': 'Toronto Pearson', 'lat': 43.6777, 'lon': -79.6248, 'region': 'North America', 'country': 'Canada'},
    'MEX': {'name': 'Mexico City Intl', 'lat': 19.4361, 'lon': -99.0719, 'region': 'North America', 'country': 'Mexico'},
    
    # Europe
    'LHR': {'name': 'London Heathrow', 'lat': 51.4700, 'lon': -0.4543, 'region': 'Europe', 'country': 'UK'},
    'CDG': {'name': 'Paris Charles de Gaulle', 'lat': 49.0097, 'lon': 2.5479, 'region': 'Europe', 'country': 'France'},
    'FRA': {'name': 'Frankfurt Main', 'lat': 50.0379, 'lon': 8.5622, 'region': 'Europe', 'country': 'Germany'},
    'AMS': {'name': 'Amsterdam Schiphol', 'lat': 52.3105, 'lon': 4.7683, 'region': 'Europe', 'country': 'Netherlands'},
    'MAD': {'name': 'Madrid Barajas', 'lat': 40.4839, 'lon': -3.5680, 'region': 'Europe', 'country': 'Spain'},
    'IST': {'name': 'Istanbul Airport', 'lat': 41.2753, 'lon': 28.7519, 'region': 'Europe', 'country': 'Turkey'},
    'FCO': {'name': 'Rome Fiumicino', 'lat': 41.8003, 'lon': 12.2389, 'region': 'Europe', 'country': 'Italy'},
    'ZRH': {'name': 'Zurich Airport', 'lat': 47.4582, 'lon': 8.5555, 'region': 'Europe', 'country': 'Switzerland'},

    # Asia & Middle East
    'DXB': {'name': 'Dubai International', 'lat': 25.2532, 'lon': 55.3657, 'region': 'Middle East', 'country': 'UAE'},
    'DOH': {'name': 'Doha Hamad', 'lat': 25.2731, 'lon': 51.6081, 'region': 'Middle East', 'country': 'Qatar'},
    'SIN': {'name': 'Singapore Changi', 'lat': 1.3644, 'lon': 103.9915, 'region': 'Asia', 'country': 'Singapore'},
    'HND': {'name': 'Tokyo Haneda', 'lat': 35.5494, 'lon': 139.7798, 'region': 'Asia', 'country': 'Japan'},
    'NRT': {'name': 'Tokyo Narita', 'lat': 35.7720, 'lon': 140.3929, 'region': 'Asia', 'country': 'Japan'},
    'HKG': {'name': 'Hong Kong Intl', 'lat': 22.3080, 'lon': 113.9185, 'region': 'Asia', 'country': 'Hong Kong'},
    'DEL': {'name': 'Delhi Indira Gandhi', 'lat': 28.5562, 'lon': 77.1000, 'region': 'Asia', 'country': 'India'},
    'BOM': {'name': 'Mumbai Shivaji', 'lat': 19.0896, 'lon': 72.8656, 'region': 'Asia', 'country': 'India'},
    'ICN': {'name': 'Seoul Incheon', 'lat': 37.4602, 'lon': 126.4407, 'region': 'Asia', 'country': 'South Korea'},
    'BKK': {'name': 'Bangkok Suvarnabhumi', 'lat': 13.6900, 'lon': 100.7501, 'region': 'Asia', 'country': 'Thailand'},
    'PVG': {'name': 'Shanghai Pudong', 'lat': 31.1443, 'lon': 121.8083, 'region': 'Asia', 'country': 'China'},

    # South America
    'GRU': {'name': 'São Paulo Guarulhos', 'lat': -23.4356, 'lon': -46.4731, 'region': 'South America', 'country': 'Brazil'},
    'EZE': {'name': 'Buenos Aires Ezeiza', 'lat': -34.8222, 'lon': -58.5358, 'region': 'South America', 'country': 'Argentina'},
    'BOG': {'name': 'Bogotá El Dorado', 'lat': 4.7016, 'lon': -74.1469, 'region': 'South America', 'country': 'Colombia'},
    'SCL': {'name': 'Santiago Arturo Benitez', 'lat': -33.3930, 'lon': -70.7858, 'region': 'South America', 'country': 'Chile'},

    # Africa
    'JNB': {'name': 'Johannesburg OR Tambo', 'lat': -26.1367, 'lon': 28.2411, 'region': 'Africa', 'country': 'South Africa'},
    'CAI': {'name': 'Cairo International', 'lat': 30.1219, 'lon': 31.4056, 'region': 'Africa', 'country': 'Egypt'},
    'NBO': {'name': 'Nairobi Jomo Kenyatta', 'lat': -1.3192, 'lon': 36.9275, 'region': 'Africa', 'country': 'Kenya'},
    'ADD': {'name': 'Addis Ababa Bole', 'lat': 8.9779, 'lon': 38.7993, 'region': 'Africa', 'country': 'Ethiopia'},
    'LOS': {'name': 'Lagos Murtala Muhammed', 'lat': 6.5774, 'lon': 3.3212, 'region': 'Africa', 'country': 'Nigeria'},

    # Oceania
    'SYD': {'name': 'Sydney Kingsford Smith', 'lat': -33.9399, 'lon': 151.1753, 'region': 'Oceania', 'country': 'Australia'},
    'MEL': {'name': 'Melbourne Airport', 'lat': -37.6690, 'lon': 144.8410, 'region': 'Oceania', 'country': 'Australia'},
    'AKL': {'name': 'Auckland Airport', 'lat': -37.0082, 'lon': 174.7850, 'region': 'Oceania', 'country': 'New Zealand'},
}

# Major international carriers with authentic IATA callsign prefixes
GLOBAL_AIRLINES = {
    'Emirates': {'code': 'EK', 'callsign': 'UAE', 'country': 'UAE'},
    'Qatar Airways': {'code': 'QR', 'callsign': 'QTR', 'country': 'Qatar'},
    'Singapore Airlines': {'code': 'SQ', 'callsign': 'SIA', 'country': 'Singapore'},
    'Air India': {'code': 'AI', 'callsign': 'AIC', 'country': 'India'},
    'Cathay Pacific': {'code': 'CX', 'callsign': 'CPA', 'country': 'Hong Kong'},
    'All Nippon Airways': {'code': 'NH', 'callsign': 'ANA', 'country': 'Japan'},
    'Japan Airlines': {'code': 'JL', 'callsign': 'JAL', 'country': 'Japan'},
    'Korean Air': {'code': 'KE', 'callsign': 'KAL', 'country': 'South Korea'},
    'Turkish Airlines': {'code': 'TK', 'callsign': 'THY', 'country': 'Turkey'},
    'Lufthansa': {'code': 'LH', 'callsign': 'DLH', 'country': 'Germany'},
    'British Airways': {'code': 'BA', 'callsign': 'BAW', 'country': 'UK'},
    'Air France': {'code': 'AF', 'callsign': 'AFR', 'country': 'France'},
    'Qantas': {'code': 'QF', 'callsign': 'QFA', 'country': 'Australia'},
    'LATAM Airlines': {'code': 'LA', 'callsign': 'LAN', 'country': 'Chile/Brazil'},
    'Ethiopian Airlines': {'code': 'ET', 'callsign': 'ETH', 'country': 'Ethiopia'},
    'Delta Air Lines': {'code': 'DL', 'callsign': 'DAL', 'country': 'USA'},
    'American Airlines': {'code': 'AA', 'callsign': 'AAL', 'country': 'USA'},
    'United Airlines': {'code': 'UA', 'callsign': 'UAL', 'country': 'USA'},
    'Air Canada': {'code': 'AC', 'callsign': 'ACA', 'country': 'Canada'},
}

AIRCRAFT_MODELS = ['A380-800', 'B777-300ER', 'A350-900', 'B787-9', 'A330-300', 'B737-800', 'A321neo']
WEATHER_CONDITIONS = ['Clear', 'Cloudy', 'Rain', 'Thunderstorm', 'High Winds', 'Fog', 'Snow/Blizzard']

def calculate_haversine_distance(orig_code: str, dest_code: str) -> float:
    """Calculates great-circle distance in miles between any two global airports."""
    c1 = GLOBAL_AIRPORTS.get(orig_code)
    c2 = GLOBAL_AIRPORTS.get(dest_code)
    if not c1 or not c2:
        return 1500.0
    lat1, lon1 = c1['lat'], c1['lon']
    lat2, lon2 = c2['lat'], c2['lon']
    r = 3958.8  # Earth radius in miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(max(0.0, min(1.0, a))))
    return round(r * c, 1)

class FlightWeatherStreamGenerator:
    """
    Flightradar24-Scale Global Aviation Telemetry Simulator.
    Simulates high-density commercial air traffic (1,200+ simultaneous aircraft)
    traversing worldwide great-circle airways alongside dynamic atmospheric weather.
    """
    def __init__(self):
        self.storm_shock_hub = None
        self.storm_shock_counter = 0
        self.airport_codes = list(GLOBAL_AIRPORTS.keys())
        self.airline_names = list(GLOBAL_AIRLINES.keys())
        
        # Airport baseline meteorological state
        self.airport_weather = {}
        for ap in self.airport_codes:
            self.airport_weather[ap] = {
                'weather_condition': 'Clear',
                'wind_speed_kts': round(random.uniform(5.0, 16.0), 1),
                'visibility_miles': round(random.uniform(8.0, 10.0), 1),
                'precipitation_mm': 0.0,
                'congestion_index': round(random.uniform(15.0, 48.0), 1),
                'ground_stop_risk': 'NORMAL'
            }

    def trigger_storm_shock(self, target_hub: str = 'ORD', duration_steps: int = 25):
        """Triggers an extreme weather shock / supercell / typhoon at a specific airport hub."""
        if target_hub in self.airport_weather:
            self.storm_shock_hub = target_hub
            self.storm_shock_counter = duration_steps

    def update_hub_weather(self):
        """Continuously evolves meteorological conditions across all global hubs."""
        for ap in self.airport_codes:
            if self.storm_shock_hub == ap and self.storm_shock_counter > 0:
                self.storm_shock_counter -= 1
                if self.storm_shock_counter <= 0:
                    self.storm_shock_hub = None
                
                # Severe convective weather shock
                self.airport_weather[ap] = {
                    'weather_condition': random.choice(['Thunderstorm', 'High Winds', 'Snow/Blizzard']),
                    'wind_speed_kts': round(random.uniform(38.0, 58.0), 1),
                    'visibility_miles': round(random.uniform(0.5, 2.2), 1),
                    'precipitation_mm': round(random.uniform(18.0, 42.0), 1),
                    'congestion_index': round(random.uniform(85.0, 99.0), 1),
                    'ground_stop_risk': 'SEVERE GROUND STOP'
                }
            else:
                # Stochastic ambient variation
                cond = np.random.choice(
                    WEATHER_CONDITIONS,
                    p=[0.50, 0.22, 0.12, 0.06, 0.05, 0.03, 0.02]
                )
                wind = max(3.0, round(np.random.normal(loc=12.0, scale=6.0), 1))
                vis = min(10.0, max(1.0, round(np.random.normal(loc=9.0, scale=1.8), 1)))
                precip = round(random.uniform(2.0, 15.0), 1) if cond in ['Rain', 'Thunderstorm', 'Snow/Blizzard'] else 0.0
                congestion = min(100.0, max(5.0, round(np.random.normal(loc=35.0, scale=15.0), 1)))
                
                risk = 'NORMAL'
                if wind > 30.0 or vis < 3.0 or congestion > 75.0:
                    risk = 'MODERATE DELAYS'
                if wind > 40.0 or cond == 'Thunderstorm':
                    risk = 'HIGH DELAY RISK'

                self.airport_weather[ap] = {
                    'weather_condition': cond,
                    'wind_speed_kts': wind,
                    'visibility_miles': vis,
                    'precipitation_mm': precip,
                    'congestion_index': congestion,
                    'ground_stop_risk': risk
                }

    def get_weather_df(self) -> pd.DataFrame:
        """Returns the current weather snapshot for all global airports."""
        records = []
        now = datetime.now()
        for ap, w in self.airport_weather.items():
            meta = GLOBAL_AIRPORTS.get(ap, {})
            records.append({
                'airport_code': ap,
                'airport_name': meta.get('name', ap),
                'region': meta.get('region', 'Global'),
                'country': meta.get('country', ''),
                'weather_condition': w['weather_condition'],
                'wind_speed_kts': w['wind_speed_kts'],
                'visibility_miles': w['visibility_miles'],
                'precipitation_mm': w['precipitation_mm'],
                'congestion_index': w['congestion_index'],
                'ground_stop_risk': w['ground_stop_risk'],
                'updated_at': now
            })
        return pd.DataFrame(records)

    def generate_flight_event(self) -> dict:
        """Generates a realistic international commercial flight telemetry event."""
        now = datetime.now()
        airline_name = random.choice(self.airline_names)
        airline_info = GLOBAL_AIRLINES.get(airline_name, {'code': 'FL', 'country': ''})
        code_prefix = airline_info['code']
        flight_num = random.randint(100, 2999)
        flight_id = f"{code_prefix}-{flight_num}"
        
        origin, destination = random.sample(self.airport_codes, 2)
        dist = calculate_haversine_distance(origin, destination)
        
        dest_weather = self.airport_weather.get(destination, {})
        weather_cond = dest_weather.get('weather_condition', 'Clear')
        wind = dest_weather.get('wind_speed_kts', 12.0)
        vis = dest_weather.get('visibility_miles', 9.0)
        precip = dest_weather.get('precipitation_mm', 0.0)
        congestion = dest_weather.get('congestion_index', 30.0)

        status = np.random.choice(['Airborne', 'Approaching', 'Taxiing', 'Scheduled'], p=[0.72, 0.16, 0.08, 0.04])
        altitude = random.randint(31000, 42000) if status == 'Airborne' else (random.randint(3000, 14000) if status == 'Approaching' else 0)
        speed = random.randint(450, 540) if status == 'Airborne' else (random.randint(180, 270) if status == 'Approaching' else 25)

        return {
            'timestamp': now,
            'flight_id': flight_id,
            'airline': airline_name,
            'origin': origin,
            'destination': destination,
            'scheduled_dep_hour': now.hour,
            'distance_miles': float(dist),
            'altitude_ft': int(altitude),
            'speed_kts': int(speed),
            'status': status,
            'weather_condition': weather_cond,
            'wind_speed_kts': float(wind),
            'visibility_miles': float(vis),
            'precipitation_mm': float(precip),
            'congestion_index': float(congestion),
            'predicted_delay_min': 0.0,
            'delay_severity': 'On-Time (0-15m)',
            'primary_cause': 'Normal Flow',
            'confidence_score': 0.95
        }

    def generate_batch(self, count: int = 40) -> pd.DataFrame:
        """Generates a batch of global flight telemetry records and updates weather."""
        self.update_hub_weather()
        events = [self.generate_flight_event() for _ in range(count)]
        return pd.DataFrame(events)

    def generate_high_density_global_airspace(self, target_count: int = 1200) -> pd.DataFrame:
        """
        Synthesizes high-density global airspace traffic (Flightradar24 scale).
        Populates worldwide routes with active commercial flights.
        """
        self.update_hub_weather()
        events = [self.generate_flight_event() for _ in range(target_count)]
        return pd.DataFrame(events)
