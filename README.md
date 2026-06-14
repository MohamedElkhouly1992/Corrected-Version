# HVAC v3 corrected deployment bundle

This bundle contains a drop-in corrected `hvac_v3_engine.py` and a compact Streamlit deployment interface.

## What was fixed

The former physics branch evaluated degradation before maintenance and then used the same state-advancing evaluator after maintenance. The corrected sequence is:

1. read the beginning-of-period state;
2. advance physical degradation once;
3. make the maintenance decision from the pre-maintenance state;
4. apply the maintenance reset;
5. evaluate energy, COP, comfort and carbon without advancing degradation;
6. propagate the same accepted post-maintenance state.

## Install and run

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
pytest -q
streamlit run streamlit_app.py
```

For a lighter installation without optional CatBoost/SHAP support:

```bash
pip install -r requirements-core.txt
```

## Validation

```bash
pytest -q tests/test_state_update.py
python run_smoke_test.py
```

The unit tests verify:

- one state advance when no maintenance occurs;
- consistent filter-reset propagation after maintenance;
- zero degradation in explicit no-degradation mode.

## New audit fields

The timestep CSV contains start, pre-maintenance, and post-maintenance state fields plus:

- `accepted_degradation_state_updates`
- `state_update_consistency_flag`

For a correct physics run, the first field is `1` and the second should remain `1` for every row.

## Deployment note

The included Streamlit interface is a compact deployment shell built around the corrected engine. If you have a larger custom project UI, replace its old engine file with this corrected `hvac_v3_engine.py` and retain the existing UI.

## Delivered manuscript support

The `docs/` folder contains the complete nomenclature table, equation-to-reference map, and APA 7th edition reference list. The reference map distinguishes literature-supported equation families from empirical model coefficients that require calibration rather than citation as universal constants.

## Verified bundle status

This release was checked using Python compilation, three state-update regression tests, and an end-to-end smoke run. Passing these checks confirms the corrected execution path runs and exports results; it does not replace external validation of the HVAC physics or calibration coefficients.
