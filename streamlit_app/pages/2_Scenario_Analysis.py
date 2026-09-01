import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from config import PAGE_CONFIG, THEME_COLORS, apply_custom_css, load_data

st.set_page_config(
    page_title="Scenario Analysis | Uber Analytics",
    page_icon="📈",
    layout="wide"
)
apply_custom_css()

# Load Dataset
try:
    df = load_data()
    df.columns = [c.strip().lower() for c in df.columns]
    data_loaded = True
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    data_loaded = False

st.title("📈 Executive What-If & Scenario Simulator")
st.markdown("Simulate supply-side incentives, driver cancellation suppression, and net revenue recovery projections.")
st.markdown("---")

if data_loaded:
    # Baseline Metrics
    total_trips = len(df)
    status_col = "booking_status" if "booking_status" in df.columns else None
    val_col = "booking_value" if "booking_value" in df.columns else None

    # Driver cancellation baseline
    if status_col:
        driver_cancel_trips = df[df[status_col].astype(
            str).str.lower().str.contains("driver", na=False)]
        baseline_driver_cancel_count = len(driver_cancel_trips)
    else:
        baseline_driver_cancel_count = int(total_trips * 0.18)

    avg_booking_val = float(
        df[val_col].mean()) if val_col and val_col in df.columns else 508.0
    baseline_lost_revenue = baseline_driver_cancel_count * avg_booking_val

    # -----------------------------
    # 1. Simulation Inputs
    # -----------------------------
    c_left, c_right = st.columns([1, 1.2], gap="large")

    with c_left:
        st.subheader("⚙️ Incentive Policy Controls")

        target_fleet = st.selectbox(
            "Select Target Vehicle Fleet",
            options=["All Fleets", "Auto", "Bike", "Go Mini",
                     "Go Sedan", "Premier Sedan", "Uber XL"],
            index=0
        )

        bonus_per_trip = st.slider(
            "Driver Peak Incentive Bonus (₹ / Trip)",
            min_value=0,
            max_value=100,
            value=35,
            step=5,
            help="Additional per-trip payout during high-demand hours."
        )

        min_rides_threshold = st.slider(
            "Daily Milestone Requirement (Rides / Day)",
            min_value=5,
            max_value=20,
            value=10,
            step=1,
            help="Minimum completed rides to qualify for driver bonus."
        )

        st.markdown("---")
        st.write("#### 🎯 Strategic Assumptions")
        # Elasticity: for every ₹10 incentive, cancellation drops by ~3.2%
        # Max 45% drop ceiling
        reduction_rate = min(bonus_per_trip * 0.32, 45.0)
        st.write(
            f"• **Projected Driver Acceptance Lift:** `+{reduction_rate:.1f}%`")
        st.write(f"• **Target Fleet Scope:** `{target_fleet}`")

    # -----------------------------
    # 2. Simulation Calculations
    # -----------------------------
    recovered_trips = int(baseline_driver_cancel_count *
                          (reduction_rate / 100.0))
    recovered_gross_rev = recovered_trips * avg_booking_val
    uber_commission_rev = recovered_gross_rev * 0.20  # 20% Uber cut

    # Cost of incentive (applied to recovered + a share of active completed rides)
    qualified_drivers_cost = (
        recovered_trips + int(total_trips * 0.15)) * (bonus_per_trip * 0.4)
    net_profit_impact = uber_commission_rev - qualified_drivers_cost

    with c_right:
        st.subheader("📊 Scenario Financial Impact")

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(
                label="Recovered Rides",
                value=f"{recovered_trips:,}",
                delta=f"-{reduction_rate:.1f}% Cancel"
            )
        with m2:
            st.metric(
                label="Recovered Gross Revenue",
                value=f"₹{recovered_gross_rev/100000:,.2f}L",
                delta="Revenue Lift"
            )
        with m3:
            st.metric(
                label="Net Economic Impact",
                value=f"₹{net_profit_impact/100000:,.2f}L",
                delta="Positive ROI" if net_profit_impact > 0 else "High Cost",
                delta_color="normal" if net_profit_impact > 0 else "inverse"
            )

        st.markdown("---")
        st.markdown("#### ⚖️ Baseline vs Simulated Recovery Comparison")

        categories = ["Driver Cancelled Rides",
                      "Lost Revenue (₹ Lakhs)", "Net Revenue Yield (₹ Lakhs)"]
        baseline_vals = [
            baseline_driver_cancel_count,
            round(baseline_lost_revenue / 100000, 2),
            round((total_trips * avg_booking_val * 0.20) / 100000, 2)
        ]
        simulated_vals = [
            baseline_driver_cancel_count - recovered_trips,
            round((baseline_lost_revenue - recovered_gross_rev) / 100000, 2),
            round(((total_trips * avg_booking_val * 0.20) +
                  net_profit_impact) / 100000, 2)
        ]

        fig_compare = go.Figure(data=[
            go.Bar(name='Baseline (Current)', x=categories,
                   y=baseline_vals, marker_color='#64748B'),
            go.Bar(name='Simulated (With Incentive)', x=categories,
                   y=simulated_vals, marker_color=THEME_COLORS["primary"])
        ])
        fig_compare.update_layout(
            barmode='group',
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#FFFFFF",
            legend=dict(orientation="h", yanchor="bottom", y=-0.3),
            height=280,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_compare, use_container_width=True)

        if net_profit_impact > 0:
            st.success(
                f"💡 **Executive Recommendation:** The ₹{bonus_per_trip}/trip incentive is financially viable, yielding a positive net platform ROI while converting {recovered_trips:,} lost riders.")
        else:
            st.error(f"⚠️ **Cost Warning:** High incentive cost outweighs commission gains. Lower bonus to ₹25-35 to maintain positive unit economics.")
