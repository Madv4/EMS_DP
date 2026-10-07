const assert = require("node:assert/strict");
const {
  ConsumptionEvent,
  ConsumptionSubject,
  ConsumptionAlertObserver,
} = require("./consumptionAlert");

function runCase(caseId, threshold, timeIndex, loadId, gridDraw, renewableDraw, expectedCount, expectedConsumption) {
  const subject = new ConsumptionSubject();
  const observer = new ConsumptionAlertObserver(threshold);
  subject.subscribe(observer);
  const consumption = gridDraw + renewableDraw;
  assert.ok(Math.abs(consumption - expectedConsumption) <= 1e-9, `${caseId}: consumption mismatch`);
  subject.notify(new ConsumptionEvent(timeIndex, { [loadId]: consumption }));
  assert.equal(observer.alerts.length, expectedCount, `${caseId}: alert count mismatch`);
  if (observer.alerts.length > 0) {
    assert.ok(Math.abs(observer.alerts[0].consumption - expectedConsumption) <= 1e-9);
  }
}

const cases = [
  ["CA01", 10.0, 0, "load-a", 5.0, 0.0, 0, 5.0],
  ["CA02", 10.0, 1, "load-a", 7.0, 5.0, 1, 12.0],
  ["CA03", 10.0, 2, "load-a", 10.0, 0.0, 0, 10.0],
  ["CA04", 0.05, 3, "load-b", 0.04, 0.02, 1, 0.06],
  ["CA05", 20.0, 4, "load-c", 12.0, 9.0, 1, 21.0],
];
for (const testCase of cases) runCase(...testCase);

const subject = new ConsumptionSubject();
const observer = new ConsumptionAlertObserver(10.0);
subject.subscribe(observer);
subject.subscribe(observer);
subject.notify(new ConsumptionEvent(5, { "load-a": 11.0 }));
assert.equal(observer.alerts.length, 1, "duplicate subscription must not duplicate alerts");

subject.unsubscribe(observer);
subject.notify(new ConsumptionEvent(6, { "load-a": 12.0 }));
assert.equal(observer.alerts.length, 1, "unsubscribed observer must not receive events");

const multi = new ConsumptionAlertObserver(10.0);
subject.subscribe(multi);
subject.notify(new ConsumptionEvent(7, { "load-a": 11.0, "load-b": 10.0, "load-c": 12.0 }));
assert.deepEqual(multi.alerts.map((alert) => alert.loadId), ["load-a", "load-c"]);

assert.throws(() => new ConsumptionAlertObserver(0.0));
assert.throws(() => new ConsumptionAlertObserver(-1.0));

const total = cases.length + 5;
console.log(`Observer tests: ${total}/${total} passed`);
