import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from config import PAGE_CONFIG, THEME_COLORS, apply_custom_css, load_data

st.set_page_config(page_title="Trip Fare Simulator | Uber Analytics", page_icon="🚖", layout="wide")
apply_custom_css()

# Load Dataset
try:
    df = load_data()
    df.columns = [c.strip().lower() for c in df.columns]
    data_loaded = True
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    data_loaded = False

st.title("🚖 Dynamic Trip Fare & Surge Simulator")
st.markdown("Simulate on-demand trip fares, peak-hour pricing, and cancellation risks across Delhi-NCR corridors.")
st.markdown("---")

if data_loaded:
    # -----------------------------
    # 1. Base Rates & Logic Matrix
    # -----------------------------
    BASE_RATES = {
        "Bike": {"base": 25, "per_km": 8, "per_min": 1.0, "speed_kmh": 28},
        "eBike": {"base": 20, "per_km": 7, "per_min": 0.8, "speed_kmh": 22},
        "Auto": {"base": 35, "per_km": 11, "per_min": 1.2, "speed_kmh": 25},
        "Go Mini": {"base": 50, "per_km": 14, "per_min": 1.5, "speed_kmh": 30},
        "Go Sedan": {"base": 60, "per_km": 16, "per_min": 1.8, "speed_kmh": 32},
        "Premier Sedan": {"base": 80, "per_km": 20, "per_min": 2.2, "speed_kmh": 32},
        "Uber XL": {"base": 110, "per_km": 24, "per_min": 2.5, "speed_kmh": 28},
    }

    # Extract distinct locations
    locations = sorted(df["pickup_location"].dropna().unique().tolist()) if "pickup_location" in df.columns else ["Connaught Place", "Cyber Hub", "Noida Sector 62", "IGI Airport"]

    # -----------------------------
    # 2. Simulator Controls
    # -----------------------------
    col_input, col_result = st.columns([1, 1.2], gap="large")

    with col_input:
        st.subheader("🛠️ Trip Parameters")
        
        c_pick, c_drop = st.columns(2)
        with c_pick:
            pickup = st.selectbox("Pickup Location", options=locations, index=0)
        with c_drop:
            # Default to a different index if available
            drop_idx = min(1, len(locations)-1)
            drop = st.selectbox("Drop Location", options=locations, index=drop_idx)

        c_fleet, c_time = st.columns(2)
        with c_fleet:
            fleet_options = list(BASE_RATES.keys())
            selected_fleet = st.selectbox("Vehicle Category", options=fleet_options, index=2)
        with c_time:
            time_slot = st.selectbox("Time Slot", options=["Morning Rush (8-12 PM)", "Afternoon (12-4 PM)", "Evening Rush (4-8 PM)", "Late Night (12-4 AM)", "Early Morning (4-8 AM)"], index=0)

        st.markdown("#### Surge & Traffic Multipliers")
        surge_mult = st.slider("Dynamic Surge Multiplier", min_value=1.0, max_value=3.0, value=1.2, step=0.1, help="Simulate demand-supply imbalance.")
        is_raining = st.checkbox("🌧️ Rain / Weather Disruption (+15% ETA & Risk)")

        # Historical distance lookup or default
        matched_rides = df[(df["pickup_location"] == pickup) & (df["drop_location"] == drop)] if ("pickup_location" in df.columns and "drop_location" in df.columns) else pd.DataFrame()
        
        if len(matched_rides) > 0 and "ride_distance" in matched_rides.columns:
            est_distance = float(matched_rides["ride_distance"].mean())
        else:
            est_distance = 18.5  # Realistic average trip distance

        st.info(f"📍 **Estimated Route Distance:** `{est_distance:.1f} km`")

    # -----------------------------
    # 3. Dynamic Fare Engine
    # -----------------------------
    rate_info = BASE_RATES[selected_fleet]
    traffic_factor = 1.35 if "Rush" in time_slot else (0.85 if "Late Night" in time_slot else 1.0)
    if is_raining:
        traffic_factor *= 1.15

    est_duration_mins = (est_distance / rate_info["speed_kmh"]) * 60 * traffic_factor
    
    base_fare = rate_info["base"] + (est_distance * rate_info["per_km"]) + (est_duration_mins * rate_info["per_min"])
    final_fare = round(base_fare * surge_mult, 2)
    
    # Revenue split
    driver_share = round(final_fare * 0.78, 2)
    platform_fee = round(final_fare * 0.17, 2)
    taxes = round(final_fare * 0.05, 2)

    # Cancellation Risk Estimation
    base_risk = 18.0 if selected_fleet in ["Auto", "Bike"] else 12.0
    if surge_mult > 1.8:
        base_risk += 6.0
    if "Rush" in time_slot:
        base_risk += 4.5
    if is_raining:
        base_risk += 5.0
    cancel_risk = min(round(base_risk, 1), 65.0)

    with col_result:
        st.subheader("📊 Fare & Economics Output")
        
        r1, r2, r3 = st.columns(3)
        with r1:
            st.metric("Total Fare", f"₹{final_fare:,.0f}", delta=f"{(surge_mult-1.0)*100:.0f}% Surge" if surge_mult > 1.0 else None)
        with r2:
            st.metric("Estimated ETA", f"{int(est_duration_mins)} mins")
        with r3:
            st.metric("Cancel Risk", f"{cancel_risk}%", delta="-High" if cancel_risk > 25 else "Normal", delta_color="inverse")

        st.markdown("---")
        st.markdown("#### 💰 Revenue Distribution Breakdown")

        fig_breakdown = go.Figure(go.Bar(
            x=[driver_share, platform_fee, taxes],
            y=["Driver Payout (78%)", "Uber Platform Cut (17%)", "GST & Tolls (5%)"],
            orientation='h',
            marker=dict(color=[THEME_COLORS["primary"], "#F59E0B", "#64748B"]),
            text=[f"₹{driver_share}", f"₹{platform_fee}", f"₹{taxes}"],
            textposition='auto',
        ))
        fig_breakdown.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#FFFFFF",
            xaxis=dict(showgrid=False, title="Amount (₹)"),
            yaxis=dict(showgrid=False),
            height=240,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_breakdown, use_container_width=True)

        # Strategic Insight Tag
        if surge_mult > 1.5:
            st.warning(f"⚠️ High Surge ({surge_mult}x) detected. High driver conversion likely, but rider cancellation sensitivity increases by ~12%.")
        else:
            st.success("✅ Standard demand corridor. Optimal booking-to-completion ratio expected.")
            