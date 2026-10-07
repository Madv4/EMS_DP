#include "strategy_tariff.hpp"

#include <cmath>
#include <functional>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

using namespace strategy_tariff;

namespace {
int total = 0;
int passed = 0;
TariffContext context(std::make_shared<FlatTariff>(0.15));

void run(const std::string& name, const std::function<void()>& test) {
    ++total;
    try {
        test();
        ++passed;
    } catch (const std::exception& error) {
        throw std::runtime_error(name + " failed: " + error.what());
    }
}

void checkPrice(std::shared_ptr<TariffStrategy> strategy, int timeIndex, double expected) {
    context.setStrategy(std::move(strategy));
    const double actual = context.getPrice(timeIndex);
    if (std::abs(actual - expected) > 1e-9) {
        throw std::runtime_error("price mismatch");
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
    run("DT01", [] { checkPrice(std::make_shared<FlatTariff>(0.15), 0, 0.15); });
    run("DT02", [] { checkPrice(std::make_shared<FlatTariff>(0.15), 23, 0.15); });
    run("DT03", [] { checkPrice(std::make_shared<TimeOfUseTariff>(0.30, 0.15, 18, 22), 17, 0.15); });
    run("DT04", [] { checkPrice(std::make_shared<TimeOfUseTariff>(0.30, 0.15, 18, 22), 18, 0.30); });
    run("DT05", [] { checkPrice(std::make_shared<TimeOfUseTariff>(0.30, 0.15, 18, 22), 21, 0.30); });
    run("DT06", [] { checkPrice(std::make_shared<TimeOfUseTariff>(0.30, 0.15, 18, 22), 22, 0.15); });
    run("DT07", [] { checkPrice(std::make_shared<TimeOfUseTariff>(0.30, 0.15, 18, 22), 42, 0.30); });
    run("DT08", [] { checkPrice(std::make_shared<DynamicTariff>(std::vector<double>{0.10, 0.20, 0.35, 0.15}), 0, 0.10); });
    run("DT09", [] { checkPrice(std::make_shared<DynamicTariff>(std::vector<double>{0.10, 0.20, 0.35, 0.15}), 2, 0.35); });
    run("DT10", [] { checkPrice(std::make_shared<DynamicTariff>(std::vector<double>{0.10, 0.20, 0.35, 0.15}), 4, 0.10); });
    run("negative flat price", [] { expectInvalidArgument([] { FlatTariff tariff(-0.01); }); });
    run("negative time-of-use price", [] { expectInvalidArgument([] { TimeOfUseTariff tariff(-0.01, 0.10); }); });
    run("invalid peak window", [] { expectInvalidArgument([] { TimeOfUseTariff tariff(0.30, 0.15, 22, 18); }); });
    run("empty dynamic series", [] { expectInvalidArgument([] { DynamicTariff tariff(std::vector<double>{}); }); });
    run("negative dynamic price", [] { expectInvalidArgument([] { DynamicTariff tariff(std::vector<double>{0.10, -0.20}); }); });
    run("negative time-of-use index", [] { expectInvalidArgument([] { TimeOfUseTariff(0.30, 0.15).getPrice(-1); }); });
    run("negative dynamic index", [] { expectInvalidArgument([] { DynamicTariff(std::vector<double>{0.10}).getPrice(-1); }); });
    std::cout << "Strategy tests: " << passed << "/" << total << " passed\n";
}
