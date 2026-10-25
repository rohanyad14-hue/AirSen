import streamlit as st
import pandas as pd

def render_airport_weather_matrix(weather_df: pd.DataFrame):
    """Renders real-time airport hub weather, surface winds, and ground-stop alert matrix."""
    st.markdown("### 🌐 Global Hub Atmospheric Conditions & Ground Stop Risk")
    st.caption("Live METAR observations and runway saturation across key commercial airspace sectors worldwide.")

    if weather_df.empty:
        st.info("Awaiting airport meteorological updates...")
        return

    # Filter by continent/region
    regions = ["All Continents"] + sorted(list(weather_df['region'].unique())) if 'region' in weather_df.columns else ["All Continents"]
    selected_region = st.selectbox("Filter Hubs by Region:", options=regions, index=0)

    display_df = weather_df.copy()
    if selected_region != "All Continents" and 'region' in display_df.columns:
        display_df = display_df[display_df['region'] == selected_region]

    display_df.rename(columns={
        'airport_code': 'IATA',
        'airport_name': 'Airport Hub',
        'region': 'Region',
        'country': 'Country',
        'weather_condition': 'Weather Condition',
        'wind_speed_kts': 'Winds (kts)',
        'visibility_miles': 'Visibility (mi)',
        'precipitation_mm': 'Precip (mm)',
        'congestion_index': 'Runway Queue (%)',
        'ground_stop_risk': 'Airspace Delay Risk'
    }, inplace=True)

    cols_to_show = [c for c in ['IATA', 'Airport Hub', 'Region', 'Country', 'Weather Condition', 'Winds (kts)', 'Visibility (mi)', 'Precip (mm)', 'Runway Queue (%)', 'Airspace Delay Risk'] if c in display_df.columns]
    
    st.dataframe(
        display_df[cols_to_show],
        use_container_width=True,
        hide_index=True
    )
