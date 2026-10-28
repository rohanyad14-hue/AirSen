import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

DARK_LAYOUT = dict(
    paper_bgcolor='rgba(15, 23, 42, 0.4)',
    plot_bgcolor='rgba(15, 23, 42, 0.4)',
    font=dict(family='Plus Jakarta Sans, sans-serif', color='#94A3B8', size=11),
    margin=dict(l=40, r=20, t=35, b=35),
    xaxis=dict(
        gridcolor='rgba(255, 255, 255, 0.05)',
        zerolinecolor='rgba(255, 255, 255, 0.05)',
        showline=False
    ),
    yaxis=dict(
        gridcolor='rgba(255, 255, 255, 0.05)',
        zerolinecolor='rgba(255, 255, 255, 0.05)',
        showline=False
    ),
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='right',
        x=1,
        font=dict(size=11, color='#CBD5E1')
    )
)

def render_flight_radar_table(recent_df: pd.DataFrame):
    """Renders real-time flight radar table with predicted delays and causes."""
    if recent_df.empty:
        st.info("Awaiting flight radar stream...")
        return

    st.markdown("#### 📡 Live Global Air Traffic Radar Stream (Flightradar24 Scale)")
    
    cols_to_use = [
        'flight_id', 'airline', 'origin', 'destination', 'altitude_ft', 'speed_kts',
        'status', 'weather_condition', 'wind_speed_kts',
        'predicted_delay_min', 'delay_severity', 'primary_cause'
    ]
    avail_cols = [c for c in cols_to_use if c in recent_df.columns]
    display_df = recent_df[avail_cols].copy()

    display_df.rename(columns={
        'flight_id': 'Flight',
        'airline': 'Airline',
        'origin': 'From',
        'destination': 'To',
        'altitude_ft': 'Alt (ft)',
        'speed_kts': 'Speed (kts)',
        'status': 'Status',
        'weather_condition': 'Weather',
        'wind_speed_kts': 'Wind (kts)',
        'predicted_delay_min': 'Est Delay (min)',
        'delay_severity': 'Severity',
        'primary_cause': 'Primary Delay Driver'
    }, inplace=True)

    st.dataframe(
        display_df.head(250),
        use_container_width=True,
        height=280,
        hide_index=True
    )

def render_delay_analytics_charts(recent_df: pd.DataFrame, airline_df: pd.DataFrame, route_df: pd.DataFrame):
    """Renders analytical charts: Weather vs Delay scatter, Airline OTP, and Route Hotspots."""
    col1, col2 = st.columns(2)

    with col1:
        if not recent_df.empty:
            sample_df = recent_df.head(350)
            fig1 = px.scatter(
                sample_df,
                x='wind_speed_kts',
                y='predicted_delay_min',
                color='weather_condition',
                size='congestion_index',
                title="<b>Weather Friction: Wind Speed vs Predicted Delay</b>",
                labels={
                    'wind_speed_kts': 'Surface Wind Speed (knots)',
                    'predicted_delay_min': 'Predicted Delay (minutes)',
                    'weather_condition': 'Weather',
                    'congestion_index': 'Congestion'
                },
                color_discrete_sequence=['#00E5FF', '#10B981', '#F59E0B', '#EF4444', '#A855F7', '#EC4899', '#38BDF8']
            )
            layout1 = dict(**DARK_LAYOUT)
            layout1['height'] = 310
            fig1.update_layout(layout1)
            st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

    with col2:
        if not airline_df.empty:
            fig2 = px.bar(
                airline_df.head(15),
                x='airline',
                y='avg_delay_min',
                color='on_time_pct',
                color_continuous_scale=['#EF4444', '#F59E0B', '#10B981'],
                title="<b>Global Airline Reliability Benchmark: Average Delay & On-Time %</b>",
                labels={
                    'airline': 'Airline',
                    'avg_delay_min': 'Mean Delay (min)',
                    'on_time_pct': 'On-Time %'
                }
            )
            layout2 = dict(**DARK_LAYOUT)
            layout2['height'] = 310
            fig2.update_layout(layout2)
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
