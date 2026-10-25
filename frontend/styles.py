def get_custom_css():
    """Returns ultra-sleek, modern dark-mode CSS for the Streamlit dashboard."""
    return """
    <style>
    /* Global Base */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    code, pre, .stCodeBlock {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Main Container background */
    .stApp {
        background-color: #080C14;
        color: #E2E8F0;
    }

    /* Top Header */
    .sentinel-header {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.5) 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }

    .sentinel-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #00F0FF, #7000FF, #00FF87);
    }

    .sentinel-title {
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #FFFFFF, #94A3B8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 6px 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .sentinel-subtitle {
        font-size: 14px;
        color: #64748B;
        margin: 0;
    }

    /* Live Badge */
    .badge-live {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        background: rgba(0, 230, 118, 0.15);
        color: #00E676;
        border: 1px solid rgba(0, 230, 118, 0.3);
    }

    .badge-pulse {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #00E676;
        box-shadow: 0 0 10px #00E676;
        animation: pulse-dot 1.5s infinite;
    }

    @keyframes pulse-dot {
        0% { transform: scale(0.9); opacity: 0.7; }
        50% { transform: scale(1.3); opacity: 1; }
        100% { transform: scale(0.9); opacity: 0.7; }
    }

    /* Glassmorphic Metric Cards */
    .metric-card {
        background: linear-gradient(180deg, rgba(17, 24, 39, 0.7) 0%, rgba(15, 23, 42, 0.6) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.4);
    }

    .metric-title {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #F8FAFC;
        letter-spacing: -0.5px;
    }

    .metric-sub {
        font-size: 12px;
        color: #64748B;
        margin-top: 6px;
    }

    /* Autonomous Insight Banner */
    .insight-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(20, 30, 48, 0.85) 100%);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 20px;
        position: relative;
    }

    .insight-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
    }

    .badge-optimal {
        background: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .badge-degraded {
        background: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }

    .badge-critical {
        background: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    /* Action item cards */
    .action-pill {
        background: rgba(30, 41, 59, 0.7);
        border-left: 3px solid #38BDF8;
        padding: 10px 14px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 8px;
        font-size: 13px;
        color: #CBD5E1;
    }

    /* Custom Streamlit tabs & buttons */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 42px;
        border-radius: 8px;
        padding: 0 18px;
        background-color: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        color: #94A3B8;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background-color: rgba(56, 189, 248, 0.15) !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
        color: #38BDF8 !important;
        font-weight: 600;
    }

    /* DuckDB Badge */
    .duckdb-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        background: #FFF314;
        color: #000000;
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 4px;
        display: inline-block;
    }
    </style>
    """
