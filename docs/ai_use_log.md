# AI-use log — PLE-SBS

Kept as required by `docs/ai_usage_policy.md`. "Checked by" names the verification actually performed (test, reference comparison, hand calculation, documentation lookup), not an intention. Dates are the repository's commit dates.

| Period | Tool | Task | Significant assistance received | Changes I made | Checked by |
|---|---|---|---|---|---|
| 2 June 2026 | AI coding assistant | Project set-up | Drafted the build scripts, the paper template and the data layout | Chose the single-physics-file structure so the paper and the website share one model; set the 7-page limit in the build | Build runs end to end; page-count check fails the build when exceeded |
| 4–10 June | AI coding assistant | Hazard model, cable model, pod dynamics | Drafted `sim/core.js` from my written specification of the TNT equivalence, cube-root blast scaling, High's fireball correlations, the taut-string influence line and the pod equation of motion; explained the eddy-current brake's velocity dependence | Decided the two-corner brake sizing, the danger levels and the requirements R1–R7; chose the thermal dose threshold between pain and first-degree burn | Unit tests against closed-form cases (√2gh arrival, incline time, terminal speed, wL²/8T and PL/4T sag); hand calculation of the reference launcher's TNT and blast distance |
| 8–13 June | AI coding assistant | Evacuation simulator and web interface | Drafted the dispatch logic, the headway bisection, the Monte Carlo loop and the browser interface | Set the human timings, the balanced-loading rule and the release-from-inside design; chose what the interface exposes | Time-step halving changes the total by 0.03 s; a stalled pod holds the one behind it; validation against the Shuttle-era basket speed with no tuning |
