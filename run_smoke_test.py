from __future__ import annotations

import tempfile
from pathlib import Path

from hvac_v3_engine import BuildingSpec, HVACConfig, run_scenario_model


def main() -> None:
    cfg = HVACConfig(years=1, TIME_STEP_HOURS=24.0, APO_POP=8, APO_ITERS=3)
    bldg = BuildingSpec(conditioned_area_m2=1000.0, floors=2, n_spaces=10)
    with tempfile.TemporaryDirectory(prefix="hvac_v3_smoke_") as tmp:
        outputs = run_scenario_model(
            output_dir=tmp,
            axis_mode="one_strategy",
            bldg=bldg,
            cfg=cfg,
            fixed_severity="Moderate",
            fixed_climate="C0_Baseline",
            include_baseline_layer=False,
            degradation_model="physics",
            time_step_hours=24.0,
            memory_safe_mode=True,
            generate_figures=False,
            generate_excel_report=False,
            generate_pdf_report=False,
        )
        summary = Path(tmp) / "one_axis_strategy_summary.csv"
        if not summary.exists():
            raise RuntimeError(f"Smoke test failed; summary not created. Returned: {outputs}")
        print(f"Smoke test passed: {summary}")


if __name__ == "__main__":
    main()
