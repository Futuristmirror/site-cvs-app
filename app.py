import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Closed Vent System Calculator", layout="wide")
st.title("Closed Vent System Assessment Tool")

# Setup Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🛢 Tank Layout", "🌊 Main Process", "➕ Add to Main Process", "🌬 MAIN TANK VENT 1", "🌬 MAIN TANK VENT 2", "🔥 FLARE VENT"])

# Shared logic block (used in all three vent tabs)
def render_vent_tab(label_prefix):
    st.subheader("Summary")
    summary_lengths = []

    col_sets = st.columns(8)
    id_configs = [
        {"label": '1.5"', "id_in": 1.338},
        {"label": '2"', "id_in": 2.067},
        {"label": '3"', "id_in": 3.068},
        {"label": '4"', "id_in": 4.026},
        {"label": '6"', "id_in": 6.070},
        {"label": '8"', "id_in": 7.981},
        {"label": '10"', "id_in": 10.020},
        {"label": '12"', "id_in": 11.938},
    ]

    for config, col in zip(id_configs, col_sets):
        with col:
            label = config["label"]
            ID_in = config["id_in"]

            st.markdown(f"### {label_prefix} {label} Pipe")
            st.markdown("<div style='background-color:#f0f0f0; padding: 4px; border-radius: 6px'><b>Developed Length</b></div>", unsafe_allow_html=True)
            developed_length = st.number_input(f"{label_prefix} {label} Developed Length (ft)", min_value=0.0, value=0.0, step=1.0, key=f"dev_{label_prefix}_{label}")

            st.markdown("---")
            def fitting_input(tag, multiplier):
                qty = st.number_input(f"{label_prefix} {label} {tag} (qty)", min_value=0, value=0, step=1, key=f"{tag}_{label_prefix}_{label}")
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

            st.markdown("<hr style='margin-top: 20px; margin-bottom: 6px'>", unsafe_allow_html=True)
            st.markdown(f"**{label_prefix} {label} Knockouts / Expansions**")
            def knockout_le(diam):
                if diam == 0:
                    return 0.0
                if diam > ID_in:
                    return (1 / 12) * ID_in * ((1 - ((ID_in**2) / (diam**2))) ** 2)
                else:
                    return (1 / 12) * ID_in * 0.5 * (1 - ((diam**2) / (ID_in**2)))

            knockout_le_total = 0
            for i in range(3):
                d = st.number_input(f"{label_prefix} {label} Knockout {i+1} Diameter (in)", min_value=0.0, value=0.0, key=f"kdiam{i}_{label_prefix}_{label}")
                knockout_le_total += knockout_le(d)

            st.markdown("<hr style='margin-top: 20px; margin-bottom: 6px'>", unsafe_allow_html=True)
            st.markdown(f"**{label_prefix} {label} Specialty Valves / Components**")
            def specialty_valve_le(cv):
                if cv == 0:
                    return 0.0
                numerator = 100 * 891 * (ID_in ** 5)
                denominator = (12 * (1 + (3.6 / ID_in) + 0.03 * ID_in)) * (cv ** 2)
                return numerator / denominator

            specialty_le_total = 0
            for i in range(3):
                cv = st.number_input(f"{label_prefix} {label} Specialty Valve {i+1} Cv", min_value=0.0, value=0.0, key=f"cv{i}_{label_prefix}_{label}")
                specialty_le_total += specialty_valve_le(cv)

            total_pipe = developed_length + total_le_fittings + knockout_le_total + specialty_le_total

            numerator = total_pipe * (1 + (3.6 / ID_in) + (0.03 * ID_in)) * (3.068 ** 5)
            denominator = (ID_in ** 5) * (1 + (3.6 / 3.068) + (0.03 * 3.068))
            total_pipe_nps = numerator / denominator

            summary_lengths.append(total_pipe_nps if total_pipe_nps > 0 else 0.0)

            st.metric(f"{label_prefix} {label} Total Header Length (ft)", f"{total_pipe:.2f}")
            st.metric(f"{label_prefix} {label} Total Length (ft) of 3\" NPS", f"{total_pipe_nps:.2f}")

    total_nps_sum = sum(summary_lengths)
    if total_nps_sum == 0:
        capacity = ""
    else:
        capacity = math.sqrt((0.22437 * (3.068 ** 5)) / (total_nps_sum * (1 + (3.6 / 3.068) + (0.03 * 3.068))))

    st.subheader("Overall System Summary")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Total Length (ft) of 3\" NPS", f"{total_nps_sum:.2f}")
    with c2:
        st.metric("Capacity (MMSCFD/SQRT(psi))", f"{capacity:.5f}" if capacity else "")

# Call render function in each new tab
with tab4:
    render_vent_tab("MAIN TANK VENT 1")

with tab5:
    render_vent_tab("MAIN TANK VENT 2")

with tab6:
    render_vent_tab("FLARE VENT")

