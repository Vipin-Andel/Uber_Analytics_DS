import streamlit as st
import pandas as pd
import plotly.express as px
from config import PAGE_CONFIG, THEME_COLORS, apply_custom_css, load_data

st.set_page_config(
    page_title="Corridor Explorer | Uber Analytics",
    page_icon="🗺️",
    layout="wide"
)
apply_custom_css()

# Load Data
try:
    df = load_data()
    df.columns = [c.strip().lower() for c in df.columns]
    data_loaded = True
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    data_loaded = False

st.title("🗺️ Regional Corridor & Demand Flow Explorer")
st.markdown(
    "Analyze high-density mobility corridors, revenue yields per route, and spatial trip distribution.")
st.markdown("---")

if data_loaded:
    pick_col = "pickup_location" if "pickup_location" in df.columns else None
    drop_col = "drop_location" if "drop_location" in df.columns else None
    val_col = "booking_value" if "booking_value" in df.columns else None
    dist_col = "ride_distance" if "ride_distance" in df.columns else None
    status_col = "booking_status" if "booking_status" in df.columns else None

    # Filter Completed Trips
    if status_col:
        comp_df = df[df[status_col].astype(str).str.lower(
        ).str.contains("completed|success", na=False)]
    else:
        comp_df = df

    # -----------------------------
    # 1. Top Corridors Table & Aggregation
    # -----------------------------
    if pick_col and drop_col and val_col and dist_col:
        comp_df["Corridor"] = comp_df[pick_col] + " ➔ " + comp_df[drop_col]

        corridor_stats = comp_df.groupby("Corridor").agg(
            Total_Trips=("Corridor", "count"),
            Total_Revenue=(val_col, "sum"),
            Avg_Distance=(dist_col, "mean"),
            Avg_Fare=(val_col, "mean")
        ).reset_index()

        corridor_stats["Yield_Per_KM"] = corridor_stats["Total_Revenue"] / \
            (corridor_stats["Total_Trips"] * corridor_stats["Avg_Distance"])
        top_10_corridors = corridor_stats.sort_values(
            by="Total_Revenue", ascending=False).head(10)

        # Layout: Split View
        col_left, col_right = st.columns([1.2, 1], gap="large")

        with col_left:
            st.subheader("🏆 Top 10 High-Yield Corridors")

            fig_bar = px.bar(
                top_10_corridors.sort_values(
                    by="Total_Revenue", ascending=True),
                x="Total_Revenue",
                y="Corridor",
                orientation="h",
                text="Total_Trips",
                color_discrete_sequence=[THEME_COLORS["primary"]],
            )
            fig_bar.update_traces(
                texttemplate='%{text} Trips', textposition='inside')
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#FFFFFF",
                xaxis=dict(showgrid=False, title="Realized Revenue (₹)"),
                yaxis=dict(showgrid=False, title=""),
                height=380,
                margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_right:
            st.subheader("🔍 Corridor Specifics")
            selected_corridor = st.selectbox("Select Route Corridor", options=corridor_stats.sort_values(
                by="Total_Trips", ascending=False)["Corridor"].head(25).tolist())

            c_meta = corridor_stats[corridor_stats["Corridor"]
                                    == selected_corridor].iloc[0]

            k1, k2 = st.columns(2)
            with k1:
                st.metric("Total Trips", f"{int(c_meta['Total_Trips']):,}")
                st.metric("Avg Ride Distance",
                          f"{c_meta['Avg_Distance']:.1f} km")
            with k2:
                st.metric("Corridor Revenue",
                          f"₹{c_meta['Total_Revenue']:,.0f}")
                st.metric("Yield Rate", f"₹{c_meta['Yield_Per_KM']:.1f} / km")

            st.markdown("---")
            st.caption("💡 **Yield Rate Insight:** Higher yield routes represent ideal pricing sweet-spots where surge absorption is high and driver deadhead miles are minimal.")

        st.markdown("---")
        st.subheader("📋 Comprehensive Route Corridor Leaderboard")
        st.dataframe(
            corridor_stats.sort_values(by="Total_Revenue", ascending=False).head(50).style.format({
                "Total_Trips": "{:,}",
                "Total_Revenue": "₹{:,.0f}",
                "Avg_Distance": "{:.2f} km",
                "Avg_Fare": "₹{:.2f}",
                "Yield_Per_KM": "₹{:.2f}"
            }),
            use_container_width=True,
            height=280
        )