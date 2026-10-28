import os
import time
import math
import logging
import threading
import urllib.request
import urllib.parse
import json
import pandas as pd
import numpy as np
from datetime import datetime
from backend.stream_generator import GLOBAL_AIRPORTS, calculate_haversine_distance

logger = logging.getLogger(__name__)

# OpenSky OAuth and API endpoints
OPENSKY_TOKEN_URL = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
OPENSKY_STATES_URL = "https://opensky-network.org/api/states/all"

# Default credentials provided for OpenSky OAuth API client
DEFAULT_CLIENT_ID = os.getenv("OPENSKY_CLIENT_ID", "vittestuser1-api-client")
DEFAULT_CLIENT_SECRET = os.getenv("OPENSKY_CLIENT_SECRET", "fTcm0AvUIM5NdxWNvp7GwC3acqfykKSB")

# Comprehensive mapping from 3-letter ICAO callsign prefixes to international airlines
ICAO_PREFIX_TO_AIRLINE = {
    'UAE': 'Emirates',
    'QTR': 'Qatar Airways',
    'SIA': 'Singapore Airlines',
    'AIC': 'Air India',
    'CPA': 'Cathay Pacific',
    'ANA': 'All Nippon Airways',
    'JAL': 'Japan Airlines',
    'KAL': 'Korean Air',
    'THY': 'Turkish Airlines',
    'DLH': 'Lufthansa',
    'BAW': 'British Airways',
    'AFR': 'Air France',
    'QFA': 'Qantas',
    'LAN': 'LATAM Airlines',
    'ETH': 'Ethiopian Airlines',
    'DAL': 'Delta Air Lines',
    'AAL': 'American Airlines',
    'UAL': 'United Airlines',
    'ACA': 'Air Canada',
    'KLM': 'KLM Royal Dutch',
    'SWR': 'Swiss International Air',
    'AUA': 'Austrian Airlines',
    'IBE': 'Iberia',
    'AZA': 'ITA Airways',
    'TAP': 'TAP Air Portugal',
    'SAS': 'Scandinavian Airlines',
    'FIN': 'Finnair',
    'VIR': 'Virgin Atlantic',
    'ETD': 'Etihad Airways',
    'OMA': 'Oman Air',
    'GFA': 'Gulf Air',
    'RJA': 'Royal Jordanian',
    'MEA': 'Middle East Airlines',
    'SVA': 'Saudia',
    'RAM': 'Royal Air Maroc',
    'EGY': 'EgyptAir',
    'KQA': 'Kenya Airways',
    'SAA': 'South African Airways',
    'CCA': 'Air China',
    'CES': 'China Eastern',
    'CSN': 'China Southern',
    'EVA': 'EVA Air',
    'CAL': 'China Airlines',
    'MAS': 'Malaysia Airlines',
    'THA': 'Thai Airways',
    'GIA': 'Garuda Indonesia',
    'VNM': 'Vietnam Airlines',
    'PAL': 'Philippine Airlines',
    'ANZ': 'Air New Zealand',
    'AMX': 'Aeromexico',
    'AVA': 'Avianca',
    'ARG': 'Aerolineas Argentinas',
    'GLO': 'Gol Transportes Aéreos',
    'TAM': 'LATAM Brasil',
    'SWA': 'Southwest Airlines',
    'JBU': 'JetBlue Airways',
    'ASA': 'Alaska Airlines',
    'FFT': 'Frontier Airlines',
    'NKS': 'Spirit Airlines',
    'WJA': 'WestJet',
    'RYR': 'Ryanair',
    'EZY': 'easyJet',
    'TVF': 'Transavia France',
    'WZZ': 'Wizz Air',
    'VLG': 'Vueling Airlines',
    'VOE': 'Volotea',
    'IGO': 'IndiGo',
    'SEJ': 'SpiceJet',
    'VTI': 'Vistara',
    'AXB': 'Air India Express',
}

class OpenSkyClient:
    """
    Authenticated OpenSky Network Client.
    Fetches real-world commercial flight ADS-B telemetry using OAuth2 authentication,
    normalizes real GPS coordinates, speed, and altitude, and maps to airport hubs.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(OpenSkyClient, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, client_id: str = DEFAULT_CLIENT_ID, client_secret: str = DEFAULT_CLIENT_SECRET):
        if self._initialized:
            return
        self.client_id = client_id
        self.client_secret = client_secret
        
        self.access_token = None
        self.token_expiry = 0
        self.last_fetch_time = 0
        self.cache_ttl = 10.0  # seconds to cache live states
        self.cached_states = []
        self.last_status_msg = "Initialized"
        self.last_flight_count = 0
        self.is_connected = False
        
        self._initialized = True

    def _get_access_token(self) -> str:
        """Retrieves or refreshes OAuth2 Bearer token from OpenSky auth server."""
        now = time.time()
        if self.access_token and now < (self.token_expiry - 90):
            return self.access_token

        data = urllib.parse.urlencode({
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }).encode('utf-8')

        req = urllib.request.Request(
            OPENSKY_TOKEN_URL,
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'AeroSentinel/1.0'}
        )

        with urllib.request.urlopen(req, timeout=12) as resp:
            body = json.loads(resp.read().decode('utf-8'))
            self.access_token = body.get('access_token')
            expires_in = body.get('expires_in', 1800)
            self.token_expiry = now + expires_in
            self.is_connected = True
            logger.info("OpenSky OAuth token successfully refreshed.")
            return self.access_token

    def fetch_live_states(self, force_refresh: bool = False) -> list:
        """
        Polls OpenSky states endpoint with rate-limiting and in-memory caching.
        Returns list of live flight vectors.
        """
        now = time.time()
        if not force_refresh and (now - self.last_fetch_time) < self.cache_ttl and self.cached_states:
            return self.cached_states

        token = self._get_access_token()
        req = urllib.request.Request(
            OPENSKY_STATES_URL,
            headers={
                'Authorization': f'Bearer {token}',
                'User-Agent': 'AeroSentinel/1.0'
            }
        )

        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            states = data.get('states', [])
            self.cached_states = states
            self.last_fetch_time = now
            self.last_flight_count = len(states)
            self.last_status_msg = f"Active ({len(states):,} real aircraft tracked)"
            return states

    def test_connection(self) -> dict:
        """Tests OAuth authentication and live API ping."""
        try:
            states = self.fetch_live_states(force_refresh=True)
            return {
                'success': True,
                'client_id': self.client_id,
                'total_tracked': len(states),
                'message': f"Authenticated successfully as {self.client_id}. {len(states):,} live planes online."
            }
        except Exception as e:
            self.is_connected = False
            self.last_status_msg = f"Connection error: {str(e)}"
            return {
                'success': False,
                'client_id': self.client_id,
                'total_tracked': 0,
                'message': str(e)
            }

    @staticmethod
    def _resolve_airline(callsign: str, country: str) -> str:
        """Maps callsign or country to clean commercial airline name."""
        if not callsign:
            return f"{country} Transport" if country else "International Carrier"
        
        cs = callsign.strip().upper()
        prefix3 = cs[:3]
        if prefix3 in ICAO_PREFIX_TO_AIRLINE:
            return ICAO_PREFIX_TO_AIRLINE[prefix3]
        
        prefix2 = cs[:2]
        if prefix2 in ICAO_PREFIX_TO_AIRLINE:
            return ICAO_PREFIX_TO_AIRLINE[prefix2]
            
        return f"{country} Commercial" if country and country != "None" else f"Flight {cs}"

    @staticmethod
    def _match_nearest_hubs(lat: float, lon: float, heading: float = None):
        """
        Finds the most logical Origin and Destination among the 39 global hubs.
        Uses aircraft GPS position and track heading to project origin behind and dest ahead.
        """
        distances = []
        for code, info in GLOBAL_AIRPORTS.items():
            d = math.hypot(lat - info['lat'], lon - info['lon'])
            distances.append((d, code, info))
        distances.sort(key=lambda x: x[0])

        nearest_code = distances[0][1]
        
        # If heading is available, find a destination hub that lies generally ahead
        if heading is not None and not math.isnan(heading):
            best_dest = None
            best_diff = 360.0
            for d, code, info in distances[1:]:
                # Calculate bearing from aircraft to hub
                phi1, phi2 = math.radians(lat), math.radians(info['lat'])
                d_lon = math.radians(info['lon'] - lon)
                y = math.sin(d_lon) * math.cos(phi2)
                x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(d_lon)
                bearing = (math.degrees(math.atan2(y, x)) + 360) % 360
                diff = abs((heading - bearing + 180) % 360 - 180)
                if diff < best_diff:
                    best_diff = diff
                    best_dest = code
            dest_code = best_dest if best_dest and best_diff < 90 else distances[1][1]
        else:
            dest_code = distances[1][1]

        return nearest_code, dest_code

    def get_live_flights_dataframe(self, limit: int = 120, weather_lookup: dict = None) -> pd.DataFrame:
        """
        Converts live OpenSky states into a structured DataFrame compatible with flights_stream schema.
        """
        try:
            states = self.fetch_live_states()
        except Exception as e:
            logger.error(f"Error fetching OpenSky states: {e}")
            return pd.DataFrame()

        # Filter for valid airborne or positioned flights with callsigns
        valid = [
            s for s in states 
            if s[5] is not None and s[6] is not None and s[1] and s[1].strip()
        ]

        if not valid:
            return pd.DataFrame()

        # Select a representative sample or up to limit
        if len(valid) > limit:
            # Deterministic or diverse selection across countries
            selected = valid[:limit]
        else:
            selected = valid

        records = []
        now = datetime.now()

        for s in selected:
            icao24 = str(s[0]).strip().lower()
            callsign = str(s[1]).strip().upper()
            country = str(s[2]).strip() if s[2] else 'International'
            lon = float(s[5])
            lat = float(s[6])
            baro_alt_m = s[7]
            on_ground = bool(s[8])
            vel_ms = s[9]
            true_track = s[10]
            vert_rate_ms = s[11]

            # Conversions
            alt_ft = int(round(baro_alt_m * 3.28084)) if baro_alt_m is not None else 32000
            alt_ft = max(0, min(50000, alt_ft))
            
            speed_kts = int(round(vel_ms * 1.94384)) if vel_ms is not None else 450
            speed_kts = max(0, min(700, speed_kts))

            # Status determination
            if on_ground:
                status = 'Taxiing'
            elif vert_rate_ms is not None and vert_rate_ms < -2.0 and alt_ft < 8000:
                status = 'Approaching'
            else:
                status = 'Airborne'

            airline = self._resolve_airline(callsign, country)
            orig_hub, dest_hub = self._match_nearest_hubs(lat, lon, true_track)
            dist_miles = calculate_haversine_distance(orig_hub, dest_hub)

            # Weather conditions from lookup if provided, or clean standard atmosphere
            w_info = (weather_lookup or {}).get(dest_hub, {})
            weather_cond = w_info.get('weather_condition', 'Clear')
            wind_speed = float(w_info.get('wind_speed_kts', 12.0))
            vis_miles = float(w_info.get('visibility_miles', 10.0))
            precip = float(w_info.get('precipitation_mm', 0.0))
            congestion = float(w_info.get('congestion_index', 35.0))

            records.append({
                'timestamp': now,
                'flight_id': callsign if callsign else f"ICAO-{icao24.upper()}",
                'airline': airline,
                'origin': orig_hub,
                'destination': dest_hub,
                'scheduled_dep_hour': now.hour,
                'distance_miles': float(dist_miles),
                'altitude_ft': alt_ft,
                'speed_kts': speed_kts,
                'status': status,
                'weather_condition': weather_cond,
                'wind_speed_kts': wind_speed,
                'visibility_miles': vis_miles,
                'precipitation_mm': precip,
                'congestion_index': congestion,
                'latitude': lat,
                'longitude': lon,
                'origin_country': country,
            })

        df = pd.DataFrame(records)
        return df
