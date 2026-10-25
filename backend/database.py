import duckdb
import os
import threading
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "aero_engine.duckdb")

class DuckDBManager:
    """
    High-Performance DuckDB Manager for Real-Time Flight & Weather Telemetry.
    Fixes DuckDB connection configuration conflicts by sharing a persistent,
    thread-safe connection guarded with a threading.Lock.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DuckDBManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, db_path=DB_PATH):
        if self._initialized:
            return
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.lock = threading.Lock()
        
        # Single persistent master connection with read_write mode
        self.con = duckdb.connect(self.db_path, read_only=False)
        self._init_database()
        self._initialized = True

    def _init_database(self):
        """Initializes tables, sequences, and indexes."""
        with self.lock:
            self.con.execute("""
                CREATE SEQUENCE IF NOT EXISTS flight_seq START 1;

                CREATE TABLE IF NOT EXISTS flights_stream (
                    id BIGINT,
                    timestamp TIMESTAMP,
                    flight_id VARCHAR,
                    airline VARCHAR,
                    origin VARCHAR,
                    destination VARCHAR,
                    scheduled_dep_hour INTEGER,
                    distance_miles DOUBLE,
                    altitude_ft INTEGER,
                    speed_kts INTEGER,
                    status VARCHAR,
                    weather_condition VARCHAR,
                    wind_speed_kts DOUBLE,
                    visibility_miles DOUBLE,
                    precipitation_mm DOUBLE,
                    congestion_index DOUBLE,
                    predicted_delay_min DOUBLE DEFAULT 0.0,
                    delay_severity VARCHAR DEFAULT 'On-Time (0-15m)',
                    primary_cause VARCHAR DEFAULT 'Normal Flow',
                    confidence_score DOUBLE DEFAULT 0.95
                );

                CREATE TABLE IF NOT EXISTS airport_weather (
                    airport_code VARCHAR PRIMARY KEY,
                    airport_name VARCHAR,
                    region VARCHAR,
                    country VARCHAR,
                    weather_condition VARCHAR,
                    wind_speed_kts DOUBLE,
                    visibility_miles DOUBLE,
                    precipitation_mm DOUBLE,
                    congestion_index DOUBLE,
                    ground_stop_risk VARCHAR,
                    updated_at TIMESTAMP
                );
            """)

            # Ensure clean schema alignment for airport_weather
            cols = [r[0] for r in self.con.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'airport_weather'").fetchall()]
            if cols and (len(cols) != 11 or cols[1] != 'airport_name'):
                self.con.execute("DROP TABLE IF EXISTS airport_weather;")
                self.con.execute("""
                    CREATE TABLE airport_weather (
                        airport_code VARCHAR PRIMARY KEY,
                        airport_name VARCHAR,
                        region VARCHAR,
                        country VARCHAR,
                        weather_condition VARCHAR,
                        wind_speed_kts DOUBLE,
                        visibility_miles DOUBLE,
                        precipitation_mm DOUBLE,
                        congestion_index DOUBLE,
                        ground_stop_risk VARCHAR,
                        updated_at TIMESTAMP
                    );
                """)

    def insert_flights_batch(self, df: pd.DataFrame):
        """Vectorized insertion of a batch of real-time flight records."""
        if df.empty:
            return 0
        with self.lock:
            self.con.register("df_flight_batch", df)
            self.con.execute("""
                INSERT INTO flights_stream (
                    id, timestamp, flight_id, airline, origin, destination,
                    scheduled_dep_hour, distance_miles, altitude_ft, speed_kts,
                    status, weather_condition, wind_speed_kts, visibility_miles,
                    precipitation_mm, congestion_index, predicted_delay_min,
                    delay_severity, primary_cause, confidence_score
                )
                SELECT 
                    nextval('flight_seq'),
                    timestamp, flight_id, airline, origin, destination,
                    scheduled_dep_hour, distance_miles, altitude_ft, speed_kts,
                    status, weather_condition, wind_speed_kts, visibility_miles,
                    precipitation_mm, congestion_index, predicted_delay_min,
                    delay_severity, primary_cause, confidence_score
                FROM df_flight_batch
            """)
            self.con.unregister("df_flight_batch")
            return len(df)

    def update_airport_weather(self, weather_df: pd.DataFrame):
        """Updates real-time airport ground conditions and congestion indices."""
        if weather_df.empty:
            return
        with self.lock:
            self.con.register("w_batch", weather_df)
            self.con.execute("""
                INSERT OR REPLACE INTO airport_weather (
                    airport_code, airport_name, region, country,
                    weather_condition, wind_speed_kts, visibility_miles,
                    precipitation_mm, congestion_index, ground_stop_risk, updated_at
                )
                SELECT 
                    airport_code, airport_name, region, country,
                    weather_condition, wind_speed_kts, visibility_miles,
                    precipitation_mm, congestion_index, ground_stop_risk, updated_at
                FROM w_batch
            """)
            self.con.unregister("w_batch")

    def update_ai_predictions(self, ids: list, delays: list, severities: list, causes: list, confidences: list):
        """Updates AI delay predictions back into DuckDB."""
        if not ids:
            return
        update_df = pd.DataFrame({
            'id': ids,
            'predicted_delay_min': delays,
            'delay_severity': severities,
            'primary_cause': causes,
            'confidence_score': confidences
        })
        with self.lock:
            self.con.register("update_ai_df", update_df)
            self.con.execute("""
                UPDATE flights_stream
                SET 
                    predicted_delay_min = update_ai_df.predicted_delay_min,
                    delay_severity = update_ai_df.delay_severity,
                    primary_cause = update_ai_df.primary_cause,
                    confidence_score = update_ai_df.confidence_score
                FROM update_ai_df
                WHERE flights_stream.id = update_ai_df.id
            """)
            self.con.unregister("update_ai_df")

    def get_summary_metrics(self):
        """Fetches executive real-time flight KPIs in a single instant query."""
        with self.lock:
            res = self.con.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    COALESCE(COUNT(DISTINCT flight_id), 0) as active_flights,
                    COALESCE(AVG(predicted_delay_min), 0.0) as avg_predicted_delay,
                    COALESCE(SUM(CASE WHEN predicted_delay_min <= 15.0 THEN 1 ELSE 0 END)::FLOAT / NULLIF(COUNT(*), 0) * 100.0, 100.0) as on_time_rate,
                    COALESCE(SUM(CASE WHEN predicted_delay_min > 45.0 THEN 1 ELSE 0 END), 0) as severe_delays_count,
                    COALESCE(MAX(predicted_delay_min), 0.0) as max_delay,
                    COALESCE(AVG(wind_speed_kts), 0.0) as mean_fleet_wind,
                    COALESCE(AVG(congestion_index), 0.0) as mean_fleet_congestion
                FROM flights_stream
            """).fetchdf()
        return res.iloc[0].to_dict()

    def get_recent_flights(self, limit: int = 150):
        """Fetches latest flight stream records for real-time monitoring."""
        with self.lock:
            df = self.con.execute(f"""
                SELECT * 
                FROM flights_stream 
                ORDER BY timestamp DESC, id DESC 
                LIMIT {limit}
            """).fetchdf()
        return df

    def get_unscored_flights(self, limit: int = 300):
        """Fetches records pending AI delay inference."""
        with self.lock:
            df = self.con.execute(f"""
                SELECT id, flight_id, airline, origin, destination, scheduled_dep_hour,
                       distance_miles, altitude_ft, speed_kts, status, weather_condition,
                       wind_speed_kts, visibility_miles, precipitation_mm, congestion_index
                FROM flights_stream
                WHERE predicted_delay_min = 0.0 AND delay_severity = 'On-Time (0-15m)' AND primary_cause = 'Normal Flow'
                ORDER BY id DESC
                LIMIT {limit}
            """).fetchdf()
        return df

    def get_airport_weather_table(self):
        """Fetches latest weather and risk status across major airport hubs."""
        with self.lock:
            df = self.con.execute("""
                SELECT * FROM airport_weather ORDER BY congestion_index DESC
            """).fetchdf()
        return df

    def get_airline_performance(self):
        """Aggregates delay statistics by airline."""
        with self.lock:
            df = self.con.execute("""
                SELECT 
                    airline,
                    COUNT(*) as flight_count,
                    ROUND(AVG(predicted_delay_min), 1) as avg_delay_min,
                    ROUND(SUM(CASE WHEN predicted_delay_min <= 15.0 THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100.0, 1) as on_time_pct,
                    ROUND(SUM(CASE WHEN predicted_delay_min > 45.0 THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100.0, 1) as severe_delay_pct
                FROM flights_stream
                GROUP BY airline
                ORDER BY avg_delay_min ASC
            """).fetchdf()
        return df

    def get_route_delay_hotspots(self, limit: int = 8):
        """Finds top routes most affected by weather/congestion delays."""
        with self.lock:
            df = self.con.execute(f"""
                SELECT 
                    origin || ' ➔ ' || destination as route,
                    COUNT(*) as total_flights,
                    ROUND(AVG(predicted_delay_min), 1) as mean_delay_min,
                    ROUND(AVG(wind_speed_kts), 1) as avg_wind,
                    ROUND(AVG(congestion_index), 1) as avg_congestion,
                    MODE(primary_cause) as predominant_cause
                FROM flights_stream
                GROUP BY route
                HAVING total_flights >= 3
                ORDER BY mean_delay_min DESC
                LIMIT {limit}
            """).fetchdf()
        return df

    def get_timeseries_delay_trend(self, bucket_seconds: int = 5, limit: int = 30):
        """Aggregates flight delays over time buckets for live charting."""
        with self.lock:
            df = self.con.execute(f"""
                SELECT 
                    time_bucket(INTERVAL '{bucket_seconds} seconds', timestamp) as time_bucket,
                    COUNT(*) as flights_count,
                    AVG(predicted_delay_min) as mean_delay,
                    AVG(congestion_index) as mean_congestion,
                    AVG(wind_speed_kts) as mean_wind
                FROM flights_stream
                GROUP BY time_bucket
                ORDER BY time_bucket DESC
                LIMIT {limit}
            """).fetchdf()
        return df.sort_values(by="time_bucket", ascending=True).reset_index(drop=True)

    def generate_big_data_flight_archive(self, num_records: int = 250000):
        """
        Synthesizes huge historical flight logs inside DuckDB in under 1 second.
        Demonstrates DuckDB's in-process big data capabilities.
        """
        with self.lock:
            start_time = datetime.now()
            self.con.execute(f"""
                INSERT INTO flights_stream (
                    id, timestamp, flight_id, airline, origin, destination,
                    scheduled_dep_hour, distance_miles, altitude_ft, speed_kts,
                    status, weather_condition, wind_speed_kts, visibility_miles,
                    precipitation_mm, congestion_index, predicted_delay_min,
                    delay_severity, primary_cause, confidence_score
                )
                SELECT 
                    nextval('flight_seq') AS id,
                    NOW() - (INTERVAL '1 second' * (row_number() OVER ()) * 0.2) AS timestamp,
                    'FL-' || ((random() * 8999)::INT + 1000)::VARCHAR AS flight_id,
                    CASE (random() * 5)::INT
                        WHEN 0 THEN 'Delta'
                        WHEN 1 THEN 'American'
                        WHEN 2 THEN 'United'
                        WHEN 3 THEN 'Southwest'
                        WHEN 4 THEN 'British Airways'
                        ELSE 'Lufthansa'
                    END AS airline,
                    CASE (random() * 7)::INT
                        WHEN 0 THEN 'JFK'
                        WHEN 1 THEN 'ORD'
                        WHEN 2 THEN 'ATL'
                        WHEN 3 THEN 'LAX'
                        WHEN 4 THEN 'DFW'
                        WHEN 5 THEN 'LHR'
                        WHEN 6 THEN 'SFO'
                        ELSE 'DEN'
                    END AS origin,
                    CASE (random() * 7)::INT
                        WHEN 0 THEN 'MIA'
                        WHEN 1 THEN 'SEA'
                        WHEN 2 THEN 'BOS'
                        WHEN 3 THEN 'CDG'
                        WHEN 4 THEN 'LAS'
                        WHEN 5 THEN 'MCO'
                        WHEN 6 THEN 'HND'
                        ELSE 'PHX'
                    END AS destination,
                    (random() * 23)::INT AS scheduled_dep_hour,
                    ROUND(300.0 + random() * 3200.0, 1) AS distance_miles,
                    ((random() * 15000)::INT + 24000) AS altitude_ft,
                    ((random() * 120)::INT + 420) AS speed_kts,
                    'Airborne' AS status,
                    CASE (random() * 6)::INT
                        WHEN 0 THEN 'Clear'
                        WHEN 1 THEN 'Cloudy'
                        WHEN 2 THEN 'Rain'
                        WHEN 3 THEN 'Thunderstorm'
                        WHEN 4 THEN 'High Winds'
                        WHEN 5 THEN 'Fog'
                        ELSE 'Snow/Blizzard'
                    END AS weather_condition,
                    ROUND(5.0 + random() * 45.0, 1) AS wind_speed_kts,
                    ROUND(1.0 + random() * 9.0, 1) AS visibility_miles,
                    ROUND(random() * 25.0, 1) AS precipitation_mm,
                    ROUND(10.0 + random() * 85.0, 1) AS congestion_index,
                    ROUND(GREATEST(0.0, random() * 35.0 + (CASE WHEN random() > 0.85 THEN 65.0 ELSE 0.0 END)), 1) AS predicted_delay_min,
                    'Moderate (15-45m)' AS delay_severity,
                    'Weather & Airspace Flow' AS primary_cause,
                    0.94 AS confidence_score
                FROM range({num_records})
            """)
            duration = (datetime.now() - start_time).total_seconds()
        return num_records, duration

    def execute_custom_sql(self, sql_query: str):
        """Executes arbitrary SQL queries with millisecond execution timing."""
        start_time = datetime.now()
        with self.lock:
            try:
                df = self.con.execute(sql_query).fetchdf()
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000.0
                error = None
            except Exception as e:
                df = pd.DataFrame()
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000.0
                error = str(e)
        return df, duration_ms, error

    def clear_database(self):
        """Cleans all flight tables for a fresh run."""
        with self.lock:
            self.con.execute("TRUNCATE TABLE flights_stream;")
            self.con.execute("ALTER SEQUENCE flight_seq RESTART WITH 1;")
