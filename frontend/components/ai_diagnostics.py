import streamlit as st
import pandas as pd
import plotly.express as px
from frontend.components.telemetry_charts import DARK_LAYOUT

def render_ai_diagnostics(ai_insights: dict, drift_results: dict, corr_matrix: dict, notable_corrs: list):
    """Renders the comprehensive Autonomous Non-LLM AI Analysis & Diagnostics Panel."""
    health_status = ai_insights.get('system_health', 'OPTIMAL')
    health_score = ai_insights.get('health_score', 98.0)
    summary_text = ai_insights.get('executive_summary', 'Models operating within nominal operational thresholds.')
    root_causes = ai_insights.get('root_cause_attributions', [])
    recommendations = ai_insights.get('recommended_actions', [])

    badge_class = "badge-optimal" if health_status == 'OPTIMAL' else (
        "badge-degraded" if 'DEGRADED' in health_status else "badge-critical"
    )

    # 1. Executive Narrative Banner
    st.markdown(f"""
    <div class="insight-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="insight-badge {badge_class}">AI SENTINEL // STATUS: {health_status}</span>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #94A3B8;">
                REASONING ENGINE: SCIPY STATS & SKLEARN ML (NO-LLM)
            </span>
        </div>
        <p style="font-size: 15px; line-height: 1.6; color: #E2E8F0; margin: 8px 0 16px 0;">
            {summary_text}
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:
        # 2. Concept & Distribution Drift Table
        st.markdown("#### 🔬 Autonomous Statistical Drift Detection (KS-Test)")
        st.caption("Compares recent telemetry distribution against historical baseline (99% confidence threshold).")
        
        if drift_results:
            drift_rows = []
            for col_name, d in drift_results.items():
                status_icon = "🔴 DRIFT" if d['drift_detected'] else "🟢 STABLE"
                drift_rows.append({
                    "Feature": col_name,
                    "Baseline Mean": f"{d['baseline_mean']:.2f}",
                    "Recent Mean": f"{d['recent_mean']:.2f}",
                    "Shift (%)": f"{d['pct_change']:+.1f}%",
                    "KS Stat": f"{d['statistic']:.3f}",
                    "P-Value": f"{d['p_value']:.4e}",
                    "Drift Status": status_icon
                })
            st.dataframe(pd.DataFrame(drift_rows), use_container_width=True, hide_index=True)
        else:
            st.info("Accumulating baseline records for statistical drift computation...")

        # 3. Root Cause Attribution
        st.markdown("#### 🎯 AI Root-Cause & Attribution Analysis")
        if root_causes:
            for cause in root_causes:
                st.markdown(f"""
                <div class="action-pill" style="border-left-color: #A855F7;">
                    {cause}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div class='action-pill'>No concentrated anomaly vectors identified.</div>", unsafe_allow_html=True)

    with col2:
        # 4. Correlation Matrix & Dependencies
        st.markdown("#### 🔗 Real-Time Multi-Variable Correlations")
        if corr_matrix:
            corr_df = pd.DataFrame(corr_matrix)
            fig = px.imshow(
                corr_df,
                text_auto=".2f",
                aspect="auto",
                color_continuous_scale="RdBu_r",
                zmin=-1,
                zmax=1
            )
            layout = dict(**DARK_LAYOUT)
            layout['height'] = 240
            layout['margin'] = dict(l=30, r=20, t=10, b=10)
            fig.update_layout(layout)
            st.plotly_chart(fig, use_container_width=True)
        
        # 5. Prescriptive Tactical Recommendations
        st.markdown("#### ⚡ Autonomous Prescriptive Actions")
        if recommendations:
            for action in recommendations:
                st.markdown(f"""
                <div class="action-pill">
                    {action}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div class='action-pill'>All pipeline heuristics within target thresholds.</div>", unsafe_allow_html=True)
