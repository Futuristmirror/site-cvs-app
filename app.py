import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Closed Vent System Calculator", layout="wide")
st.title("Closed Vent System Assessment Tool")

# Setup Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🛢 Tank Layout", "🌊 Main Process", "➕ Add to Main Process", "🌬 MAIN TANK VENT"])


# -----------------------------
# Tab 1: Tank Layout
# -----------------------------
with tab1:
    st.header("Tank Layout")

    st.subheader("Oil & Water Tank Setup")
    col1, col2 = st.columns(2)
    with col1:
        oil_tank_qty = st.number_input("Oil Tank Quantity", min_value=0, value=7)
        oil_tank_size = st.selectbox("Oil Tank Size (bbl)", options=[210, 300, 400, 500, 750, 1000], index=3)
        oil_tank_rating = st.number_input("Lowest Oil Tank Rating (oz)", min_value=0.0, value=16.0)

        oil_scfh = oil_tank_qty * oil_tank_size if oil_tank_qty else 0
        st.markdown("#### Oil SCFH")
        st.metric("Oil Tanks SCFH", f"{oil_scfh}")

    with col2:
        water_tank_qty = st.number_input("Water Tank Quantity", min_value=0, value=4)
        water_tank_size = st.selectbox("Water Tank Size (bbl)", options=[210, 300, 400, 500, 750, 1000], index=3)
        water_tank_rating = st.number_input("Lowest Water Tank Rating (oz)", min_value=0.0, value=16.0)

        water_scfh = water_tank_size * 0.6 * water_tank_qty if water_tank_qty else 0
        st.markdown("#### Water SCFH")
        st.metric("Water Tanks SCFH", f"{water_scfh}")

    # Total PPIVFR row below both
    total_thermal_ppivfr = (oil_scfh + water_scfh) * 24 / 1_000_000
    st.markdown("#### Total Thermal PPIVFR")
    st.metric("Total Thermal PPIVFR", f"{total_thermal_ppivfr:.5f} mmscfd")

    st.markdown("### Pressure Inputs")
    col3, col4 = st.columns(2)
    with col3:
        thief_prv_input = st.number_input("Minimum Thief Hatch/PRV (osig)", min_value=0.0, value=8.0)
    with col4:
        leaking_safety = st.number_input("Leaking Safety Factor (osig)", min_value=0.0, value=2.0)

    design_pressure = (thief_prv_input - leaking_safety) * 0.9
    st.metric("Design Pressure", f"{design_pressure:.2f} osig")

    if design_pressure < 0:
        st.warning("⚠️ Leaking Safety Factor is greater than PRV — design pressure may be invalid.")

    st.markdown("### Notes")
    st.text_area("Assumptions / Observations", "~ tank pressure assumed based on operator input", height=80)


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
# -----------------------------
# Tab 3: Add to Main Process
# -----------------------------
with tab3:
    st.header("➕ Add to Main Process")

    st.markdown("This section will allow you to define additional process sources that contribute to total PPIVFR (e.g., LACT, Recirc, Vapor Return).")

    st.info("🛠 GOT PISSED AND STOPPED HERE")

   # -----------------------------
# Tab 4: MAIN TANK VENT
# -----------------------------
with tab4:
    st.header("🌬 MAIN TANK VENT HEADER1 (3\" Only)")

    st.markdown("This prototype models the 3\" header row using the original Excel formulas. Blue = calculated values, Green = input.")

    st.subheader("Pipe Characteristics")

    # User input for developed length (G6)
    developed_length = st.number_input("Developed Length (ft)", min_value=0.0, value=0.0, step=1.0)

    # Constants (G7 to G11)
    ID_in = 3.068  # G7
    eD = 12 * 0.00015 / ID_in  # G8
    turb_factor = 0.25 / (math.log10(eD / 3.7) ** 2)  # G9
    spitz_factor = (1 + 3.6 / ID_in + 0.03 * ID_in) / 100  # G10
    ratio = turb_factor / spitz_factor  # G11

    col1, col2 = st.columns(2)
    with col1:
        st.metric("ID (inches)", f"{ID_in:.3f}")
        st.metric("ε/D", f"{eD:.5f}")
        st.metric("Turb Friction Factor fr", f"{turb_factor:.4f}")
    with col2:
        st.metric("Spitzglass ƒspzz", f"{spitz_factor:.5f}")
        st.metric("Ratio (fr / ƒspzz)", f"{ratio:.4f}")

    st.subheader("Pipe Fittings – 3\"")

    # Inputs: Quantities for fittings (G13–G16)
    tee_run = st.number_input("Tee, Flow thru run (qty)", min_value=0, value=0, step=1)
    tee_branch = st.number_input("Tee, Flow thru branch (qty)", min_value=0, value=0, step=1)
    elbow_90 = st.number_input("Elbow, 90° Threaded (qty)", min_value=0, value=0, step=1)
    elbow_45 = st.number_input("Elbow, 45° Threaded (qty)", min_value=0, value=0, step=1)

    # Calculated Le values (H13–H16)
    def calc_le(qty, multiplier):
        return qty * (1 / 12) * ID_in * multiplier

    le_tee_run = calc_le(tee_run, 20)
    le_tee_branch = calc_le(tee_branch, 60)
    le_elbow_90 = calc_le(elbow_90, 30)
    le_elbow_45 = calc_le(elbow_45, 16)

    st.markdown("#### Equivalent Lengths (Le, ft)")

    le_col1, le_col2 = st.columns(2)
    with le_col1:
        st.metric("Le - Tee, Run", f"{le_tee_run:.2f}")
        st.metric("Le - Tee, Branch", f"{le_tee_branch:.2f}")
    with le_col2:
        st.metric("Le - Elbow 90°", f"{le_elbow_90:.2f}")
        st.metric("Le - Elbow 45°", f"{le_elbow_45:.2f}")

    st.subheader("Summary")

    total_le = le_tee_run + le_tee_branch + le_elbow_90 + le_elbow_45
    total_pipe = developed_length + total_le

    st.metric("Total Equivalent Fittings Le (ft)", f"{total_le:.2f}")
    st.metric("Total Length of 3\" Header (ft)", f"{total_pipe:.2f}")

