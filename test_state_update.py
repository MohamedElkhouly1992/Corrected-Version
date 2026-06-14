from __future__ import annotations

import math
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hvac_v3_engine import (  # noqa: E402
    BuildingSpec,
    HVACConfig,
    advance_physics_degradation_state,
    apply_hvac_preset,
    apply_severity,
    degradation_index,
    simulate_combo,
)


def one_step_weather() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "step_of_year": 1,
                "day_of_year": 1,
                "hour_of_day": 0.0,
                "time_step_hours": 24.0,
                "T_mean_C": 30.0,
                "T_max_C": 35.0,
                "RH_mean_pct": 60.0,
                "GHI_mean_Wm2": 400.0,
                "weather_native_resolution": "unit_test",
            }
        ]
    )


def base_config() -> HVACConfig:
    cfg = HVACConfig(years=1, TIME_STEP_HOURS=24.0)
    cfg.APPLY_MONTHLY_COMPONENT_SEASONAL_CORRECTION = False
    cfg.APPLY_OPERATIONAL_STATE_LAYER_TO_CORE = False
    cfg.APPLY_DYNAMIC_RC_CORE_SOLVER = False
    cfg.APPLY_MONTHLY_HVAC_AVAILABILITY_TO_CORE = False
    cfg.APPLY_MONTHLY_MINIMUM_OPERATIONAL_LOAD_TO_CORE = False
    cfg.APPLY_SCHEDULE_BASED_FAN_TO_CORE = False
    cfg.APPLY_DEADBAND_FALLBACK_FIX_TO_CORE = False
    cfg.APPLY_SOFT_DEADBAND_ACTIVATION_TO_CORE = False
    return cfg


def test_one_step_without_maintenance_advances_once() -> None:
    cfg = base_config()
    cfg.RF_THRESH = 1e9
    cfg.DP_THRESH = 1e9
    cfg.DEG_TRIGGER = 1e9
    cfg.RF_WARN = 1e9
    cfg.DP_WARN = 1e9

    daily, _, _ = simulate_combo(
        strategy="S1",
        severity="Moderate",
        climate_name="C0_Baseline",
        bldg=BuildingSpec(conditioned_area_m2=500.0),
        base_cfg=cfg,
        base_weather=one_step_weather(),
        degradation_model="physics",
        random_state=7,
    )
    assert len(daily) == 1
    row = daily.iloc[0]

    applied = apply_hvac_preset(apply_severity(cfg, "Moderate"))
    expected_rf, expected_dust, expected_dp, expected_delta = advance_physics_degradation_state(
        applied, rf=0.0, dust=0.0, af=1.0, duration_hours=24.0
    )

    assert math.isclose(row["R_f"], expected_rf, rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(row["dust_kg"], expected_dust, rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(row["dP_Pa"], expected_dp, rel_tol=0.0, abs_tol=1e-9)
    assert math.isclose(row["delta"], expected_delta, rel_tol=0.0, abs_tol=1e-9)
    assert row["accepted_degradation_state_updates"] == 1
    assert row["state_update_consistency_flag"] == 1


def test_filter_maintenance_propagates_clean_filter_state() -> None:
    cfg = base_config()
    # S0 replaces the filter on day 1; HX maintenance is not scheduled on day 1.
    daily, _, _ = simulate_combo(
        strategy="S0",
        severity="Moderate",
        climate_name="C0_Baseline",
        bldg=BuildingSpec(conditioned_area_m2=500.0),
        base_cfg=cfg,
        base_weather=one_step_weather(),
        degradation_model="physics",
        random_state=7,
    )
    row = daily.iloc[0]
    assert row["filter_replaced"] == 1
    assert row["hx_cleaned"] == 0
    assert row["dust_pre_maintenance_kg"] > 0.0
    assert row["dust_post_maintenance_kg"] == 0.0
    assert row["dust_kg"] == 0.0
    assert math.isclose(row["dP_Pa"], cfg.DP_CLEAN, rel_tol=0.0, abs_tol=1e-9)
    expected_dp, expected_delta = degradation_index(
        apply_hvac_preset(apply_severity(cfg, "Moderate")),
        float(row["R_f"]),
        0.0,
    )
    assert math.isclose(row["dP_Pa"], expected_dp, rel_tol=0.0, abs_tol=1e-9)
    assert math.isclose(row["delta"], expected_delta, rel_tol=0.0, abs_tol=1e-9)
    assert row["state_update_consistency_flag"] == 1


def test_no_degradation_mode_has_zero_state_updates() -> None:
    cfg = base_config()
    daily, _, _ = simulate_combo(
        strategy="S1",
        severity="Moderate",
        climate_name="C0_Baseline",
        bldg=BuildingSpec(conditioned_area_m2=500.0),
        base_cfg=cfg,
        base_weather=one_step_weather(),
        degradation_model="none",
        random_state=7,
    )
    row = daily.iloc[0]
    assert row["R_f"] == 0.0
    assert row["dust_kg"] == 0.0
    assert row["delta"] == 0.0
    assert row["accepted_degradation_state_updates"] == 0
    assert row["state_update_consistency_flag"] == 1
