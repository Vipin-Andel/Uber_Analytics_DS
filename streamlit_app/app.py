import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import PAGE_CONFIG, THEME_COLORS, apply_custom_css, load_data

# Initialize Page Settings
st.set_page_config(**PAGE_CONFIG)
apply_custom_css()

# Load Dataset
try:
    df = load_data()
    # Normalize column names to lowercase for robust matching
    df.columns = [c.strip().lower() for c in df.columns]
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {e}")
    data_loaded = False

# Sidebar Branding & System Context
with st.sidebar:
    st.title("🚖 Uber Executive")
    st.caption("Mobility & Revenue Decision Platform")
    st.markdown("---")
    st.markdown("### 📍 System Context")
    st.write("**Region:** Delhi-NCR")
    st.write(
        f"**Records Processed:** {len(df):,}" if data_loaded else "No Data")
    st.markdown("---")
    st.caption("v1.0 Executive Build | Phase 4")

# Main Header
st.title("Executive Mobility Intelligence Hub")
st.markdown(
    "High-level executive overview of demand fulfillment, fleet revenue realization, and trip economics.")

if data_loaded:
    # -----------------------------
    # 1. Top KPI Summary Cards
    # -----------------------------
    total_bookings = len(df)

    # Check for status column
    status_col = "booking_status" if "booking_status" in df.columns else None
    value_col = "booking_value" if "booking_value" in df.columns else None
    dist_col = "ride_distance" if "ride_distance" in df.columns else None
    fleet_col = "vehicle_category" if "vehicle_category" in df.columns else (
        "vehicle_type" if "vehicle_type" in df.columns else None)

    if status_col:
        completed_mask = df[status_col].astype(
            str).str.lower().str.contains("completed|success", na=False)
        completed_trips = df[completed_mask]
        cancel_mask = df[status_col].astype(
            str).str.lower().str.contains("cancel", na=False)
        cancel_rate = (cancel_mask.sum() / total_bookings) * \
            100 if total_bookings > 0 else 0
    else:
        completed_trips = df
        cancel_rate = 0.0

    realized_rev = completed_trips[value_col].sum(
    ) if value_col and value_col in completed_trips.columns else 0.0
    avg_distance = df[dist_col].mean(
    ) if dist_col and dist_col in df.columns else 0.0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Bookings", value=f"{total_bookings:,}")
    with col2:
        st.metric(label="Realized Revenue", value=f"₹{realized_rev:,.2f}")
    with col3:
        st.metric(label="Avg Trip Distance", value=f"{avg_distance:.2f} km")
    with col4:
        st.metric(label="Cancellation Rate", value=f"{cancel_rate:.1f}%")

    st.markdown("---")

    # -----------------------------
    # 2. Executive Visuals Row
    # -----------------------------
    c1, c2 = st.columns([1, 1])

    with c1:
        st.subheader("Booking Fulfillment Split")
        if status_col:
            status_counts = df[status_col].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]

            fig_donut = px.pie(
                status_counts,
                names="Status",
                values="Count",
                hole=0.55,
                color_discrete_sequence=[
                    THEME_COLORS["primary"], "#F59E0B", THEME_COLORS["card_bg"], "#64748B", "#EF4444"],
            )
            fig_donut.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#FFFFFF",
                legend=dict(orientation="h", yanchor="bottom", y=-0.2),
                margin=dict(l=20, r=20, t=30, b=20),
            )
            st.plotly_chart(fig_donut, use_container_width=True)

    with c2:
        st.subheader("Revenue Contribution by Fleet")
        if fleet_col and value_col:
            fleet_rev = completed_trips.groupby(
                fleet_col)[value_col].sum().reset_index()
            fleet_rev = fleet_rev.sort_values(by=value_col, ascending=True)

            fig_bar = px.bar(
                fleet_rev,
                x=value_col,
                y=fleet_col,
                orientation="h",
                color_discrete_sequence=[THEME_COLORS["primary"]],
            )
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#FFFFFF",
                xaxis=dict(showgrid=False, title="Realized Revenue (₹)"),
                yaxis=dict(showgrid=False, title=""),
                margin=dict(l=20, r=20, t=30, b=20),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.info("👈 Use the **Sidebar Menu** to explore the **Trip Fare Simulator**, **Scenario Analysis**, and **Corridor Explorer**.")
