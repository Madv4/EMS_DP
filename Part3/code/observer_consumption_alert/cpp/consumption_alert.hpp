#pragma once

#include <algorithm>
#include <map>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace consumption_alert {

struct ConsumptionEvent {
    int timeIndex;
    std::map<std::string, double> byLoad;
};

class ConsumptionObserver {
public:
    virtual ~ConsumptionObserver() = default;
    virtual void update(const ConsumptionEvent& event) = 0;
};

class ConsumptionSubject {
public:
    void subscribe(ConsumptionObserver* observer) {
        if (observer == nullptr) throw std::invalid_argument("observer must not be null");
        if (std::find(observers_.begin(), observers_.end(), observer) == observers_.end()) {
            observers_.push_back(observer);
        }
    }

    void unsubscribe(ConsumptionObserver* observer) {
        const auto position = std::find(observers_.begin(), observers_.end(), observer);
        if (position == observers_.end()) throw std::invalid_argument("observer is not subscribed");
        observers_.erase(position);
    }

    void notify(const ConsumptionEvent& event) {
        const auto snapshot = observers_;
        for (ConsumptionObserver* observer : snapshot) observer->update(event);
    }

private:
    std::vector<ConsumptionObserver*> observers_;
};

struct AlertRecord {
    int timeIndex;
    std::string loadId;
    double consumption;
    double threshold;
};

class ConsumptionAlertObserver final : public ConsumptionObserver {
public:
    explicit ConsumptionAlertObserver(double threshold = 10.0) {
        setThreshold(threshold);
    }

    void setThreshold(double threshold) {
        if (threshold <= 0) throw std::invalid_argument("threshold must be positive");
        threshold_ = threshold;
    }

    void update(const ConsumptionEvent& event) override {
        for (const auto& [loadId, consumption] : event.byLoad) {
            if (consumption > threshold_) {
                alerts_.push_back({event.timeIndex, loadId, consumption, threshold_});
            }
        }
    }

    const std::vector<AlertRecord>& snapshot() const {
        return alerts_;
    }

private:
    double threshold_{};
    std::vector<AlertRecord> alerts_;
};

}  // namespace consumption_alert
