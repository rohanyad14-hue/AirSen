import streamlit as st
import pandas as pd
from backend.ai_engine import AirAssistantAIEngine

def render_air_assistant(recent_flights: pd.DataFrame, ai_engine: AirAssistantAIEngine):
    """
    Renders the dedicated Air Assistant AI panel.
    Allows inspecting any active flight to get an immediate prediction of how late it will be,
    along with root-cause meteorological breakdowns and prescriptive advice.
    """
    st.markdown("### ✈️ Air Assistant AI // Flight Delay Inspector")
    st.caption("Select an active commercial flight or adjust atmospheric variables to predict arrival delay in real time.")

    if recent_flights.empty:
        st.info("Awaiting live flight telemetry stream...")
        return

    # Pre-formatted flight labels to eliminate format_func serialization crashes
    # Note: Do NOT put volatile dynamic metrics (like changing delay numbers) into the dropdown option string,
    # as that causes option list mismatches and ValueError on reruns.
    display_options = []
    flight_dict = {}
    for _, r in recent_flights.head(100).iterrows():
        fid = r['flight_id']
        label = f"{fid} | {r['airline']} | {r['origin']} ➔ {r['destination']}"
        if label not in flight_dict:
            display_options.append(label)
            flight_dict[label] = r.to_dict()

    # Ensure any previously selected flight remains in options to prevent Streamlit widget index mismatch
    prev_sel = st.session_state.get("assistant_flight_picker_stable")
    if prev_sel and prev_sel not in display_options:
        display_options.insert(0, prev_sel)

    if not display_options:
        st.info("Awaiting live flight telemetry stream...")
        return

    selected_label = st.selectbox(
        "Select Flight to Inspect:",
        options=display_options,
        index=0,
        key="assistant_flight_picker_stable"
    )

    flight_row = flight_dict.get(selected_label, recent_flights.iloc[0].to_dict())

    # Generate AI explanation
    explanation = ai_engine.explain_single_flight(flight_row)
    pred_delay = explanation['predicted_delay']

    # Color theme based on delay
    if pred_delay <= 15:
        badge_style = "background: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.4);"
        delay_color = "#10B981"
        status_label = "ON-TIME / SCHEDULED"
    elif pred_delay <= 45:
        badge_style = "background: rgba(245, 158, 11, 0.15); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.4);"
        delay_color = "#F59E0B"
        status_label = "MODERATE DELAY EXPECTED"
    else:
        badge_style = "background: rgba(239, 68, 68, 0.15); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.4);"
        delay_color = "#EF4444"
        status_label = "SEVERE AIRSPACE HAZARD"

    col_diag1, col_diag2 = st.columns([3, 2])

    with col_diag1:
        html_card = (
            f'<div class="insight-card">'
            f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">'
            f'<span class="insight-badge" style="{badge_style}">{status_label}</span>'
            f'<span style="font-family: \'JetBrains Mono\', monospace; font-size: 13px; color: #94A3B8;">'
            f'AI CONFIDENCE: {explanation["confidence"] * 100:.0f}%'
            f'</span>'
            f'</div>'
            f'<div style="display: flex; align-items: baseline; gap: 12px; margin: 12px 0;">'
            f'<span style="font-size: 38px; font-weight: 800; color: {delay_color};">+{pred_delay:.0f} MIN</span>'
            f'<span style="font-size: 15px; color: #94A3B8;">estimated late arrival at <b>{flight_row["destination"]}</b></span>'
            f'</div>'
            f'<p style="font-size: 14px; line-height: 1.6; color: #E2E8F0; margin: 8px 0 14px 0;">{explanation["verdict"]}</p>'
            f'<div class="action-pill" style="border-left-color: {delay_color}; margin-top: 10px;">'
            f'<b>Air Assistant Advisory:</b> {explanation["recommendation"]}'
            f'</div>'
            f'</div>'
        )
        st.markdown(html_card, unsafe_allow_html=True)

    with col_diag2:
        st.markdown("#### 🌦 Destination Weather Telemetry")
        wcol1, wcol2 = st.columns(2)
        with wcol1:
            st.metric("Weather Condition", flight_row['weather_condition'])
            st.metric("Crosswinds", f"{flight_row['wind_speed_kts']:.1f} kts")
        with wcol2:
            st.metric("Surface Visibility", f"{flight_row['visibility_miles']:.1f} mi")
            st.metric("Runway Congestion", f"{flight_row['congestion_index']:.0f}%")

    # Interactive Scenario Simulator for this flight
    with st.expander("🧪 What-If Weather Simulator for this Aircraft", expanded=False):
        st.caption("Simulate how sudden weather or congestion shifts would change this aircraft's arrival delay.")
        sim_col1, sim_col2, sim_col3 = st.columns(3)
        with sim_col1:
            sim_wind = st.slider("Simulated Wind Speed (kts):", 0.0, 60.0, float(flight_row['wind_speed_kts']), 2.0, key="sim_wind_slider")
        with sim_col2:
            sim_cong = st.slider("Simulated Runway Congestion (%):", 0.0, 100.0, float(flight_row['congestion_index']), 5.0, key="sim_cong_slider")
        with sim_col3:
            sim_weather = st.selectbox("Simulated Condition:", ['Clear', 'Rain', 'High Winds', 'Thunderstorm', 'Snow/Blizzard'], index=0, key="sim_weather_select")

        # Run quick what-if inference
        sim_df = pd.DataFrame([{
            'distance_miles': flight_row['distance_miles'],
            'scheduled_dep_hour': flight_row['scheduled_dep_hour'],
            'wind_speed_kts': sim_wind,
            'visibility_miles': 2.0 if sim_weather in ['Thunderstorm', 'Snow/Blizzard'] else 9.0,
            'precipitation_mm': 20.0 if sim_weather in ['Thunderstorm', 'Snow/Blizzard'] else 0.0,
            'congestion_index': sim_cong,
            'weather_condition': sim_weather,
            'airline': flight_row['airline']
        }])
        sim_delay, _, _, _ = ai_engine.predict_flight_delays(sim_df)
        sim_html = (
            f'<div style="font-family: \'JetBrains Mono\', monospace; font-size: 14px; color: #00E5FF; padding: 10px; background: rgba(15, 23, 42, 0.6); border-radius: 8px;">'
            f'⚡ Simulated AI Output: Under {sim_weather} with {sim_wind:.0f} kts wind and {sim_cong:.0f}% congestion, expected delay is <b>+{sim_delay[0]:.0f} minutes</b>.'
            f'</div>'
        )
        st.markdown(sim_html, unsafe_allow_html=True)
