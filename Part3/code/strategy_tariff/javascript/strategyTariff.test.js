const assert = require("node:assert/strict");
const {
  FlatTariff,
  TimeOfUseTariff,
  DynamicTariff,
  TariffContext,
} = require("./strategyTariff");

function assertPrice(actual, expected, caseId) {
  assert.ok(Math.abs(actual - expected) <= 1e-9, `${caseId}: expected ${expected}, got ${actual}`);
}

const context = new TariffContext(new FlatTariff(0.15));
const cases = [
  ["DT01", new FlatTariff(0.15), 0, 0.15],
  ["DT02", new FlatTariff(0.15), 23, 0.15],
  ["DT03", new TimeOfUseTariff(0.30, 0.15, 18, 22), 17, 0.15],
  ["DT04", new TimeOfUseTariff(0.30, 0.15, 18, 22), 18, 0.30],
  ["DT05", new TimeOfUseTariff(0.30, 0.15, 18, 22), 21, 0.30],
  ["DT06", new TimeOfUseTariff(0.30, 0.15, 18, 22), 22, 0.15],
  ["DT07", new TimeOfUseTariff(0.30, 0.15, 18, 22), 42, 0.30],
  ["DT08", new DynamicTariff([0.10, 0.20, 0.35, 0.15]), 0, 0.10],
  ["DT09", new DynamicTariff([0.10, 0.20, 0.35, 0.15]), 2, 0.35],
  ["DT10", new DynamicTariff([0.10, 0.20, 0.35, 0.15]), 4, 0.10],
];

for (const [caseId, strategy, timeIndex, expected] of cases) {
  context.setStrategy(strategy);
  assertPrice(context.getPrice(timeIndex), expected, caseId);
}

const invalidCases = [
  () => new FlatTariff(-0.01),
  () => new TimeOfUseTariff(-0.01, 0.10),
  () => new TimeOfUseTariff(0.30, 0.15, 22, 18),
  () => new DynamicTariff([]),
  () => new DynamicTariff([0.10, -0.20]),
  () => new TimeOfUseTariff(0.30, 0.15).getPrice(-1),
  () => new DynamicTariff([0.10]).getPrice(-1),
];
for (const action of invalidCases) assert.throws(action);

console.log(`Strategy tests: ${cases.length + invalidCases.length}/${cases.length + invalidCases.length} passed`);
