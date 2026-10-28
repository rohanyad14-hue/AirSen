import time
import threading
import pandas as pd
from datetime import datetime
from backend.database import DuckDBManager
from backend.stream_generator import FlightWeatherStreamGenerator
from backend.ai_engine import AirAssistantAIEngine
from backend.opensky_client import OpenSkyClient

class AutonomousOrchestrator:
    """
    Autonomous Background Worker for Real-Time Flight & Weather Telemetry.
    Streams live flights (via OpenSky ADS-B API or High-Density Synthetic Generator),
    updates airport meteorological conditions, triggers AI delay predictions,
    and stores results in DuckDB.
    """
    _instance = None
    _lock = threading.Lock()

    MODE_OPENSKY = "opensky"
    MODE_SYNTHETIC = "synthetic"

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(AutonomousOrchestrator, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.db = DuckDBManager()
        self.generator = FlightWeatherStreamGenerator()
        self.ai = AirAssistantAIEngine()
        self.opensky = OpenSkyClient()
        
        self.mode = self.MODE_OPENSKY  # Default to live real-world ADS-B telemetry
        self.is_running = False
        self.thread = None
        self.batch_size = 30
        self.sleep_interval = 2.0  # seconds between cycles (respecting OpenSky rate limit)
        self.total_streamed = 0
        self.cycle_count = 0
        self.last_cycle_time = None
        self.last_cycle_latency_ms = 0.0
        self.opensky_error_count = 0
        
        self._initialized = True

    def set_data_mode(self, mode: str):
        """Switches between 'opensky' (live real API) and 'synthetic' (simulation)."""
        if mode in [self.MODE_OPENSKY, self.MODE_SYNTHETIC]:
            self.mode = mode
            if mode == self.MODE_OPENSKY:
                # Trigger an immediate ingestion batch of real flights
                self.ingest_live_opensky_snapshot(limit=300)

    def ingest_live_opensky_snapshot(self, limit: int = 500):
        """Immediately fetches and loads live airborne flights into DuckDB."""
        try:
            weather_df = self.generator.get_weather_df()
            weather_lookup = {r['airport_code']: r.to_dict() for _, r in weather_df.iterrows()}
            real_batch = self.opensky.get_live_flights_dataframe(limit=limit, weather_lookup=weather_lookup)
            if not real_batch.empty:
                delays, sevs, causes, confs = self.ai.predict_flight_delays(real_batch)
                real_batch['predicted_delay_min'] = delays
                real_batch['delay_severity'] = sevs
                real_batch['primary_cause'] = causes
                real_batch['confidence_score'] = confs
                self.db.insert_flights_batch(real_batch)
                self.total_streamed += len(real_batch)
                return len(real_batch)
        except Exception as e:
            print(f"[AeroSentinel OpenSky Ingest Error]: {e}")
        return 0

    def seed_initial_if_needed(self):
        """Ensures database has an initial baseline of flights on startup."""
        metrics = self.db.get_summary_metrics()
        if metrics['total_records'] < 300:
            # Try fetching real OpenSky flights first
            ingested = self.ingest_live_opensky_snapshot(limit=600)
            if ingested < 100:
                # Fallback to high density synthetic if offline
                initial_flights = self.generator.generate_high_density_global_airspace(target_count=1200)
                delays, sevs, causes, confs = self.ai.predict_flight_delays(initial_flights)
                initial_flights['predicted_delay_min'] = delays
                initial_flights['delay_severity'] = sevs
                initial_flights['primary_cause'] = causes
                initial_flights['confidence_score'] = confs
                self.db.insert_flights_batch(initial_flights)
            self.db.update_airport_weather(self.generator.get_weather_df())

    def start(self):
        """Starts the autonomous background ingestion and scoring thread."""
        with self._lock:
            if self.is_running and self.thread and self.thread.is_alive():
                return
            self.seed_initial_if_needed()
            self.is_running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()

    def stop(self):
        """Pauses the worker."""
        with self._lock:
            self.is_running = False

    def trigger_hub_storm(self, hub: str = 'ORD', duration_steps: int = 20):
        """Triggers a simulated severe weather event at an airport hub."""
        self.generator.trigger_storm_shock(target_hub=hub, duration_steps=duration_steps)

    def _run_loop(self):
        """Main autonomous execution cycle."""
        self.seed_initial_if_needed()

        while self.is_running:
            t0 = time.time()
            try:
                # 1. Update weather table
                weather_df = self.generator.get_weather_df()
                self.db.update_airport_weather(weather_df)
                weather_lookup = {r['airport_code']: r.to_dict() for _, r in weather_df.iterrows()}

                stream_batch = pd.DataFrame()

                # 2. Ingest according to selected mode
                if self.mode == self.MODE_OPENSKY:
                    try:
                        stream_batch = self.opensky.get_live_flights_dataframe(
                            limit=self.batch_size, 
                            weather_lookup=weather_lookup
                        )
                    except Exception as e:
                        self.opensky_error_count += 1
                        print(f"[OpenSky Live Stream Warning]: {e}")

                # If OpenSky returned empty (rate-limit/network) or mode is synthetic, use generator
                if stream_batch.empty:
                    stream_batch = self.generator.generate_batch(count=self.batch_size)

                # 3. Run immediate AI delay predictions on inbound batch
                delays, sevs, causes, confs = self.ai.predict_flight_delays(stream_batch)
                stream_batch['predicted_delay_min'] = delays
                stream_batch['delay_severity'] = sevs
                stream_batch['primary_cause'] = causes
                stream_batch['confidence_score'] = confs
                
                self.db.insert_flights_batch(stream_batch)
                self.total_streamed += len(stream_batch)

                self.cycle_count += 1
                self.last_cycle_time = datetime.now()
                self.last_cycle_latency_ms = round((time.time() - t0) * 1000.0, 2)

            except Exception as e:
                print(f"[AeroSentinel Autonomous Worker Error]: {e}")

            time.sleep(self.sleep_interval)

    def get_status(self):
        """Returns worker status including OpenSky connection telemetry."""
        return {
            'is_running': self.is_running,
            'mode': self.mode,
            'total_streamed': self.total_streamed,
            'cycle_count': self.cycle_count,
            'last_cycle_time': self.last_cycle_time,
            'last_cycle_latency_ms': self.last_cycle_latency_ms,
            'batch_size': self.batch_size,
            'sleep_interval': self.sleep_interval,
            'storm_hub': self.generator.storm_shock_hub,
            'opensky_connected': self.opensky.is_connected,
            'opensky_last_count': self.opensky.last_flight_count,
            'opensky_status_msg': self.opensky.last_status_msg,
            'opensky_client_id': self.opensky.client_id
        }
