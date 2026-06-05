// Physics sanity checks for sim/core.js.  Run: node --test test/
const test = require('node:test');
const assert = require('node:assert/strict');
const S = require('../sim/core.js');

const close = (a, b, tol, msg) => assert.ok(Math.abs(a - b) <= tol, `${msg}: ${a} vs ${b} (tol ${tol})`);

// A rigid straight wire: enormous tension removes sag from the cable and the pods.
function straight(over) {
  const cfg = S.resolve(Object.assign({
    accessHeight: 50, terminusHeight: 0, span: 300, tension: 1e9,
    mu: 0, cdaPod: 0, cdaPerson: 0, brakeK: 0, brakeLength: 0, brakeRunout: 0, dt: 0.005,
  }, over));
  return { cfg, wire: S.makeWire(cfg) };
}

test('taut string: point load P at midspan deflects P L / (4 T)', () => {
  const wire = { L: 400, H: 40, hb: 0, T: 100e3, w: 0, chord: -0.1 };
  close(S.deflection(wire, 200, [{ x: 200, P: 5000 }]), (5000 * 400) / (4 * 100e3), 1e-9, 'midspan deflection');
});

test('taut string: self-weight sag is w L^2 / (8 T)', () => {
  const wire = { L: 400, H: 40, hb: 0, T: 100e3, w: 40, chord: -0.1 };
  close(S.deflection(wire, 200, []), (40 * 400 * 400) / (8 * 100e3), 1e-9, 'midspan sag');
});
