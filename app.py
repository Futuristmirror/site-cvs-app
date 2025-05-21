
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Closed Vent System Calculator", layout="wide")

st.title("Closed Vent System Assessment Tool")
st.markdown("This is an early prototype based on Site ABC walkdown and Excel logic.")

# Input section
st.header("Basic Inputs")

col1, col2 = st.columns(2)
with col1:
    oil_tank_qty = st.number_input("Oil Tank Quantity", min_value=0, value=4)
    oil_tank_size = st.selectbox("Oil Tank Size (bbl)", options=[210, 300, 400, 500, 750, 1000], index=3)
    oil_design_pressure = st.number_input("Oil Tank Design Pressure (osig)", min_value=0.0, value=16.0)

with col2:
    water_tank_qty = st.number_input("Water Tank Quantity", min_value=0, value=2)
    water_tank_size = st.selectbox("Water Tank Size (bbl)", options=[210, 300, 400, 500, 750, 1000], index=2)
    water_design_pressure = st.number_input("Water Tank Design Pressure (osig)", min_value=0.0, value=16.0)

assumption_note = st.text_input("Any Assumptions?", value="~ tank pressure assumed based on operator input")

# Calculation (placeholder)
st.header("System Calculations")
total_volume = (oil_tank_qty * oil_tank_size) + (water_tank_qty * water_tank_size)
vapor_space = total_volume * 0.25

st.metric(label="Total Tank Volume (bbl)", value=f"{total_volume}")
st.metric(label="Estimated Vapor Space (25%)", value=f"{vapor_space:.1f} bbl")

# Export
st.header("Export")
df = pd.DataFrame({
    "Oil Tanks": [oil_tank_qty],
    "Oil Size": [oil_tank_size],
    "Water Tanks": [water_tank_qty],
    "Water Size": [water_tank_size],
    "Total Volume": [total_volume],
    "Vapor Space": [vapor_space],
    "Assumption": [assumption_note]
})

st.download_button("Download CSV", data=df.to_csv(index=False), file_name="site_output.csv", mime="text/csv")
