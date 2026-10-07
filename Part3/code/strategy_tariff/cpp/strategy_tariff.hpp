#pragma once

#include <algorithm>
#include <cstddef>
#include <memory>
#include <stdexcept>
#include <utility>
#include <vector>

namespace strategy_tariff {

class TariffStrategy {
public:
    virtual ~TariffStrategy() = default;
    virtual double getPrice(int timeIndex) const = 0;
};

class FlatTariff final : public TariffStrategy {
public:
    explicit FlatTariff(double price) : price_(price) {
        if (price < 0) throw std::invalid_argument("price must be non-negative");
    }

    double getPrice(int) const override {
        return price_;
    }

private:
    double price_;
};

class TimeOfUseTariff final : public TariffStrategy {
public:
    TimeOfUseTariff(
        double peakPrice,
        double offPeakPrice,
        int peakStart = 18,
        int peakEnd = 22
    ) : peakPrice_(peakPrice), offPeakPrice_(offPeakPrice),
        peakStart_(peakStart), peakEnd_(peakEnd) {
        if (std::min(peakPrice, offPeakPrice) < 0) {
            throw std::invalid_argument("prices must be non-negative");
        }
        if (!(0 <= peakStart && peakStart < peakEnd && peakEnd <= 24)) {
            throw std::invalid_argument("peak window must fall within a day");
        }
    }

    double getPrice(int timeIndex) const override {
        if (timeIndex < 0) throw std::invalid_argument("timeIndex must be non-negative");
        const int hour = timeIndex % 24;
        return peakStart_ <= hour && hour < peakEnd_ ? peakPrice_ : offPeakPrice_;
    }

private:
    double peakPrice_;
    double offPeakPrice_;
    int peakStart_;
    int peakEnd_;
};

class DynamicTariff final : public TariffStrategy {
public:
    explicit DynamicTariff(std::vector<double> prices) : prices_(std::move(prices)) {
        if (prices_.empty()
            || std::any_of(prices_.begin(), prices_.end(), [](double price) { return price < 0; })) {
            throw std::invalid_argument("prices must be a non-empty, non-negative series");
        }
    }

    double getPrice(int timeIndex) const override {
        if (timeIndex < 0) throw std::invalid_argument("timeIndex must be non-negative");
        return prices_.at(static_cast<std::size_t>(timeIndex) % prices_.size());
    }

private:
    std::vector<double> prices_;
};

class TariffContext {
public:
    explicit TariffContext(std::shared_ptr<TariffStrategy> strategy) {
        setStrategy(std::move(strategy));
    }

    void setStrategy(std::shared_ptr<TariffStrategy> strategy) {
        if (!strategy) throw std::invalid_argument("strategy must not be null");
        strategy_ = std::move(strategy);
    }

    double getPrice(int timeIndex) const {
        return strategy_->getPrice(timeIndex);
    }

private:
    std::shared_ptr<TariffStrategy> strategy_;
};

}  // namespace strategy_tariff
