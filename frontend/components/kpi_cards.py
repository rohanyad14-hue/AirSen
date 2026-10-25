import streamlit as st

def render_kpi_cards(summary_metrics: dict, worker_status: dict):
    """Renders sleek glassmorphic executive Air Assistant KPI cards."""
    total_records = summary_metrics.get('total_records', 0)
    avg_delay = summary_metrics.get('avg_predicted_delay', 0.0)
    on_time_rate = summary_metrics.get('on_time_rate', 100.0)
    severe_count = summary_metrics.get('severe_delays_count', 0)
    mean_wind = summary_metrics.get('mean_fleet_wind', 0.0)
    storm_hub = worker_status.get('storm_hub', None)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">
                <span>Active Flight Stream</span>
                <span class="duckdb-tag">DUCKDB</span>
            </div>
            <div class="metric-value">{int(total_records):,}</div>
            <div class="metric-sub">⚡ Ingesting {worker_status.get('batch_size', 20)} flights/sec</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        delay_color = "#10B981" if avg_delay <= 15.0 else ("#F59E0B" if avg_delay <= 35.0 else "#EF4444")
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">
                <span>Mean Predicted Delay</span>
                <span style="color: {delay_color}; font-weight: 700;">AI INFERENCE</span>
            </div>
            <div class="metric-value" style="color: {delay_color};">+{avg_delay:.1f} <span style="font-size: 16px; color: #94A3B8;">min</span></div>
            <div class="metric-sub">Across all airborne corridors</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        otp_color = "#10B981" if on_time_rate >= 80.0 else ("#F59E0B" if on_time_rate >= 65.0 else "#EF4444")
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">
                <span>On-Time Performance</span>
                <span style="color: {otp_color};">OTP INDEX</span>
            </div>
            <div class="metric-value" style="color: {otp_color};">{on_time_rate:.1f}%</div>
            <div class="metric-sub">⚠️ {int(severe_count):,} flights with &gt;45m delay</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        alert_text = f"⛈ STORM AT {storm_hub}" if storm_hub else "NORMAL ATMOSPHERE"
        alert_color = "#EF4444" if storm_hub else "#38BDF8"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">
                <span>Weather Threat Alert</span>
                <span style="color: {alert_color}; font-weight: 600;">{alert_text}</span>
            </div>
            <div class="metric-value" style="color: {alert_color}; font-size: 22px;">{mean_wind:.1f} <span style="font-size: 16px; color: #94A3B8;">kts avg wind</span></div>
            <div class="metric-sub">Real-time METAR friction</div>
        </div>
        """, unsafe_allow_html=True)
