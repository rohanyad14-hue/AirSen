import os
import sys

# Ensure workspace root is in python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import pandas as pd
import streamlit as st
from backend.database import DuckDBManager
from backend.autonomous_worker import AutonomousOrchestrator
from backend.stream_generator import GLOBAL_AIRPORTS
from frontend.styles import get_custom_css
from frontend.components import (
    render_kpi_cards,
    render_air_assistant,
    render_flight_world_map,
    render_flight_radar_table,
    render_delay_analytics_charts,
    render_airport_weather_matrix,
    render_duckdb_sandbox
)

# Singleton Database & Autonomous Worker Initialization
@st.cache_resource
def get_backend():
    db = DuckDBManager()
    worker = AutonomousOrchestrator()
    worker.start()  # Autonomously stream & score flights on boot
    return db, worker

def main():
    # 1. Page Configuration
    st.set_page_config(
        page_title="AeroSentinel // Global Air Assistant AI & Flight Radar",
        page_icon="✈️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 2. Inject Custom CSS
    st.markdown(get_custom_css(), unsafe_allow_html=True)

    # 3. Singleton Database & Autonomous Worker Initialization
    db_manager, orchestrator = get_backend()

    # 4. Sidebar Controls & Meteorological Simulator
    with st.sidebar:
        st.markdown("### 🎛 Flight Radar Controls")
        
        status = orchestrator.get_status()
        is_active = status['is_running']
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if is_active:
                if st.button("⏸ Pause Feed", use_container_width=True, key="sb_pause_btn"):
                    orchestrator.stop()
                    st.rerun()
            else:
                if st.button("▶ Resume Feed", use_container_width=True, type="primary", key="sb_resume_btn"):
                    orchestrator.start()
                    st.rerun()
        
        with col_s2:
            if st.button("🔄 Instant Sync", use_container_width=True, type="secondary", key="sb_sync_btn"):
                st.rerun()

        st.markdown("---")
        st.markdown("#### 🛰️ Radar Data Stream")
        source_mode_options = [
            "🛰️ Live OpenSky API (Real-World ADS-B)",
            "📡 Synthetic Simulator (High-Density Airspace)"
        ]
        curr_mode_idx = 0 if status.get('mode') == 'opensky' else 1
        selected_source = st.selectbox(
            "Telemetry Stream Mode:",
            options=source_mode_options,
            index=curr_mode_idx,
            key="sb_data_source_mode"
        )
        target_mode = "opensky" if "OpenSky" in selected_source else "synthetic"
        if target_mode != status.get('mode'):
            orchestrator.set_data_mode(target_mode)
            st.rerun()

        if target_mode == "opensky":
            live_count = status.get('opensky_last_count', 0)
            client_id = status.get('opensky_client_id', 'vittestuser1-api-client')
            st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 8px; padding: 10px 12px; margin-bottom: 10px;">
                <div style="font-size: 11px; font-weight: 700; color: #10B981; letter-spacing: 0.5px;">🟢 OPENSKY NETWORK CONNECTED</div>
                <div style="font-size: 11px; color: #94A3B8; font-family: monospace; margin-top: 3px;">Client: <b>{client_id}</b></div>
                <div style="font-size: 11px; color: #38BDF8; font-family: monospace; margin-top: 2px;">Global Live Aircraft: <b>{live_count:,}</b></div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("📥 Pull Real OpenSky Fleet (400 Planes)", use_container_width=True, key="sb_pull_opensky_btn"):
                with st.spinner("Fetching live ADS-B telemetry from OpenSky Network..."):
                    added = orchestrator.ingest_live_opensky_snapshot(limit=400)
                    st.toast(f"Ingested {added} live airborne flights from OpenSky Network!", icon="🛰️")
                    st.rerun()

        st.markdown("---")
        st.markdown("#### ⚡ Flight Stream Volume")
        new_batch_size = st.slider(
            "Flights Ingested per Batch:",
            min_value=20,
            max_value=120,
            value=status['batch_size'],
            step=20,
            key="sb_batch_size_slider"
        )
        if new_batch_size != status['batch_size']:
            orchestrator.batch_size = new_batch_size

        st.markdown("---")
        st.markdown("#### ⛈ Extreme Weather Shock Injector")
        st.caption("Trigger a typhoon, blizzard, or convective thunderstorm at any international hub to watch real-time AI delay cascades.")
        
        hub_display_list = [f"{code} - {GLOBAL_AIRPORTS[code]['name']} ({GLOBAL_AIRPORTS[code]['country']})" for code in sorted(GLOBAL_AIRPORTS.keys())]
        default_hub_label = next((h for h in hub_display_list if h.startswith("ORD -")), hub_display_list[0])
        default_idx = hub_display_list.index(default_hub_label) if default_hub_label in hub_display_list else 0
        target_hub_choice = st.selectbox(
            "Target Airport Hub:",
            options=hub_display_list,
            index=default_idx,
            key="sb_shock_hub_select"
        )
        target_hub = target_hub_choice.split(" - ")[0]
        
        if st.button(f"⚡ Inject Storm Shock at {target_hub}", use_container_width=True, key="sb_shock_btn"):
            orchestrator.trigger_hub_storm(hub=target_hub, duration_steps=25)
            st.toast(f"⛈ Severe storm cell triggered at {target_hub}! Watch delay predictions spike.", icon="🚨")

        st.markdown("---")
        st.markdown("""
        <div style="font-size: 11px; color: #64748B; font-family: 'JetBrains Mono', monospace;">
            DATA FEED: OpenSky Network ADS-B OAuth2 API<br>
            COVERAGE: Global (Americas, EU, Asia, ME, Africa, Oceania)<br>
            FLEET DENSITY: Flightradar24 Scale (1,200+ Active Flights)<br>
            ENGINE: DuckDB In-Process Columnar OLAP<br>
            AI MODEL: HistGradientBoosting Trees (No LLM)<br>
            STATUS: 100% Deterministic & Private
        </div>
        """, unsafe_allow_html=True)

    # 5. Top Header Banner
    worker_status = orchestrator.get_status()
    pulse_html = """<span class="badge-live"><span class="badge-pulse"></span> GLOBAL RADAR ACTIVE</span>""" if worker_status['is_running'] else """<span class="badge-live" style="background: rgba(245, 158, 11, 0.15); color: #F59E0B; border-color: rgba(245, 158, 11, 0.3);">PAUSED</span>"""
    
    feed_badge = """<span style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #10B981; background: rgba(16, 185, 129, 0.12); padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(16, 185, 129, 0.3);">🛰️ OPENSKY LIVE API</span>""" if worker_status.get('mode') == 'opensky' else """<span style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #38BDF8; background: rgba(56, 189, 248, 0.12); padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(56, 189, 248, 0.3);">📡 SIMULATOR</span>"""

    st.markdown(f"""
    <div class="sentinel-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
            <div>
                <div class="sentinel-title">
                    ✈️ AEROSENTINEL // Global Air Assistant AI & Flight Radar
                </div>
                <p class="sentinel-subtitle">
                    Worldwide Commercial Flight Telemetry • Atmospheric Weather Overlays • Non-LLM Gradient Boosted Delay Forecasting • DuckDB Big Data OLAP
                </p>
            </div>
            <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                {feed_badge}
                {pulse_html}
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #94A3B8; background: rgba(15, 23, 42, 0.6); padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(255, 255, 255, 0.05);">
                    ⏱ {worker_status['last_cycle_latency_ms']} ms cycle
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Fetch latest telemetry data safely
    try:
        summary_metrics = db_manager.get_summary_metrics()
        recent_flights = db_manager.get_recent_flights(limit=1500)  # Flightradar24 scale!
        weather_df = db_manager.get_airport_weather_table()
        airline_df = db_manager.get_airline_performance()
        route_df = db_manager.get_route_delay_hotspots(limit=10)
    except Exception as e:
        st.error(f"Error querying telemetry database: {e}")
        summary_metrics = {}
        recent_flights = pd.DataFrame()
        weather_df = pd.DataFrame()
        airline_df = pd.DataFrame()
        route_df = pd.DataFrame()

    # 6. Executive Fleet KPI Banner
    render_kpi_cards(summary_metrics, worker_status)
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 7. Main Navigation Tabs (Completely stable, zero-flicker, zero-blanking)
    tab_map, tab_assistant, tab_radar, tab_weather, tab_duckdb = st.tabs([
        "🗺️ Global Flight Radar & Weather Map",
        "✈️ Air Assistant & Flight Inspector",
        "📡 Live Radar Feed & Analytics",
        "🌐 Worldwide Hubs Weather Matrix",
        "⚡ DuckDB Big Data Flight Sandbox"
    ])

    with tab_map:
        try:
            render_flight_world_map(recent_flights, weather_df)
        except Exception as e:
            st.error(f"Error rendering Global Flight Map: {e}")

    with tab_assistant:
        try:
            render_air_assistant(recent_flights, orchestrator.ai)
        except Exception as e:
            st.error(f"Error rendering Air Assistant: {e}")

    with tab_radar:
        try:
            render_flight_radar_table(recent_flights)
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            render_delay_analytics_charts(recent_flights, airline_df, route_df)
        except Exception as e:
            st.error(f"Error rendering Live Radar Feed: {e}")

    with tab_weather:
        try:
            render_airport_weather_matrix(weather_df)
        except Exception as e:
            st.error(f"Error rendering Weather Matrix: {e}")

    with tab_duckdb:
        try:
            render_duckdb_sandbox(db_manager)
        except Exception as e:
            st.error(f"Error rendering DuckDB Sandbox: {e}")

if __name__ == "__main__":
    main()
