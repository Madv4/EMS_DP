class TariffStrategy {
  getPrice(_timeIndex) {
    throw new Error("getPrice must be implemented");
  }
}

class FlatTariff extends TariffStrategy {
  constructor(price) {
    super();
    if (price < 0) throw new RangeError("price must be non-negative");
    this.price = price;
  }

  getPrice(_timeIndex) {
    return this.price;
  }
}

class TimeOfUseTariff extends TariffStrategy {
  constructor(peakPrice, offPeakPrice, peakStart = 18, peakEnd = 22) {
    super();
    if (Math.min(peakPrice, offPeakPrice) < 0) {
      throw new RangeError("prices must be non-negative");
    }
    if (!(0 <= peakStart && peakStart < peakEnd && peakEnd <= 24)) {
      throw new RangeError("peak window must fall within a day");
    }
    this.peakPrice = peakPrice;
    this.offPeakPrice = offPeakPrice;
    this.peakStart = peakStart;
    this.peakEnd = peakEnd;
  }

  getPrice(timeIndex) {
    if (timeIndex < 0) throw new RangeError("timeIndex must be non-negative");
    const hour = timeIndex % 24;
    return this.peakStart <= hour && hour < this.peakEnd
      ? this.peakPrice
      : this.offPeakPrice;
  }
}

class DynamicTariff extends TariffStrategy {
  constructor(prices) {
    super();
    if (!Array.isArray(prices) || prices.length === 0 || prices.some((price) => price < 0)) {
      throw new RangeError("prices must be a non-empty, non-negative series");
    }
    this.prices = [...prices];
  }

  getPrice(timeIndex) {
    if (timeIndex < 0) throw new RangeError("timeIndex must be non-negative");
    return this.prices[timeIndex % this.prices.length];
  }
}

class TariffContext {
  constructor(strategy) {
    this.setStrategy(strategy);
  }

  setStrategy(strategy) {
    if (!(strategy instanceof TariffStrategy)) {
      throw new TypeError("strategy must implement TariffStrategy");
    }
    this.strategy = strategy;
  }

  getPrice(timeIndex) {
    return this.strategy.getPrice(timeIndex);
  }
}

module.exports = {
  TariffStrategy,
  FlatTariff,
  TimeOfUseTariff,
  DynamicTariff,
  TariffContext,
};
