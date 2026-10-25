import streamlit as st
import pandas as pd
from backend.database import DuckDBManager

PRESET_FLIGHT_QUERIES = {
    "P90 & P99 Flight Delays by Airline": """
SELECT 
    airline, 
    COUNT(*) as total_flights, 
    ROUND(AVG(predicted_delay_min), 1) as avg_delay, 
    ROUND(QUANTILE_CONT(predicted_delay_min, 0.50), 1) as median_delay,
    ROUND(QUANTILE_CONT(predicted_delay_min, 0.90), 1) as p90_delay,
    ROUND(QUANTILE_CONT(predicted_delay_min, 0.99), 1) as p99_delay
FROM flights_stream 
GROUP BY airline 
ORDER BY avg_delay ASC;
""",
    "Weather Condition Delay Impact Analysis": """
SELECT 
    weather_condition, 
    COUNT(*) as flight_count, 
    ROUND(AVG(wind_speed_kts), 1) as avg_wind_kts,
    ROUND(AVG(precipitation_mm), 1) as avg_precip_mm,
    ROUND(AVG(predicted_delay_min), 1) as mean_delay_min,
    ROUND(MAX(predicted_delay_min), 1) as peak_delay_min
FROM flights_stream 
GROUP BY weather_condition 
ORDER BY mean_delay_min DESC;
""",
    "Worst Delayed Corridors (Origin ➔ Destination)": """
SELECT 
    origin || ' ➔ ' || destination as flight_corridor, 
    COUNT(*) as total_scheduled,
    ROUND(AVG(predicted_delay_min), 1) as avg_delay_min,
    ROUND(AVG(congestion_index), 1) as avg_congestion,
    ROUND(SUM(CASE WHEN predicted_delay_min > 45.0 THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100.0, 1) as severe_delay_pct
FROM flights_stream 
GROUP BY flight_corridor 
HAVING total_scheduled >= 2
ORDER BY avg_delay_min DESC
LIMIT 15;
""",
    "Peak Hour Airspace Saturation Breakdown": """
SELECT 
    scheduled_dep_hour as dep_hour_utc, 
    COUNT(*) as departures_count, 
    ROUND(AVG(predicted_delay_min), 1) as avg_delay,
    ROUND(AVG(congestion_index), 1) as avg_runway_congestion
FROM flights_stream 
GROUP BY dep_hour_utc 
ORDER BY dep_hour_utc ASC;
"""
}

def render_duckdb_sandbox(db_manager: DuckDBManager):
    """Renders the Big Data DuckDB benchmark tool and interactive SQL flight console."""
    st.markdown("### ⚡ DuckDB Big Data Engine & Flight OLAP")
    st.caption("DuckDB executes vectorized OLAP queries directly in-process across millions of flight logs in milliseconds.")

    # Section A: Big Data Benchmark Generator
    with st.expander("🚀 Big Data Flight Volume Stress Generator", expanded=False):
        st.markdown("Synthesize 250,000 to 1,000,000 flight telemetry logs in DuckDB to test analytical query speeds.")
        bcol1, bcol2, bcol3 = st.columns([2, 1, 1])
        
        with bcol1:
            records_choice = st.select_slider(
                "Number of Synthetic Flight Records to Ingest:",
                options=[100000, 250000, 500000, 1000000],
                value=250000,
                format_func=lambda x: f"{x:,} flight logs"
            )
        with bcol2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Generate Big Data", use_container_width=True, type="primary"):
                with st.spinner(f"Vectorizing {records_choice:,} flight logs in DuckDB..."):
                    count, duration = db_manager.generate_big_data_flight_archive(records_choice)
                    rate = count / duration if duration > 0 else 0
                    st.success(f"Ingested {count:,} flight logs in {duration:.2f}s ({rate:,.0f} rows/sec)!")
                    st.rerun()

        with bcol3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Truncate Flight Table", use_container_width=True):
                db_manager.clear_database()
                st.warning("Flight tables reset.")
                st.rerun()

    # Section B: Interactive SQL Query Console
    selected_preset = st.selectbox(
        "Load Flight Query Preset:",
        options=list(PRESET_FLIGHT_QUERIES.keys()),
        index=0
    )

    query_input = st.text_area(
        "SQL Query (DuckDB dialect):",
        value=PRESET_FLIGHT_QUERIES[selected_preset].strip(),
        height=140
    )

    rcol1, rcol2 = st.columns([1, 4])
    with rcol1:
        run_pressed = st.button("▶ Run SQL Query", type="primary", use_container_width=True)

    if run_pressed or query_input:
        df_result, duration_ms, error = db_manager.execute_custom_sql(query_input)
        
        if error:
            st.error(f"SQL Execution Error: {error}")
        else:
            with rcol2:
                st.markdown(f"""
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #00E676; padding-top: 8px;">
                    ⚡ Executed in <b>{duration_ms:.2f} ms</b> • Returned <b>{len(df_result):,} rows</b>
                </div>
                """, unsafe_allow_html=True)
            
            st.dataframe(df_result, use_container_width=True, height=260)
