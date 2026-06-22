# AI Usage and Research Ownership — PLE-SBS

*Author: Adithya Kesan Jayakanth. Statement of policy, 1 June 2026, extended 22 June 2026 for the poster and the printed model.*

My goal in PLE-SBS is to develop my understanding of pad-safety engineering, physical modelling and simulation, and the judgment to design, run and revise a system. I use AI as a tutor, programming assistant and critical reviewer, while retaining responsibility for the requirements, the design decisions and the conclusions.

Before asking AI to implement a task, I write down the physical purpose, the assumptions, the intended algorithm and the expected behaviour. I first attempt the parts central to my learning: the hazard model (TNT equivalence, blast scaling, fireball dose), the taut-string model of the wire with coupled pod loads, the pod equation of motion and the two-corner brake sizing, the dispatch and headway rules, and the switch-yard concept.

I may use AI to explain unfamiliar concepts, suggest debugging approaches, draft routine code, improve code organisation, generate figures from result files, and review my writing. When learning a new concept, I ask for explanations and hints, then work through the reasoning independently.

I review and test AI-assisted code before accepting it. For code that affects the hazard distances, the wire profile, the pod dynamics, the brake sizing, the Monte Carlo and the evacuation times, I am able to explain its logic, modify it and identify how an error could affect the conclusions.

I verify technical claims against primary sources: NASA technical reports and press material for the Shuttle and Artemis systems, DoD and HSE documents for the explosion and thermal criteria, and handbook data for materials. Numerical results are checked by unit tests against closed-form cases, a time-step convergence check, and validation against the reported performance of real systems. AI-generated explanations or tests alone do not establish that a model is correct.

I make and document the final choices about the requirements, the danger levels, the design iterations, the sizing rule and the interpretation of results. AI may suggest possibilities or challenge an explanation; I decide what the evidence supports. I preserve failed designs (D0 to D3 in the paper) and findings that contradict my expectations, such as the design failing the level-4 window because of human timings.

My AI-use log records the tool, the task, the significant assistance, the changes I made and how I checked the output. I also distinguish my own code from external libraries and tools.

The measure of successful AI use is whether I can explain, reproduce and defend the work independently. My disclosure describes the assistance actually used and follows the requirements of each submission venue.

---

## AI-use log

Maintained by the author in `docs/ai_use_log.md` with one row per task, as the policy above requires (tool, task, significant assistance, changes made by the author, how the output was checked).

## Code provenance

| Component | Origin |
|---|---|
| `sim/core.js` (hazard model, cable, pod dynamics, evacuation, Monte Carlo, trade studies, sensitivity, scale-model fit) and `sim/export.js` | Project code, in this repository, dependency-free |
| `web/` (simulator interface) | Project code |
| `test/core.test.js` | Project code; 16 unit tests run with the Node test runner |
| `figures/make_figures.py`, `poster/make_poster_figs.py`, `scale_down/make_drawings.py`, `scale_down/make_renders.py` | Project code using matplotlib, NumPy and trimesh |
| `cad/make_parts.py`, `scale_down/make_parts.py` | Project code using manifold3d and trimesh to build watertight STL files |
| Node.js 18+, Python 3, pandoc, Google Chrome (headless), tectonic with the tikzposter class | External tools used to run tests, build the paper and the poster |
| Reference data cited in the paper (NASA NTRS reports, Spaceflight Now, DoD 6055.09, HSE HSL/2004/04, Lihou and Maund 1982, wire-rope and material handbooks) | Public sources, cited in the paper's reference list |
