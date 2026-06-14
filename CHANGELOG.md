# Changelog

## Revision `state_update_fix_2026-06-12`

- Separated physics degradation advancement from energy/comfort evaluation.
- Enforced exactly one accepted degradation-state transition per time step.
- Re-evaluated post-maintenance performance with `advance_degradation=False`.
- Propagated the same post-maintenance state used for reported pressure drop, degradation, COP, energy, comfort, and carbon.
- Added pre-maintenance, post-maintenance, and consistency-audit output columns.
- Corrected explicit `degradation_model="none"` runs so the composite indicator remains zero.
- Added three regression tests and a complete one-strategy smoke test.

This revision changes numerical results. Regenerate the full scenario matrix and every manuscript result derived from it.
