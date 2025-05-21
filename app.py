import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Closed Vent System Calculator", layout="wide")
st.title("Closed Vent System Assessment Tool")

# Setup Tabs
tab1, tab2 = st.tabs(["🛢 Tank Layout", "🌊 Main Process"])

# -----------------------------
# Tab 1: Tank Layout
# -----------------------------
with tab1:
    st.header("Tank Layout")

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

    # Calculations
    total_volume = (oil_tank_qty * oil_tank_size) + (water_tank_qty * water_tank_size)
    vapor_space = total_volume * 0.25

    st.metric(label="Total Tank Volume (bbl)", value=f"{total_volume}")
    st.metric(label="Estimated Vapor Space (25%)", value=f"{vapor_space:.1f} bbl")

    # Export
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


# -----------------------------
# Tab 2: Main Process
# -----------------------------
with tab2:
    st.header("Main Process – Oil & Water PPIVFR (Surge Adjusted)")
    oil_col, water_col = st.columns(2)

    # -----------------------------
    # Oil Section
    # -----------------------------
    with oil_col:
        st.subheader("Oil Section")
        oil_production = st.number_input("Oil Production (bbl/day)", min_value=0.0, value=350.0)
        oil_pressure = st.number_input("Oil Pressure - Last Stage (psig)", min_value=0.0, value=5.0)
        surge_percent = st.number_input("Surge Percent (%)", min_value=0.0, value=30.0)
        promax_flash = st.text_input("PROMAX Flash (SCF/BBL) [optional]", value="")
        promax_mw = st.text_input("PROMAX Vapor MW [optional]", value="")

        base_flash = 12.0
        default_mw = 28.97
        default_vapor_mw = 46.0

        try:
            promax_flash_val = float(promax_flash)
            promax_mw_val = float(promax_mw) if promax_mw else default_vapor_mw
            flash_working = (base_flash + promax_flash_val) * math.sqrt(promax_mw_val / default_mw)
            flash_source = "PROMAX"
        except:
            flash_working = (base_flash + oil_pressure * 1.15 * 1.5) * math.sqrt(default_vapor_mw / default_mw)
            flash_source = "Pressure-based"

        oil_flowrate = oil_production / 34.2
        adjusted_bbl_per_day = ((oil_flowrate * surge_percent / 100) + oil_flowrate) * 34.2
        oil_ppivfr = flash_working * adjusted_bbl_per_day / 1_000_000

        st.write(f"**Flash + Working Volume (Oil)**: {flash_working:.2f} SCF/BBL ({flash_source})")
        st.write(f"**Oil Flowrate**: {oil_flowrate:.2f} GPM")
        st.write(f"**Adjusted BBL/day (with surge)**: {adjusted_bbl_per_day:.2f}")
        st.metric("Oil PPIVFR (mmscfd, SG=1)", f"{oil_ppivfr:.5f}")

    # -----------------------------
    # Water Section
    # -----------------------------
    with water_col:
        st.subheader("Water Section")
        water_production = st.number_input("Water Production (bbl/day)", min_value=0.0, value=700.0)
        water_pressure = st.number_input("Water Pressure - First Stage (psig)", min_value=0.0, value=120.0)
        water_surge_percent = st.number_input("Surge Percent (Water) (%)", min_value=0.0, value=30.0)
        promax_water_flash = st.text_input("PROMAX Flash for Water (SCF/BBL) [optional]", value="")
        promax_water_mw = st.text_input("PROMAX Vapor MW for Water [optional]", value="")

        water_base_flash = 6.0
        carryover_flash = 4.0
        default_water_mw = 46.0

        try:
            promax_water_flash_val = float(promax_water_flash)
            promax_water_mw_val = float(promax_water_mw) if promax_water_mw else default_water_mw
            flash_working_water = (water_base_flash + promax_water_flash_val) * math.sqrt(promax_water_mw_val / default_mw)
            flash_source_water = "PROMAX"
        except:
            flash_working_water = (water_base_flash + carryover_flash) * math.sqrt(default_water_mw / default_mw)
            flash_source_water = "Calculated"

        water_flowrate = water_production / 34.2
        adjusted_bbl_per_day_water = ((water_flowrate * water_surge_percent / 100) + water_flowrate) * 34.2
        water_ppivfr = flash_working_water * adjusted_bbl_per_day_water / 1_000_000

        st.write(f"**Flash + Working Volume (Water)**: {flash_working_water:.2f} SCF/BBL ({flash_source_water})")
        st.write(f"**Water Flowrate**: {water_flowrate:.2f} GPM")
        st.write(f"**Adjusted BBL/day (with surge)**: {adjusted_bbl_per_day_water:.2f}")
        st.metric("Water PPIVFR (mmscfd, SG=1)", f"{water_ppivfr:.5f}")


