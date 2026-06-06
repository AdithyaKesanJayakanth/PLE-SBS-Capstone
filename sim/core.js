/*
 * PLE-SBS simulation core — Pre-Launch Emergency: The Slidewire Basket System
 *
 * One file, no dependencies. Used by the web app (as a classic <script>, so it
 * also works when index.html is opened straight from disk) and by Node (tests,
 * figure export) through module.exports.
 *
 * Units are SI throughout (m, s, kg, N) unless a name says otherwise
 * (e.g. massT = tonnes, psi, kN, *_ft).
 *
 * Model map (paper section in brackets):
 *   1. hazard()          blast + fireball -> required safe distance       [Design 3.1]
 *   2. cable functions   taut-string sag under moving point loads         [Design 3.2]
 *   3. simulateWire()    pod dynamics along the cable, RK4                 [Design 3.3]
 *   4. evacuate()        people -> pods -> wires -> terminus -> safety     [Design 3.4]
 *   5. monteCarlo(), tradeStudy(), sensitivity(), fitScaleModel()          [Operate 5.x]
 */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.PLESBS = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const G = 9.80665;
  const LB_PER_KG = 2.20462;
  const FT_PER_M = 3.28084;

  // ---------------------------------------------------------------------------
  // 1. Hazard model
  // ---------------------------------------------------------------------------

  // TNT-equivalent mass (kg) for a mass of propellant that takes part in the event.
  // LOX/LH2 and LOX/RP-1 follow the DoD energetic-liquid rules quoted in [R5];
  // the others are stated assumptions (see docs/author-checklist.md).
  const PROPELLANTS = {
    LOX_LH2: {
      label: 'LOX / LH2 (cryogenic)',
      liquid: true,
      tnt: (kg) => {
        const lb = kg * LB_PER_KG;
        return Math.min(lb, Math.max(0.14 * lb, 8 * Math.pow(lb, 2 / 3))) / LB_PER_KG;
      },
      note: 'max(14% W, 8 W^(2/3)) with W in lb (DoD energetic-liquid rule)',
    },
    LOX_RP1: { label: 'LOX / RP-1 (kerosene)', liquid: true, tnt: (kg) => 0.10 * kg, note: '10% (DoD)' },
    LOX_CH4: { label: 'LOX / CH4 (methane)', liquid: true, tnt: (kg) => 0.20 * kg, note: '20% (assumed; no standard yet)' },
    HYPERGOLIC: { label: 'UDMH / N2O4 (hypergolic)', liquid: true, tnt: (kg) => 0.10 * kg, note: '10% (assumed)' },
    SOLID: { label: 'Solid (HTPB / PBAN)', liquid: false, tnt: (kg, opt) => (opt.solidTntFraction || 0) * kg, note: 'HD 1.3 mass-fire; blast fraction user-set (default 0)' },
  };

  // Launch-pad presets. accessHeight = crew access level above ground (where pods
  // start); span = horizontal length of the slidewire (the existing one, where a pad
  // has one); towerOffset = rocket centreline to tower; terminusHeight < 0 = landing pit.
  const PADS = {
    GENERIC_LOW: {
      label: 'Generic low-tower pad (42 m crew level)',
      site: { accessHeight: 42, span: 300, towerOffset: 15, brakeRunout: 15, terminusHeight: -3 },
    },
    LC39B_ARTEMIS: {
      label: 'KSC LC-39B, Artemis mobile launcher (114 m)',
      site: { accessHeight: 114, span: 393, towerOffset: 20, brakeRunout: 0, terminusHeight: 0 },
    },
    LC39A: {
      label: 'KSC LC-39A, crew access arm (81 m)',
      site: { accessHeight: 81, span: 355, towerOffset: 20, brakeRunout: 0, terminusHeight: 0 },
    },
    SLC41: {
      label: 'CCSFS SLC-41, crew access tower (52 m)',
      site: { accessHeight: 52, span: 405, towerOffset: 15, brakeRunout: 10, terminusHeight: 0 },
    },
    LC39B_SHUTTLE: {
      label: 'KSC LC-39B, Shuttle-era service structure (59 m)',
      site: { accessHeight: 59, span: 362, towerOffset: 20, brakeRunout: 5, terminusHeight: 0 },
    },
  };

  // Rocket presets. Propellant masses are rounded public figures. Each rocket names
  // the pad it normally flies from; any rocket can be put on any pad.
  const VEHICLES = {
    REF: {
      label: 'Reference medium-lift crewed launcher (generic)',
      stages: [
        { name: '2 × solid boosters', prop: 'SOLID', massT: 410 },
        { name: 'Hypergolic liquid core', prop: 'HYPERGOLIC', massT: 115 },
        { name: 'Cryogenic upper stage', prop: 'LOX_LH2', massT: 28 },
      ],
      pad: 'GENERIC_LOW',
      crew: 3,
    },
    SLS: {
      label: 'SLS Block 1 / Orion',
      stages: [
        { name: '2 × 5-segment SRB', prop: 'SOLID', massT: 1256 },
        { name: 'Core stage', prop: 'LOX_LH2', massT: 987 },
        { name: 'ICPS', prop: 'LOX_LH2', massT: 29 },
      ],
      pad: 'LC39B_ARTEMIS',
      crew: 4,
    },
    F9: {
      label: 'Falcon 9 / Crew Dragon',
      stages: [
        { name: 'First stage', prop: 'LOX_RP1', massT: 396 },
        { name: 'Second stage', prop: 'LOX_RP1', massT: 92 },
      ],
      pad: 'LC39A',
      crew: 4,
    },
    ATLAS: {
      label: 'Atlas V N22 / Starliner',
      stages: [
        { name: '2 × GEM/AJ-60A SRB', prop: 'SOLID', massT: 82 },
        { name: 'Atlas booster', prop: 'LOX_RP1', massT: 284 },
        { name: 'Dual-engine Centaur', prop: 'LOX_LH2', massT: 21 },
      ],
      pad: 'SLC41',
      crew: 4,
    },
    SHUTTLE: {
      label: 'Space Shuttle (historical)',
      stages: [
        { name: '2 × SRB', prop: 'SOLID', massT: 1000 },
        { name: 'External tank', prop: 'LOX_LH2', massT: 735 },
      ],
      pad: 'LC39B_SHUTTLE',
      crew: 7,
    },
  };

  for (const k in VEHICLES) VEHICLES[k].site = PADS[VEHICLES[k].pad].site;

  // Danger level: judgment-based scenario table (NOT from a standard; it is the
  // knob the user turns). f = fraction of propellant assumed to take part,
  // warn = time from alarm to the possible event, in seconds.
  const DANGER_LEVELS = {
    1: { label: 'Precautionary hold — off-nominal reading, vehicle stable', f: 0.25, warn: 600 },
    2: { label: 'Contained leak, no ignition', f: 0.5, warn: 300 },
    3: { label: 'Major leak / vapour cloud forming', f: 0.75, warn: 180 },
    4: { label: 'Fire on the pad or tank over-pressure', f: 1.0, warn: 120 },
    5: { label: 'Imminent failure — confirmed structural breach', f: 1.0, warn: 60 },
  };

  // Quantity-distance K-factors (ft/lb^(1/3)) and the side-on overpressure they imply [R5, R6].
  const K_FACTORS = {
    24: { psi: 2.3, label: 'K24 — 2.3 psi (public traffic route)' },
    40: { psi: 1.2, label: 'K40 — 1.2 psi (inhabited building)' },
    50: { psi: 0.9, label: 'K50 — 0.9 psi (personnel separation)' },
  };

  // Power law through the K24/K40/K50 points: p ≈ 1.2 (K/40)^-1.28 psi. Valid ~K15–K80.
  function overpressurePsi(K) { return 1.2 * Math.pow(K / 40, -1.28); }
  function kForPsi(psi) { return 40 * Math.pow(psi / 1.2, -1 / 1.28); }

  function hazard(cfg) {
    const level = DANGER_LEVELS[cfg.dangerLevel] || DANGER_LEVELS[4];
    const f = cfg.participation != null ? cfg.participation : level.f;
    let tntKg = 0, liquidKg = 0, solidKg = 0;
    const byStage = cfg.stages.map((s) => {
      const p = PROPELLANTS[s.prop];
      const kg = s.massT * 1000 * f;
      const t = p.tnt(kg, cfg);
      tntKg += t;
      if (p.liquid) liquidKg += kg; else solidKg += kg;
      return { name: s.name, prop: s.prop, kg, tntKg: t };
    });
    const tntLb = tntKg * LB_PER_KG;
    const rBlast = tntKg > 0 ? (cfg.kFactor * Math.cbrt(tntLb)) / FT_PER_M : 0;

    // Fireball from the liquid propellant (High, 1968 [R7]): D = 3.86 M^0.32, t = 0.299 M^0.32.
    const fbD = liquidKg > 0 ? 3.86 * Math.pow(liquidKg, 0.32) : 0;
    const fbT = liquidKg > 0 ? 0.299 * Math.pow(liquidKg, 0.32) : 0;
    // Thermal: q(r) = SEP (R_fb / r)^2 ; safe when dose q^(4/3) t <= doseLimit.
    const qLim = fbT > 0 ? Math.pow(cfg.thermalDoseLimit / fbT, 0.75) : Infinity; // kW/m^2
    const rThermal = fbD > 0 ? (fbD / 2) * Math.sqrt(cfg.sep / qLim) : 0;

    const rReq = Math.max(rBlast, rThermal);
    return {
      level, f, byStage, tntKg, liquidKg, solidKg,
      rBlast, fireballD: fbD, fireballT: fbT, qLimit: qLim, rThermal, rReq,
      governing: rThermal > rBlast ? 'thermal' : 'blast',
      warn: cfg.warnTime != null ? cfg.warnTime : level.warn,
      psiAt: (r) => (tntKg > 0 ? overpressurePsi((r * FT_PER_M) / Math.cbrt(tntLb)) : 0),
      rForPsi: (psi) => (kForPsi(psi) * Math.cbrt(tntLb)) / FT_PER_M,
    };
  }

  // ---------------------------------------------------------------------------
  // 2. Cable: counterweight-tensioned taut string (constant horizontal tension T)
  //    carrying its own weight w (N/m) and pods as point loads P_j at x_j.
  //    Deflection below the chord: δ(x) = [w x (L-x)/2 + Σ P_j G(x, x_j)] / T
  //    G(x,a) = x (L-a)/L for x<=a, a (L-x)/L for x>=a  (influence line).
  // ---------------------------------------------------------------------------

  function cableProps(cfg) {
    const d = cfg.cableDiameter; // mm
    const massPerM = 0.00426 * d * d; // kg/m, 6x36 IWRC steel rope (approx.)
    const mbs = 0.70 * d * d * 1000; // N, minimum breaking strength (EIPS approx.)
    return { massPerM, w: massPerM * G, mbs, allow: mbs / cfg.cableSF };
  }

  function makeWire(cfg) {
    const L = cfg.span;
    const H = cfg.accessHeight;
    const hb = cfg.terminusHeight;
    const cp = cableProps(cfg);
    return { L, H, hb, T: cfg.tension * 1000, w: cp.w, cable: cp, chord: (hb - H) / L };
  }

  function deflection(wire, x, loads) {
    const { L, T, w } = wire;
    let d = (w * x * (L - x)) / 2;
    for (const ld of loads) {
      const a = ld.x;
      d += ld.P * (x <= a ? (x * (L - a)) / L : (a * (L - x)) / L);
    }
    return d / T;
  }

  // dy/dx of the cable at x. `self` is the index of the load sitting at x (its kink
  // is averaged), or -1 for a point not under a pod.
  function slopeAt(wire, x, loads, self) {
    const { L, T, w } = wire;
    let dd = (w * (L - 2 * x)) / 2;
    for (let j = 0; j < loads.length; j++) {
      const a = loads[j].x;
      let g;
      if (j === self) g = (L - 2 * a) / (2 * L);
      else g = x < a ? (L - a) / L : -a / L;
      dd += loads[j].P * g;
    }
    return wire.chord - dd / T;
  }

  function heightAt(wire, x, loads) {
    return wire.H + wire.chord * x - deflection(wire, x, loads);
  }

  // Peak tension: T * sqrt(1 + max slope^2); the steepest point is one of the ends.
  function peakTension(wire, loads) {
    const s0 = slopeAt(wire, 0, loads, -1);
    const sL = slopeAt(wire, wire.L, loads, -1);
    const s = Math.max(Math.abs(s0), Math.abs(sL));
    return wire.T * Math.sqrt(1 + s * s);
  }

  // ---------------------------------------------------------------------------
  // 3. Pod dynamics on one wire (all pods on that wire integrated together,
  //    because each pod's weight changes the slope the others feel).
  //    m dv/dt = m g sinθ − μ m g cosθ − ½ ρ CdA (v − u cosθ)|v − u cosθ| − k_b v [brake zone]
  //    dx/dt = v cosθ
  // ---------------------------------------------------------------------------

  function podMass(cfg, nPeople, personMasses) {
    let m = cfg.podMass;
    if (personMasses) for (const pm of personMasses) m += pm;
    else m += nPeople * cfg.personMass;
    return m;
  }

  function podCdA(cfg, n) { return cfg.cdaPod + n * cfg.cdaPerson; }

  /**
   * pods: [{ depart, m, cda, n }] in dispatch order on this wire.
   * opts: { mu, wind (along-wire tailwind m/s), brakeK, rho, dt, sample, tMax }
   */
  function simulateWire(cfg, wire, pods, opts) {
    const o = Object.assign(
      { mu: cfg.mu, wind: cfg.wind, brakeK: cfg.brakeK, rho: cfg.rho, dt: cfg.dt, sample: 0.1, tMax: 600 },
      opts || {}
    );
    const L = wire.L;
    // eddy-current brake fins from xBrake to xBrakeEnd, then an unbraked run-out to the dock
    const xBrakeEnd = L - cfg.brakeRunout;
    const xBrake = xBrakeEnd - cfg.brakeLength;
    // with a switch yard the magnetic brake sits in each receiving bay, not on the wire
    const wireBrake = cfg.terminal !== 'switchyard';
    const n = pods.length;
    const st = pods.map((p) => ({
      x: 0, v: 0, active: false, done: false, stalled: false,
      arrive: null, vArr: null, vPeak: 0, aPeak: 0, minSep: Infinity,
      traj: { t: [], x: [], v: [] },
    }));

    // forces -> acceleration along the path for pod i, given current x of active pods
    function accel(i, xs, vs, loads, loadIndexOf) {
      const p = pods[i];
      const dydx = slopeAt(wire, xs[i], loads, loadIndexOf[i]);
      const c = 1 / Math.sqrt(1 + dydx * dydx); // cosθ
      const s = -dydx * c; // sinθ, positive downhill
      const v = vs[i];
      const vr = v - o.wind * c;
      let a = G * s - o.mu * G * c * (v >= 0 ? 1 : -1) - (0.5 * o.rho * p.cda * vr * Math.abs(vr)) / p.m;
      if (wireBrake && xs[i] >= xBrake && xs[i] < xBrakeEnd) a -= (o.brakeK * (p.brakeScale ?? 1) * v) / p.m;
      return { a, c };
    }

    function buildLoads(xs) {
      const loads = [], loadIndexOf = new Array(n).fill(-1);
      for (let j = 0; j < n; j++) {
        if (st[j].active && !st[j].done && !st[j].stalled) {
          loadIndexOf[j] = loads.length;
          loads.push({ x: xs[j], P: pods[j].m * G });
        }
      }
      return { loads, loadIndexOf };
    }

    function deriv(xs, vs) {
      const { loads, loadIndexOf } = buildLoads(xs);
      const dx = new Array(n).fill(0), dv = new Array(n).fill(0);
      for (let i = 0; i < n; i++) {
        if (loadIndexOf[i] < 0) continue;
        const { a, c } = accel(i, xs, vs, loads, loadIndexOf);
        dx[i] = vs[i] * c;
        dv[i] = a;
      }
      return { dx, dv };
    }

    let t = Math.min(...pods.map((p) => p.depart));
    const dt = o.dt;
    let nextSample = t;
    let peakT = 0;
    const tEnd = t + o.tMax;
    while (t < tEnd) {
      for (let i = 0; i < n; i++) {
        // block dispatch: the lever stays locked until the pod ahead passes the
        // block marker at blockX (or has arrived); a stalled pod ahead keeps it locked
        const b = pods[i].blockAfter;
        const blockClear = b == null || st[b].done || (st[b].active && !st[b].stalled && st[b].x >= pods[i].blockX);
        if (!st[i].active && t >= pods[i].depart && blockClear) {
          st[i].active = true;
          st[i].departT = t;
          st[i].x = 1e-6;
        }
      }
      if (st.every((s) => s.done || s.stalled)) break;
      if (st.every((s, i) => s.done || s.stalled || (!s.active && pods[i].blockAfter != null && st[pods[i].blockAfter].stalled))) break;

      const xs = st.map((s) => s.x), vs = st.map((s) => s.v);
      // RK4
      const k1 = deriv(xs, vs);
      const x2 = xs.map((x, i) => x + 0.5 * dt * k1.dx[i]), v2 = vs.map((v, i) => v + 0.5 * dt * k1.dv[i]);
      const k2 = deriv(x2, v2);
      const x3 = xs.map((x, i) => x + 0.5 * dt * k2.dx[i]), v3 = vs.map((v, i) => v + 0.5 * dt * k2.dv[i]);
      const k3 = deriv(x3, v3);
      const x4 = xs.map((x, i) => x + dt * k3.dx[i]), v4 = vs.map((v, i) => v + dt * k3.dv[i]);
      const k4 = deriv(x4, v4);

      const { loads } = buildLoads(xs);
      peakT = Math.max(peakT, peakTension(wire, loads));

      for (let i = 0; i < n; i++) {
        const s = st[i];
        if (!s.active || s.done || s.stalled) continue;
        const nx = xs[i] + (dt / 6) * (k1.dx[i] + 2 * k2.dx[i] + 2 * k3.dx[i] + k4.dx[i]);
        const nv = vs[i] + (dt / 6) * (k1.dv[i] + 2 * k2.dv[i] + 2 * k3.dv[i] + k4.dv[i]);
        const a = (nv - vs[i]) / dt;
        if (a < 0) s.aPeak = Math.max(s.aPeak, -a);
        s.vPeak = Math.max(s.vPeak, nv);
        if (nx >= L) {
          const frac = (L - xs[i]) / Math.max(nx - xs[i], 1e-9);
          s.arrive = t + frac * dt;
          s.vArr = vs[i] + frac * (nv - vs[i]);
          s.x = L; s.v = 0; s.done = true;
        } else if (nv < cfg.creepSpeed && t > (s.departT ?? pods[i].depart) + 5) {
          // creeping below creepSpeed short of the dock counts as a stall: the pod
          // would need to be hauled in by hand, which is not an evacuation
          s.x = nx; s.v = 0; s.stalled = true;
        } else {
          s.x = nx; s.v = Math.max(nv, 0);
        }
      }

      // spacing between consecutive pods on this wire (leader i-1 ahead of follower i)
      for (let i = 1; i < n; i++) {
        if (st[i].active && !st[i].done && st[i - 1].active && !st[i - 1].done) {
          st[i].minSep = Math.min(st[i].minSep, st[i - 1].x - st[i].x);
        }
      }

      t += dt;
      if (t >= nextSample) {
        for (let i = 0; i < n; i++) {
          const s = st[i];
          if (!s.active) continue;
          if (s.traj.t.length && s.traj.x[s.traj.x.length - 1] >= L && s.done) continue;
          s.traj.t.push(+t.toFixed(3));
          s.traj.x.push(s.x);
          s.traj.v.push(s.v);
        }
        nextSample += o.sample;
      }
    }

    const out = st.map((s, i) => ({
      depart: s.departT ?? pods[i].depart,
      held: !s.active,
      arrive: s.arrive,
      vArr: s.vArr,
      vPeak: s.vPeak,
      aPeakG: s.aPeak / G,
      impactG: s.vArr != null ? arrest(Object.assign({}, cfg, { brakeK: o.brakeK }), pods[i].m, s.vArr, pods[i].brakeScale).peakG : null,
      stalled: s.stalled,
      stallX: s.stalled ? s.x : null,
      minSep: s.minSep,
      traj: s.traj,
    }));
    out.peakTension = peakT;
    return out;
  }

  // Auto-size the eddy-current brake (k_b in N·s/m). Two passive-brake constraints:
  //   (a) a FULL pod should reach the dock no faster than dockSpeed;
  //   (b) the LIGHTEST pod we expect to dispatch must still reach the dock at
  //       >= 1 m/s (a linear eddy brake over-brakes light pods: decel = k v / m).
  // k_b = min(k_a, k_b). If (a) cannot be met, the terminal buffer takes the rest
  // and the evacuation flags the buffer deceleration.
  function designBrake(cfg) {
    if (cfg.terminal === 'switchyard') return designBayBrake(cfg);
    const wire = makeWire(cfg);
    const P = cfg.crew + cfg.ground;
    const nPods = Math.max(1, Math.ceil(P / cfg.podCapacity));
    const nLight = cfg.loading === 'balance' ? Math.max(1, Math.floor(P / nPods)) : Math.max(1, P - (nPods - 1) * cfg.podCapacity);
    const xBrake = wire.L - cfg.brakeRunout - cfg.brakeLength;
    // arrival speed, or -1 if the pod stalls or crawls below 1 m/s anywhere in the brake zone
    const arr = (k, n, wind) => {
      const pod = [{ depart: 0, m: podMass(cfg, n), cda: podCdA(cfg, n) }];
      const r = simulateWire(cfg, wire, pod, { brakeK: k, wind, sample: 0.25 })[0];
      if (r.stalled) return -1;
      for (let i = 0; i < r.traj.x.length; i++) if (r.traj.x[i] > xBrake + 5 && r.traj.x[i] < wire.L - 0.5 && r.traj.v[i] < 1) return -1;
      return r.vArr;
    };
    // largest k that satisfies "arrives at >= vMin" for occupancy n (monotone in k)
    const kMaxFor = (n, vMin, wind) => {
      let lo = 0, hi = 20000;
      if (arr(hi, n, wind) >= vMin) return hi;
      for (let it = 0; it < 24; it++) {
        const mid = 0.5 * (lo + hi);
        if (arr(mid, n, wind) >= vMin) lo = mid; else hi = mid;
      }
      return lo;
    };
    // design corners: the full pod with a tailwind (fastest case), the lightest pod
    // into a headwind (slowest case); designWind = 17.5 m/s (34 kn, Shuttle-era [R3])
    const kFull = kMaxFor(cfg.podCapacity, cfg.dockSpeed, cfg.designWind);
    const kLight = kMaxFor(nLight, 1.0, -cfg.designWind);
    return Math.round(Math.min(kFull, kLight));
  }

  // Bay brake (switch yard): pods reach the points unbraked. Size k_b so the lightest
  // pod arriving at the fastest speed (design tailwind) decelerates at <= aMax.
  function designBayBrake(cfg) {
    const wire = makeWire(cfg);
    const P = cfg.crew + cfg.ground;
    const nPods = Math.max(1, Math.ceil(P / cfg.podCapacity));
    const nLight = cfg.loading === 'balance' ? Math.max(1, Math.floor(P / nPods)) : Math.max(1, P - (nPods - 1) * cfg.podCapacity);
    const mL = podMass(cfg, nLight);
    const r = simulateWire(cfg, wire, [{ depart: 0, m: mL, cda: podCdA(cfg, nLight) }], { brakeK: 0, wind: cfg.designWind, sample: 5 })[0];
    if (!r.vArr) return 0;
    return Math.round((0.97 * cfg.aMaxG * G * mL) / r.vArr); // 3 % margin
  }

  return {
    G, PROPELLANTS, PADS, VEHICLES, DANGER_LEVELS, K_FACTORS,
    hazard, overpressurePsi, kForPsi,
    cableProps, makeWire, deflection, slopeAt, heightAt, peakTension,
    podMass, podCdA, simulateWire, designBrake,
  };
});
