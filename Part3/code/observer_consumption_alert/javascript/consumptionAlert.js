class ConsumptionEvent {
  constructor(timeIndex, byLoad) {
    this.timeIndex = timeIndex;
    this.byLoad = Object.freeze({ ...byLoad });
    Object.freeze(this);
  }
}

class ConsumptionObserver {
  update(_event) {
    throw new Error("update must be implemented");
  }
}

class ConsumptionSubject {
  constructor() {
    this.observers = [];
  }

  subscribe(observer) {
    if (!(observer instanceof ConsumptionObserver)) {
      throw new TypeError("observer must implement ConsumptionObserver");
    }
    if (!this.observers.includes(observer)) this.observers.push(observer);
  }

  unsubscribe(observer) {
    const index = this.observers.indexOf(observer);
    if (index < 0) throw new Error("observer is not subscribed");
    this.observers.splice(index, 1);
  }

  notify(event) {
    for (const observer of [...this.observers]) observer.update(event);
  }
}

class ConsumptionAlertObserver extends ConsumptionObserver {
  constructor(threshold = 10.0) {
    super();
    this.alerts = [];
    this.setThreshold(threshold);
  }

  setThreshold(threshold) {
    if (threshold <= 0) throw new RangeError("threshold must be positive");
    this.threshold = threshold;
  }

  update(event) {
    for (const [loadId, consumption] of Object.entries(event.byLoad)) {
      if (consumption > this.threshold) {
        this.alerts.push(Object.freeze({
          timeIndex: event.timeIndex,
          loadId,
          consumption,
          threshold: this.threshold,
        }));
      }
    }
  }

  snapshot() {
    return this.alerts.map((alert) => ({ ...alert }));
  }
}

module.exports = {
  ConsumptionEvent,
  ConsumptionObserver,
  ConsumptionSubject,
  ConsumptionAlertObserver,
};
