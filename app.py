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
    st.header('🌬 MAIN TANK VENT HEADER1 (3" and 4")')

    header_configs = [
        {"label": '3"', "id_in": 3.068},
        {"label": '4"', "id_in": 4.026}
    ]

    for config in header_configs:
        label = config["label"]
        ID_in = config["id_in"]

        st.subheader(f"{label} Pipe Fittings")
        developed_length = st.number_input(f"{label} Developed Length (ft)", min_value=0.0, value=0.0, step=1.0, key=f"dev_{label}")

        def fitting_input(tag, multiplier):
            qty = st.number_input(f"{label} {tag} (qty)", min_value=0, value=0, step=1, key=f"{tag}_{label}")
            return qty * (1 / 12) * ID_in * multiplier

        fittings = [
            ("Tee, Flow thru run", 20),
            ("Tee, Flow thru branch", 60),
            ("Elbow, 90° Threaded", 30),
            ("Elbow, 45° Threaded", 16),
            ("Elbow, 90° (R/D ~3)", 14),
            ("Elbow, 45° (R/D ~3)", 9.9),
            ("Gate Valve", 8),
            ("Globe Valve", 340),
            ("Ball Valve", 3),
            ("Butterfly Valve", 45),
            ("Check Valve", 100),
            ("Entrance / Exit", 1)
        ]
        total_le_fittings = sum(fitting_input(name, mult) for name, mult in fittings)

        # Knockouts
        st.markdown(f"**{label} Knockouts / Expansions**")
        def knockout_le(diam):
            if diam == 0:
                return 0.0
            if diam > ID_in:
                return (1 / 12) * ID_in * ((1 - ((ID_in**2) / (diam**2))) ** 2)
            else:
                return (1 / 12) * ID_in * 0.5 * (1 - ((diam**2) / (ID_in**2)))

        knockout_le_total = 0
        for i in range(3):
            d = st.number_input(f"{label} Knockout {i+1} Diameter (in)", min_value=0.0, value=0.0, key=f"kdiam{i}_{label}")
            knockout_le_total += knockout_le(d)

        # Specialty Valves
        st.markdown(f"**{label} Specialty Valves / Components**")
        def specialty_valve_le(cv):
            if cv == 0:
                return 0.0
            numerator = 100 * 891 * (ID_in ** 5)
            denominator = (12 * (1 + (3.6 / ID_in) + 0.03 * ID_in)) * (cv ** 2)
            return numerator / denominator

        specialty_le_total = 0
        for i in range(3):
            cv = st.number_input(f"{label} Specialty Valve {i+1} Cv", min_value=0.0, value=0.0, key=f"cv{i}_{label}")
            specialty_le_total += specialty_valve_le(cv)

        # Final Summary
        st.markdown(f"**{label} Total Equivalent Length Summary**")
        total_pipe = developed_length + total_le_fittings + knockout_le_total + specialty_le_total

        numerator = total_pipe * (1 + (3.6 / ID_in) + (0.03 * ID_in)) * (3.068 ** 5)
        denominator = (ID_in ** 5) * (1 + (3.6 / 3.068) + (0.03 * 3.068))
        total_pipe_nps = numerator / denominator

        st.metric(f"{label} Total Length of Header (ft)", f"{total_pipe:.2f}")
        st.metric(f"{label} Total Length (ft) of 3\" NPS", f"{total_pipe_nps:.2f}")

        # Footer calculator
        st.markdown("**Spitzglass & Friction Calculator**")
        eD = 12 * 0.00015 / ID_in
        turb_factor = 0.25 / (math.log10(eD / 3.7) ** 2)
        spitz_factor = (1 + 3.6 / ID_in + 0.03 * ID_in) / 100
        ratio = turb_factor / spitz_factor

        col1, col2 = st.columns(2)
        with col1:
            st.metric(f"{label} ε/D", f"{eD:.5f}")
            st.metric(f"{label} Turb Friction Factor fr", f"{turb_factor:.4f}")
        with col2:
            st.metric(f"{label} Spitzglass ƒspzz", f"{spitz_factor:.5f}")
            st.metric(f"{label} Ratio (fr / ƒspzz)", f"{ratio:.4f}")

