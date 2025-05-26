import streamlit as st
import math

st.set_page_config(page_title="Closed Vent System Calculator", layout="wide")
st.title("Closed Vent System Assessment Tool")

# Setup Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🛢 Tank Layout",
    "🌊 Main Process",
    "➕ Add to Main Process",
    "🌬 MAIN TANK VENT1",
    "🌬 MAIN TANK VENT2",
    "🌬 FlareVent"
])

# -----------------------------
# Tank Layout Tab
# -----------------------------
with tab1:
    st.header("Tank Layout")
    col1, col2 = st.columns(2)
    with col1:
        oil_tank_qty = st.number_input("Oil Tank Quantity", min_value=0, value=7)
        oil_tank_size = st.selectbox("Oil Tank Size (bbl)", options=[210, 300, 400, 500, 750, 1000], index=3)
        oil_tank_rating = st.number_input("Lowest Oil Tank Rating (oz)", min_value=0.0, value=16.0)
        oil_scfh = oil_tank_qty * oil_tank_size if oil_tank_qty else 0
        st.metric("Oil Tanks SCFH", f"{oil_scfh}")
    with col2:
        water_tank_qty = st.number_input("Water Tank Quantity", min_value=0, value=4)
        water_tank_size = st.selectbox("Water Tank Size (bbl)", options=[210, 300, 400, 500, 750, 1000], index=3)
        water_tank_rating = st.number_input("Lowest Water Tank Rating (oz)", min_value=0.0, value=16.0)
        water_scfh = water_tank_size * 0.6 * water_tank_qty if water_tank_qty else 0
        st.metric("Water Tanks SCFH", f"{water_scfh}")
    total_thermal_ppivfr = (oil_scfh + water_scfh) * 24 / 1_000_000
    st.metric("Total Thermal PPIVFR", f"{total_thermal_ppivfr:.5f} mmscfd")
    col3, col4 = st.columns(2)
    with col3:
        thief_prv_input = st.number_input("Minimum Thief Hatch/PRV (osig)", min_value=0.0, value=8.0)
    with col4:
        leaking_safety = st.number_input("Leaking Safety Factor (osig)", min_value=0.0, value=2.0)
    design_pressure = (thief_prv_input - leaking_safety) * 0.9
    st.metric("Design Pressure", f"{design_pressure:.2f} osig")
    if design_pressure < 0:
        st.warning("⚠️ Leaking Safety Factor is greater than PRV — design pressure may be invalid.")
    st.text_area("Assumptions / Observations", "~ tank pressure assumed based on operator input", height=80)

# -----------------------------
# Main Process Tab
# -----------------------------
with tab2:
    st.header("Main Process – Oil & Water PPIVFR (Surge Adjusted)")
    oil_col, water_col = st.columns(2)
    with oil_col:
        oil_production = st.number_input("Oil Production (bbl/day)", min_value=0.0, value=350.0)
        oil_pressure = st.number_input("Oil Pressure - Last Stage (psig)", min_value=0.0, value=5.0)
        surge_percent = st.number_input("Surge Percent (%)", min_value=0.0, value=30.0)
        promax_flash = st.text_input("PROMAX Flash (SCF/BBL) [optional]", value="")
        promax_mw = st.text_input("PROMAX Vapor MW [optional]", value="")
        base_flash, default_mw, default_vapor_mw = 12.0, 28.97, 46.0
        try:
            flash_working = (base_flash + float(promax_flash)) * math.sqrt(float(promax_mw or default_vapor_mw) / default_mw)
        except:
            flash_working = (base_flash + oil_pressure * 1.15 * 1.5) * math.sqrt(default_vapor_mw / default_mw)
        oil_flowrate = oil_production / 34.2
        adjusted_bbl_per_day = ((oil_flowrate * surge_percent / 100) + oil_flowrate) * 34.2
        oil_ppivfr = flash_working * adjusted_bbl_per_day / 1_000_000
        st.metric("Oil PPIVFR (mmscfd, SG=1)", f"{oil_ppivfr:.5f}")
    with water_col:
        water_production = st.number_input("Water Production (bbl/day)", min_value=0.0, value=700.0)
        water_pressure = st.number_input("Water Pressure - First Stage (psig)", min_value=0.0, value=120.0)
        water_surge_percent = st.number_input("Surge Percent (Water) (%)", min_value=0.0, value=30.0)
        promax_water_flash = st.text_input("PROMAX Flash for Water (SCF/BBL) [optional]", value="")
        promax_water_mw = st.text_input("PROMAX Vapor MW for Water [optional]", value="")
        water_base_flash, carryover_flash = 6.0, 4.0
        try:
            flash_working_water = (water_base_flash + float(promax_water_flash)) * math.sqrt(float(promax_water_mw or default_vapor_mw) / default_mw)
        except:
            flash_working_water = (water_base_flash + carryover_flash) * math.sqrt(default_vapor_mw / default_mw)
        water_flowrate = water_production / 34.2
        adjusted_bbl_per_day_water = ((water_flowrate * water_surge_percent / 100) + water_flowrate) * 34.2
        water_ppivfr = flash_working_water * adjusted_bbl_per_day_water / 1_000_000
        st.metric("Water PPIVFR (mmscfd, SG=1)", f"{water_ppivfr:.5f}")

# -----------------------------
# Add to Main Process Tab
# -----------------------------
with tab3:
    st.header("➕ Add to Main Process")
    st.info("🛠 Section under development...")

# -----------------------------
# Vent Tabs (shared logic)
# -----------------------------
def render_vent_tab(tab_label):
    st.subheader("Summary")
    total_nps_sum = 0
    id_configs = [{"label": f'{n}"', "id_in": d} for n, d in zip(
        [1.5, 2, 3, 4, 6, 8, 10, 12], [1.338, 2.067, 3.068, 4.026, 6.070, 7.981, 10.020, 11.938]
    )]
    col_sets = st.columns(len(id_configs))
    for config, col in zip(id_configs, col_sets):
        with col:
            label, ID_in = config["label"], config["id_in"]
            developed_length = st.number_input(f"{tab_label} {label} Developed Length (ft)", min_value=0.0, value=0.0, key=f"{tab_label}_dev_{label}")
            fittings = [
                ("Tee, Flow thru run", 20), ("Tee, Flow thru branch", 60),
                ("Elbow, 90° Threaded", 30), ("Elbow, 45° Threaded", 16),
                ("Elbow, 90° (R/D ~3)", 14), ("Elbow, 45° (R/D ~3)", 9.9),
                ("Gate Valve", 8), ("Globe Valve", 340), ("Ball Valve", 3),
                ("Butterfly Valve", 45), ("Check Valve", 100), ("Entrance / Exit", 1)
            ]
            le_fittings = sum(st.number_input(f"{tab_label} {label} {name}", min_value=0, value=0, key=f"{tab_label}_{label}_{name}") * (1/12) * ID_in * mult for name, mult in fittings)
            knockout_le = sum(
                (lambda d: (1/12)*ID_in*((1-(ID_in**2)/(d**2))**2 if d > ID_in else 0.5*(1-(d**2)/(ID_in**2)))
                (st.number_input(f"{tab_label} {label} Knockout {i+1}", min_value=0.0, value=0.0, key=f"{tab_label}_knockout_{label}_{i}"))
                for i in range(3)
            )
            spec_valve_le = sum(
                (lambda cv: 100*891*(ID_in**5)/(12*(1+(3.6/ID_in)+(0.03*ID_in))*(cv**2) if cv else 0.0))
                (st.number_input(f"{tab_label} {label} Cv {i+1}", min_value=0.0, value=0.0, key=f"{tab_label}_cv_{label}_{i}"))
                for i in range(3)
            )
            total_pipe = developed_length + le_fittings + knockout_le + spec_valve_le
            conv_numerator = total_pipe * (1 + 3.6/ID_in + 0.03*ID_in) * 3.068**5
            conv_denominator = ID_in**5 * (1 + 3.6/3.068 + 0.03*3.068)
            total_pipe_nps = conv_numerator / conv_denominator
            total_nps_sum += total_pipe_nps
            st.metric(f"{label} Total Header Length", f"{total_pipe:.2f} ft")
            st.metric(f"{label} Total Length of 3\" NPS", f"{total_pipe_nps:.2f} ft")
    if total_nps_sum > 0:
        cap = math.sqrt((0.22437 * (3.068 ** 5)) / (total_nps_sum * (1 + (3.6 / 3.068) + (0.03 * 3.068))))
        st.metric("Total 3\" NPS Length", f"{total_nps_sum:.2f} ft")
        st.metric("Capacity (MMSCFD/SQRT(psi))", f"{cap:.5f}")
    else:
        st.metric("Total 3\" NPS Length", "0.00 ft")
        st.metric("Capacity (MMSCFD/SQRT(psi))", "—")

with tab4: render_vent_tab("MAIN TANK VENT1")
with tab5: render_vent_tab("MAIN TANK VENT2")
with tab6: render_vent_tab("FlareVent")
