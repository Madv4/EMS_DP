#include "consumption_alert.hpp"

#include <cmath>
#include <cstddef>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <string>

using namespace consumption_alert;

namespace {
int total = 0;
int passed = 0;

void run(const std::string& name, const std::function<void()>& test) {
    ++total;
    try {
        test();
        ++passed;
    } catch (const std::exception& error) {
        throw std::runtime_error(name + " failed: " + error.what());
    }
}

void runCase(
    double threshold,
    int timeIndex,
    const std::string& loadId,
    double gridDraw,
    double renewableDraw,
    std::size_t expectedAlertCount,
    double expectedConsumption
) {
    ConsumptionSubject subject;
    ConsumptionAlertObserver observer(threshold);
    subject.subscribe(&observer);
    const double consumption = gridDraw + renewableDraw;
    if (std::abs(consumption - expectedConsumption) > 1e-9) {
        throw std::runtime_error("consumption mismatch");
    }
    subject.notify({timeIndex, {{loadId, consumption}}});
    if (observer.snapshot().size() != expectedAlertCount) {
        throw std::runtime_error("alert count mismatch");
    }
    if (!observer.snapshot().empty()
        && std::abs(observer.snapshot().front().consumption - expectedConsumption) > 1e-9) {
        throw std::runtime_error("recorded consumption mismatch");
    }
}

void expectInvalidArgument(const std::function<void()>& action) {
    try {
        action();
    } catch (const std::invalid_argument&) {
        return;
    }
    throw std::runtime_error("expected invalid_argument");
}
}  // namespace

int main() {
    run("CA01", [] { runCase(10.0, 0, "load-a", 5.0, 0.0, 0, 5.0); });
    run("CA02", [] { runCase(10.0, 1, "load-a", 7.0, 5.0, 1, 12.0); });
    run("CA03", [] { runCase(10.0, 2, "load-a", 10.0, 0.0, 0, 10.0); });
    run("CA04", [] { runCase(0.05, 3, "load-b", 0.04, 0.02, 1, 0.06); });
    run("CA05", [] { runCase(20.0, 4, "load-c", 12.0, 9.0, 1, 21.0); });

    run("duplicate subscription", [] {
        ConsumptionSubject subject;
        ConsumptionAlertObserver observer(10.0);
        subject.subscribe(&observer);
        subject.subscribe(&observer);
        subject.notify({5, {{"load-a", 11.0}}});
        if (observer.snapshot().size() != 1) throw std::runtime_error("duplicate alert");
    });

    run("unsubscribe", [] {
        ConsumptionSubject subject;
        ConsumptionAlertObserver observer(10.0);
        subject.subscribe(&observer);
        subject.unsubscribe(&observer);
        subject.notify({6, {{"load-a", 12.0}}});
        if (!observer.snapshot().empty()) throw std::runtime_error("unexpected alert");
    });

    run("multiple loads", [] {
        ConsumptionSubject subject;
        ConsumptionAlertObserver observer(10.0);
        subject.subscribe(&observer);
        subject.notify({7, {{"load-a", 11.0}, {"load-b", 10.0}, {"load-c", 12.0}}});
        if (observer.snapshot().size() != 2) throw std::runtime_error("expected two alerts");
        if (observer.snapshot()[0].loadId != "load-a" || observer.snapshot()[1].loadId != "load-c") {
            throw std::runtime_error("wrong alerted loads");
        }
    });

    run("zero threshold", [] { expectInvalidArgument([] { ConsumptionAlertObserver observer(0.0); }); });
    run("negative threshold", [] { expectInvalidArgument([] { ConsumptionAlertObserver observer(-1.0); }); });

    std::cout << "Observer tests: " << passed << "/" << total << " passed\n";
}
