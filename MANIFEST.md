# Bundle manifest

## Runtime files
- `streamlit_app.py`: compact deployment UI
- `hvac_v3_engine.py`: corrected simulation engine
- `requirements.txt`: full dependencies including CatBoost/SHAP
- `requirements-core.txt`: lighter dependencies
- `.streamlit/config.toml`: Streamlit theme/server settings
- `Procfile`, `runtime.txt`: common cloud deployment helpers

## Verification
- `tests/test_state_update.py`: regression tests for the corrected state transition
- `run_smoke_test.py`: end-to-end export smoke test
- `STATE_UPDATE_FIX.patch`: unified diff against the uploaded engine

## Documentation
- `README.md`, `CHANGELOG.md`
- `docs/Nomenclature_and_Equation_References.docx`
- `docs/Nomenclature_and_Equation_References.pdf`
- `docs/APA_Equation_References.txt`
- `docs/Corrected_Q1_Methodology_Equations.docx` when available

## Backup
- `hvac_v3_engine_original_backup.py`: unchanged uploaded engine
