from __future__ import annotations

import io
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import streamlit as st

from hvac_v3_engine import (
    BuildingSpec,
    CLIMATE_LEVELS,
    HVACConfig,
    HVAC_PRESETS,
    SCENARIOS,
    SEVERITY_LEVELS,
    run_scenario_model,
)

st.set_page_config(page_title="HVAC ROM — Corrected State Update", layout="wide")
st.markdown(
    """
    <style>
    .stApp {background: #101419; color: #e8edf2;}
    [data-testid="stHeader"] {background: rgba(16,20,25,0.95);}
    .block-container {padding-top: 1.2rem; max-width: 1500px;}
    .hero {padding: 1.1rem 1.3rem; border: 1px solid #303842; border-radius: 14px;
           background: linear-gradient(135deg,#171d24,#11161c); margin-bottom: 1rem;}
    .ok {padding: .75rem 1rem; border-left: 4px solid #2ca58d; background:#15221f; border-radius:8px;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h2>Reduced-Order HVAC Degradation Framework</h2>
      <div>Corrected engine: one accepted degradation-state transition per simulation time step.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

run_tab, setup_tab, audit_tab = st.tabs(["Run model", "Setup", "State-update audit"])

with setup_tab:
    st.subheader("Building and HVAC configuration")
    c1, c2, c3 = st.columns(3)
    with c1:
        area = st.number_input("Conditioned area (m²)", 50.0, 500000.0, 5000.0, 100.0)
        floors = st.number_input("Floors", 1, 100, 4)
        spaces = st.number_input("Spaces/zones", 1, 5000, 40)
        occ_density = st.number_input("Occupancy density (person/m²)", 0.0, 2.0, 0.08, 0.01)
    with c2:
        lighting = st.number_input("Lighting (W/m²)", 0.0, 100.0, 10.0, 0.5)
        equipment = st.number_input("Equipment (W/m²)", 0.0, 200.0, 8.0, 0.5)
        airflow = st.number_input("Airflow (m³/h·m²)", 0.1, 50.0, 4.0, 0.1)
        infiltration = st.number_input("Infiltration (ACH)", 0.0, 10.0, 0.5, 0.1)
    with c3:
        hvac_type = st.selectbox("HVAC system", list(HVAC_PRESETS.keys()), index=0)
        years = st.number_input("Simulation years", 1, 50, 1)
        timestep = st.selectbox("Time step", [24.0, 12.0, 6.0, 3.0, 1.0], index=0, format_func=lambda x: f"{x:g} h")
        energy_price = st.number_input("Electricity price (USD/kWh)", 0.0, 5.0, 0.12, 0.01)

    st.caption("The deployment defaults retain the current research calibration modules. Disable them in code for ablation studies.")

with run_tab:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        axis_mode = st.selectbox(
            "Analysis mode",
            ["one_strategy", "one_severity", "two_axis", "three_axis", "baseline_scenario"],
            index=0,
        )
    with c2:
        fixed_strategy = st.selectbox("Fixed strategy", list(SCENARIOS.keys()), index=3)
    with c3:
        fixed_severity = st.selectbox("Fixed severity", list(SEVERITY_LEVELS.keys()), index=1)
    with c4:
        fixed_climate = st.selectbox("Fixed climate", list(CLIMATE_LEVELS.keys()), index=0)

    weather_upload = st.file_uploader("Optional weather file (CSV or EPW)", type=["csv", "txt", "epw"])
    c5, c6, c7 = st.columns(3)
    with c5:
        include_baseline = st.checkbox("Include no-degradation baseline layer", value=True)
    with c6:
        memory_safe = st.checkbox("Memory-safe export", value=True)
    with c7:
        reports = st.checkbox("Generate Excel and PDF reports", value=True)

    if st.button("Run corrected model", type="primary", use_container_width=True):
        bldg = BuildingSpec(
            conditioned_area_m2=float(area),
            floors=int(floors),
            n_spaces=int(spaces),
            occupancy_density_p_m2=float(occ_density),
            lighting_w_m2=float(lighting),
            equipment_w_m2=float(equipment),
            airflow_m3h_m2=float(airflow),
            infiltration_ach=float(infiltration),
        )
        cfg = HVACConfig(
            years=int(years),
            hvac_system_type=hvac_type,
            TIME_STEP_HOURS=float(timestep),
            E_PRICE=float(energy_price),
        )

        with st.spinner("Running the scenario matrix..."):
            tmpdir = Path(tempfile.mkdtemp(prefix="hvac_v3_corrected_"))
            weather_mode = "synthetic"
            epw_path = None
            csv_path = None
            if weather_upload is not None:
                uploaded_path = tmpdir / weather_upload.name
                uploaded_path.write_bytes(weather_upload.getvalue())
                if uploaded_path.suffix.lower() == ".epw":
                    weather_mode, epw_path = "epw", str(uploaded_path)
                else:
                    weather_mode, csv_path = "csv", str(uploaded_path)

            outputs = run_scenario_model(
                output_dir=tmpdir,
                axis_mode=axis_mode,
                bldg=bldg,
                cfg=cfg,
                weather_mode=weather_mode,
                epw_path=epw_path,
                csv_path=csv_path,
                fixed_strategy=fixed_strategy,
                fixed_severity=fixed_severity,
                fixed_climate=fixed_climate,
                include_baseline_layer=include_baseline,
                degradation_model="physics",
                time_step_hours=float(timestep),
                memory_safe_mode=memory_safe,
                generate_figures=True,
                generate_excel_report=reports,
                generate_pdf_report=reports,
            )

            summary_path = Path(outputs["summary_csv"])
            summary_df = pd.read_csv(summary_path) if summary_path.exists() else pd.DataFrame()
            st.session_state["latest_summary"] = summary_df

            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for file in tmpdir.rglob("*"):
                    if file.is_file():
                        zf.write(file, file.relative_to(tmpdir))
            st.session_state["latest_zip"] = buffer.getvalue()

        st.success("Corrected simulation completed.")

    if "latest_summary" in st.session_state:
        st.dataframe(st.session_state["latest_summary"], use_container_width=True)
    if "latest_zip" in st.session_state:
        st.download_button(
            "Download complete result package",
            data=st.session_state["latest_zip"],
            file_name="hvac_v3_corrected_results.zip",
            mime="application/zip",
            use_container_width=True,
        )

with audit_tab:
    st.markdown(
        """
        <div class="ok"><b>Corrected sequence</b><br>
        Start-of-step state → one physical degradation update → maintenance decision → maintenance restoration →
        state-static energy/comfort evaluation → propagate the same accepted state.</div>
        """,
        unsafe_allow_html=True,
    )
    st.write("New audit columns exported for every time step:")
    st.code(
        "R_f_start, dust_start_kg, delta_start\n"
        "R_f_pre_maintenance, dust_pre_maintenance_kg, dP_pre_maintenance_Pa, delta_pre_maintenance\n"
        "R_f_post_maintenance, dust_post_maintenance_kg, dP_post_maintenance_Pa, delta_post_maintenance\n"
        "accepted_degradation_state_updates, state_update_consistency_flag"
    )
    st.warning("All manuscript tables and savings claims must be regenerated with this engine revision.")
