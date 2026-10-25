import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import hashlib
from backend.stream_generator import GLOBAL_AIRPORTS

# Atmospheric Weather Pattern Definitions for Map Overlays
JET_STREAM_CORRIDORS = [
    # North Atlantic Polar Jet Stream
    {'name': 'North Atlantic Polar Jet (145 kts)', 'lons': [-85, -65, -45, -25, -10, 5, 20], 'lats': [45, 49, 53, 55, 52, 50, 48], 'wind': 145},
    # North Pacific Jet Stream
    {'name': 'North Pacific Jet Stream (150 kts)', 'lons': [120, 140, 160, 180, -160, -140, -125], 'lats': [32, 36, 40, 42, 43, 39, 36], 'wind': 150},
    # Eurasian Subtropical Jet
    {'name': 'Eurasian Subtropical Jet (125 kts)', 'lons': [25, 45, 65, 85, 105, 125], 'lats': [32, 33, 31, 29, 30, 32], 'wind': 125},
    # Southern Polar Jet Stream
    {'name': 'Southern Polar Jet (155 kts)', 'lons': [-140, -100, -60, -20, 20, 60, 100, 140, 180], 'lats': [-48, -52, -50, -47, -50, -53, -49, -46, -48], 'wind': 155}
]

STORM_RADAR_CELLS = [
    {'name': 'North Atlantic Low Pressure Storm System', 'lons': [-48, -40, -32, -26, -35, -48], 'lats': [50, 56, 58, 52, 47, 50], 'dbz': 52, 'severity': 'Extreme'},
    {'name': 'Midwest / Gulf Convective Squall Line', 'lons': [-96, -88, -82, -84, -92, -96], 'lats': [29, 34, 40, 37, 30, 29], 'dbz': 56, 'severity': 'Severe'},
    {'name': 'East Asian Monsoon Front / Convective Band', 'lons': [118, 126, 134, 132, 122, 118], 'lats': [20, 24, 30, 33, 27, 20], 'dbz': 50, 'severity': 'Severe'},
    {'name': 'Equatorial ITCZ Thunderstorm Belt', 'lons': [-40, -20, 0, 20, 40, 40, 20, 0, -20, -40], 'lats': [-2, 1, 3, 2, 0, 5, 8, 7, 5, 3], 'dbz': 48, 'severity': 'Moderate'},
    {'name': 'Alpine / Central European Squall Line', 'lons': [6, 12, 16, 14, 8, 6], 'lats': [44, 46, 49, 51, 48, 44], 'dbz': 45, 'severity': 'Moderate'}
]

TURBULENCE_ZONES = [
    {'name': 'Rocky Mountain Wave Turbulence (CAT)', 'lons': [-116, -105, -104, -115, -116], 'lats': [36, 38, 48, 47, 36], 'level': 'Severe CAT'},
    {'name': 'North Atlantic High-Shear Boundary', 'lons': [-55, -25, -22, -52, -55], 'lats': [54, 57, 52, 49, 54], 'level': 'Moderate-Severe'},
    {'name': 'Himalayan Orographic Turbulence Zone', 'lons': [78, 92, 94, 80, 78], 'lats': [27, 29, 34, 33, 27], 'level': 'Severe Mountain Wave'}
]

FOG_RESTRICTIONS = [
    {'name': 'San Francisco Coastal Marine Layer', 'lons': [-123.5, -121.5, -121.8, -123.8, -123.5], 'lats': [36.8, 37.2, 38.5, 38.1, 36.8]},
    {'name': 'English Channel / North Sea Advection Fog', 'lons': [-2.0, 4.0, 4.5, -1.5, -2.0], 'lats': [49.5, 51.5, 53.0, 51.0, 49.5]},
    {'name': 'Persian Gulf Radiation Fog Belt', 'lons': [49.0, 56.0, 56.5, 49.5, 49.0], 'lats': [24.5, 25.5, 27.0, 26.0, 24.5]}
]

def get_flight_position(flight_id: str, orig: str, dest: str, status: str):
    """Calculates deterministic en-route coordinates for an active flight."""
    c_orig = GLOBAL_AIRPORTS.get(orig, {'lat': 25.0, 'lon': 55.0})
    c_dest = GLOBAL_AIRPORTS.get(dest, {'lat': 51.5, 'lon': -0.4})

    h = int(hashlib.md5(flight_id.encode()).hexdigest(), 16)
    
    if status == 'Airborne':
        progress = 0.12 + ((h % 76) / 100.0)
    elif status == 'Approaching':
        progress = 0.88 + ((h % 10) / 100.0)
    elif status == 'Taxiing':
        progress = 0.05
    else:  # Scheduled
        progress = 0.01

    lat = c_orig['lat'] + progress * (c_dest['lat'] - c_orig['lat'])
    lon = c_orig['lon'] + progress * (c_dest['lon'] - c_orig['lon'])
    return lat, lon

def render_flight_world_map(recent_flights: pd.DataFrame, weather_df: pd.DataFrame):
    """
    Renders the Flightradar24-scale Global Radar Map with active aircraft,
    selectable atmospheric weather patterns, and origin/destination filters.
    """
    st.markdown("### 🗺️ Global Flight Radar & Meteorological Threat Map")
    st.caption("Live geographical visualization of worldwide air traffic with selectable atmospheric weather overlays and route filters.")

    if recent_flights.empty:
        st.info("Awaiting flight telemetry stream to populate world map...")
        return

    # Available airport choices for dropdowns
    available_origins = ["All Origins"] + sorted(list(recent_flights['origin'].unique()))
    available_dests = ["All Destinations"] + sorted(list(recent_flights['destination'].unique()))
    available_airlines = ["All Airlines"] + sorted(list(recent_flights['airline'].unique()))

    # Helper function to format airport labels with city
    def format_airport_label(code: str) -> str:
        if code in ["All Origins", "All Destinations"]:
            return code
        meta = GLOBAL_AIRPORTS.get(code, {})
        return f"{code} - {meta.get('name', code)} ({meta.get('country', '')})"

    # 1. Primary Filter Bar: Location, Destination, Airline & Delay
    f_row1_c1, f_row1_c2, f_row1_c3, f_row1_c4 = st.columns(4)

    with f_row1_c1:
        origin_choice = st.selectbox(
            "🛫 Origin Airport:",
            options=available_origins,
            index=0,
            format_func=format_airport_label,
            key="map_filter_origin"
        )

    with f_row1_c2:
        dest_choice = st.selectbox(
            "🛬 Destination Airport:",
            options=available_dests,
            index=0,
            format_func=format_airport_label,
            key="map_filter_destination"
        )

    with f_row1_c3:
        airline_choice = st.selectbox(
            "✈️ Airline / Carrier:",
            options=available_airlines,
            index=0,
            key="map_filter_airline"
        )

    with f_row1_c4:
        delay_choice = st.selectbox(
            "⏱️ Delay Status:",
            options=["All Flights", "On-Time (≤15m)", "Moderate Delay (15-45m)", "Severe Delay (>45m)"],
            index=0,
            key="map_filter_delay"
        )

    # 2. Secondary Filter Bar: Weather Overlays, Continent & Projection
    f_row2_c1, f_row2_c2, f_row2_c3, f_row2_c4 = st.columns(4)

    with f_row2_c1:
        weather_overlay = st.selectbox(
            "🌦️ Selectable Weather Overlay:",
            options=[
                "None (Clean Radar)",
                "🌀 Global Jet Streams (High-Altitude Winds)",
                "⛈ Convective Storm Radar (Doppler dBZ)",
                "⚠️ Clear-Air Turbulence (CAT) & Icing Zones",
                "🌫️ Low Visibility & Marine Fog Layers"
            ],
            index=1,
            key="map_weather_pattern_select"
        )

    with f_row2_c2:
        continent_choice = st.selectbox(
            "🌍 Airspace Sector / Region:",
            options=["All Continents (Global)", "Asia & Middle East", "Europe", "North America", "South America", "Africa", "Oceania"],
            index=0,
            key="map_filter_continent"
        )

    with f_row2_c3:
        projection_choice = st.selectbox(
            "🌐 Map Projection:",
            options=["natural earth", "orthographic", "equirectangular", "mercator"],
            index=0,
            format_func=lambda x: f"Projection: {x.title()}",
            key="map_filter_projection"
        )

    with f_row2_c4:
        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
        t1, t2 = st.columns(2)
        with t1:
            show_flight_paths = st.checkbox("Show Flight Paths", value=True, key="map_chk_paths")
        with t2:
            show_weather_hubs = st.checkbox("Airport Threat Rings", value=True, key="map_chk_hubs")

    # 3. Apply Filters Safely
    filtered_df = recent_flights.copy()

    if origin_choice != "All Origins":
        filtered_df = filtered_df[filtered_df['origin'] == origin_choice]

    if dest_choice != "All Destinations":
        filtered_df = filtered_df[filtered_df['destination'] == dest_choice]

    if airline_choice != "All Airlines":
        filtered_df = filtered_df[filtered_df['airline'] == airline_choice]

    if delay_choice == "On-Time (≤15m)":
        filtered_df = filtered_df[filtered_df['predicted_delay_min'] <= 15.0]
    elif delay_choice == "Moderate Delay (15-45m)":
        filtered_df = filtered_df[(filtered_df['predicted_delay_min'] > 15.0) & (filtered_df['predicted_delay_min'] <= 45.0)]
    elif delay_choice == "Severe Delay (>45m)":
        filtered_df = filtered_df[filtered_df['predicted_delay_min'] > 45.0]

    if continent_choice != "All Continents (Global)":
        target_reg_list = ['Asia', 'Middle East'] if continent_choice == "Asia & Middle East" else [continent_choice]
        valid_airports = {code for code, meta in GLOBAL_AIRPORTS.items() if meta.get('region') in target_reg_list}
        filtered_df = filtered_df[
            filtered_df['origin'].isin(valid_airports) | filtered_df['destination'].isin(valid_airports)
        ]

    # Quick metrics header above map
    total_matching = len(filtered_df)
    st.markdown(f"""
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #38BDF8; margin-bottom: 6px;">
        📡 Active Radar Targets: <b>{total_matching:,} aircraft</b> plotted across global airways
    </div>
    """, unsafe_allow_html=True)

    if filtered_df.empty:
        st.warning("⚠️ No active flights match the exact combination of filters. Try selecting 'All Destinations' or 'All Airlines'.")

    # 4. Construct Plotly Map with Selected Weather Overlays
    fig = go.Figure()

    # --- WEATHER OVERLAYS LAYER (Selectable by User) ---
    if "Jet Streams" in weather_overlay:
        for jet in JET_STREAM_CORRIDORS:
            fig.add_trace(go.Scattergeo(
                lon=jet['lons'],
                lat=jet['lats'],
                mode='lines+markers',
                line=dict(width=4.5, color='rgba(0, 229, 255, 0.65)'),
                marker=dict(size=6, symbol='arrow', color='#00E5FF'),
                hoverinfo='text',
                hovertext=f"<b>{jet['name']}</b><br>Core Velocity: {jet['wind']} knots<br>Altitude: FL340 - FL380",
                name='Jet Stream Wind Core',
                showlegend=True
            ))

    elif "Storm Radar" in weather_overlay:
        for storm in STORM_RADAR_CELLS:
            fig.add_trace(go.Scattergeo(
                lon=storm['lons'],
                lat=storm['lats'],
                mode='lines',
                fill='toself',
                fillcolor='rgba(239, 68, 68, 0.35)',
                line=dict(width=1.8, color='#EF4444'),
                hoverinfo='text',
                hovertext=f"<b>⛈ {storm['name']}</b><br>Radar Reflectivity: {storm['dbz']} dBZ<br>Severity: {storm['severity']} Convection",
                name='Severe Storm Cell',
                showlegend=True
            ))

    elif "Turbulence" in weather_overlay:
        for turb in TURBULENCE_ZONES:
            fig.add_trace(go.Scattergeo(
                lon=turb['lons'],
                lat=turb['lats'],
                mode='lines',
                fill='toself',
                fillcolor='rgba(245, 158, 11, 0.30)',
                line=dict(width=1.8, color='#F59E0B', dash='dash'),
                hoverinfo='text',
                hovertext=f"<b>⚠️ {turb['name']}</b><br>Hazard Level: {turb['level']}<br>Altitude: FL280 - FL410",
                name='Turbulence SIGMET',
                showlegend=True
            ))

    elif "Low Visibility" in weather_overlay:
        for fog in FOG_RESTRICTIONS:
            fig.add_trace(go.Scattergeo(
                lon=fog['lons'],
                lat=fog['lats'],
                mode='lines',
                fill='toself',
                fillcolor='rgba(148, 163, 184, 0.35)',
                line=dict(width=1.5, color='#94A3B8'),
                hoverinfo='text',
                hovertext=f"<b>🌫️ {fog['name']}</b><br>Surface Visibility: &lt; 0.8 miles<br>ILS CAT III Procedures Active",
                name='Low Visibility Zone',
                showlegend=True
            ))

    # --- LAYER A: Flight Path Lines (Great-Circle Arcs) ---
    if show_flight_paths and not filtered_df.empty:
        # Cap path lines at 100 to ensure crisp rendering performance
        for _, row in filtered_df.head(100).iterrows():
            c_orig = GLOBAL_AIRPORTS.get(row['origin'])
            c_dest = GLOBAL_AIRPORTS.get(row['destination'])
            if c_orig and c_dest:
                delay = row['predicted_delay_min']
                line_color = 'rgba(16, 185, 129, 0.22)' if delay <= 15 else (
                    'rgba(245, 158, 11, 0.35)' if delay <= 45 else 'rgba(239, 68, 68, 0.50)'
                )
                fig.add_trace(go.Scattergeo(
                    lon=[c_orig['lon'], c_dest['lon']],
                    lat=[c_orig['lat'], c_dest['lat']],
                    mode='lines',
                    line=dict(width=1.0, color=line_color),
                    hoverinfo='none',
                    showlegend=False
                ))

    # --- LAYER B: Airport Hub Weather & Congestion Threat Zones ---
    if show_weather_hubs and not weather_df.empty:
        hub_lats, hub_lons, hub_texts, hub_sizes, hub_colors = [], [], [], [], []
        for _, w in weather_df.iterrows():
            code = w['airport_code']
            c = GLOBAL_AIRPORTS.get(code)
            if c:
                hub_lats.append(c['lat'])
                hub_lons.append(c['lon'])
                cond = w['weather_condition']
                wind = w['wind_speed_kts']
                cong = w['congestion_index']
                risk = w['ground_stop_risk']
                
                if 'SEVERE' in risk or cond in ['Thunderstorm', 'Snow/Blizzard']:
                    color = '#EF4444'
                elif 'MODERATE' in risk or wind > 25.0:
                    color = '#F59E0B'
                else:
                    color = '#38BDF8'

                hub_colors.append(color)
                hub_sizes.append(max(8, min(20, int(cong / 5.0))))
                hub_texts.append(
                    f"<b>HUB: {code} ({c['name']})</b><br>"
                    f"Country: {c['country']}<br>"
                    f"Weather: {cond}<br>"
                    f"Surface Wind: {wind:.1f} kts | Vis: {w['visibility_miles']:.1f} mi<br>"
                    f"Runway Queue Saturation: {cong:.0f}%<br>"
                    f"Airspace Risk: {risk}"
                )

        fig.add_trace(go.Scattergeo(
            lon=hub_lons,
            lat=hub_lats,
            mode='markers+text',
            text=weather_df['airport_code'],
            textposition="top center",
            textfont=dict(size=9, color="#94A3B8"),
            marker=dict(
                size=hub_sizes,
                color=hub_colors,
                symbol='circle-open',
                line=dict(width=1.8, color=hub_colors)
            ),
            hoverinfo='text',
            hovertext=hub_texts,
            name='Airport Weather Hubs'
        ))

    # --- LAYER C: Active Aircraft Radar Targets (Flightradar24 Density) ---
    if not filtered_df.empty:
        plane_lats, plane_lons, plane_texts, plane_colors = [], [], [], []
        
        for _, row in filtered_df.iterrows():
            lat, lon = get_flight_position(row['flight_id'], row['origin'], row['destination'], row['status'])
            plane_lats.append(lat)
            plane_lons.append(lon)
            
            delay = row['predicted_delay_min']
            p_color = '#10B981' if delay <= 15 else ('#F59E0B' if delay <= 45 else '#EF4444')
            plane_colors.append(p_color)

            orig_info = GLOBAL_AIRPORTS.get(row['origin'], {})
            dest_info = GLOBAL_AIRPORTS.get(row['destination'], {})

            plane_texts.append(
                f"<b>✈️ {row['flight_id']} // {row['airline']}</b><br>"
                f"Route: {row['origin']} ({orig_info.get('country', '')}) ➔ {row['destination']} ({dest_info.get('country', '')})<br>"
                f"Distance: {row['distance_miles']:,.0f} mi<br>"
                f"Status: {row['status']} | Alt: {row['altitude_ft']:,} ft | Spd: {row['speed_kts']} kts<br>"
                f"Dest Weather: {row['weather_condition']} ({row['wind_speed_kts']:.0f} kts wind)<br>"
                f"<b>Predicted Delay: +{delay:.0f} min ({row['delay_severity']})</b><br>"
                f"Primary Driver: {row['primary_cause']}"
            )

        fig.add_trace(go.Scattergeo(
            lon=plane_lons,
            lat=plane_lats,
            mode='markers',
            marker=dict(
                size=7,
                color=plane_colors,
                symbol='arrow',
                line=dict(width=0.4, color='#FFFFFF')
            ),
            hoverinfo='text',
            hovertext=plane_texts,
            name='Airborne Aircraft'
        ))

    # 5. Map Styling & Projection
    fig.update_geos(
        projection_type=projection_choice,
        showland=True,
        landcolor='#0F172A',
        showocean=True,
        oceancolor='#080C14',
        showcoastlines=True,
        coastlinecolor='#334155',
        showcountries=True,
        countrycolor='#1E293B',
        showlakes=True,
        lakecolor='#080C14',
        bgcolor='rgba(0,0,0,0)'
    )

    fig.update_layout(
        paper_bgcolor='rgba(15, 23, 42, 0.4)',
        plot_bgcolor='rgba(15, 23, 42, 0.4)',
        font=dict(family='Plus Jakarta Sans, sans-serif', color='#94A3B8'),
        margin=dict(l=0, r=0, t=10, b=0),
        height=560,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=11, color='#CBD5E1')
        )
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # 6. Status Legend
    leg1, leg2, leg3 = st.columns(3)
    with leg1:
        st.markdown("""
        <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #10B981; margin-right: 6px;"></span>
        <span style="font-size: 13px; color: #CBD5E1;"><b>On-Time Flights</b> (0 - 15 min delay)</span>
        """, unsafe_allow_html=True)
    with leg2:
        st.markdown("""
        <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #F59E0B; margin-right: 6px;"></span>
        <span style="font-size: 13px; color: #CBD5E1;"><b>Moderate Delay</b> (15 - 45 min delay)</span>
        """, unsafe_allow_html=True)
    with leg3:
        st.markdown("""
        <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #EF4444; margin-right: 6px;"></span>
        <span style="font-size: 13px; color: #CBD5E1;"><b>Severe Delay / Storm Risk</b> (&gt;45 min delay)</span>
        """, unsafe_allow_html=True)
