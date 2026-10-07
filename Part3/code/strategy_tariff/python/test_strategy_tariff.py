import math

from strategy_tariff import DynamicTariff, FlatTariff, TariffContext, TimeOfUseTariff


def assert_price(actual: float, expected: float, case_id: str) -> None:
    if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=1e-9):
        raise AssertionError(f"{case_id}: expected {expected}, got {actual}")


def expect_error(action, case_id: str) -> None:
    try:
        action()
    except (TypeError, ValueError):
        return
    raise AssertionError(f"{case_id}: expected an error")


def main() -> None:
    context = TariffContext(FlatTariff(0.15))
    cases = [
        ("DT01", FlatTariff(0.15), 0, 0.15),
        ("DT02", FlatTariff(0.15), 23, 0.15),
        ("DT03", TimeOfUseTariff(0.30, 0.15, 18, 22), 17, 0.15),
        ("DT04", TimeOfUseTariff(0.30, 0.15, 18, 22), 18, 0.30),
        ("DT05", TimeOfUseTariff(0.30, 0.15, 18, 22), 21, 0.30),
        ("DT06", TimeOfUseTariff(0.30, 0.15, 18, 22), 22, 0.15),
        ("DT07", TimeOfUseTariff(0.30, 0.15, 18, 22), 42, 0.30),
        ("DT08", DynamicTariff([0.10, 0.20, 0.35, 0.15]), 0, 0.10),
        ("DT09", DynamicTariff([0.10, 0.20, 0.35, 0.15]), 2, 0.35),
        ("DT10", DynamicTariff([0.10, 0.20, 0.35, 0.15]), 4, 0.10),
    ]
    for case_id, strategy, time_index, expected in cases:
        context.set_strategy(strategy)
        assert_price(context.get_price(time_index), expected, case_id)

    invalid_cases = [
        ("negative flat price", lambda: FlatTariff(-0.01)),
        ("negative time-of-use price", lambda: TimeOfUseTariff(-0.01, 0.10)),
        ("invalid peak window", lambda: TimeOfUseTariff(0.30, 0.15, 22, 18)),
        ("empty dynamic series", lambda: DynamicTariff([])),
        ("negative dynamic price", lambda: DynamicTariff([0.10, -0.20])),
        ("negative time-of-use index", lambda: TimeOfUseTariff(0.30, 0.15).get_price(-1)),
        ("negative dynamic index", lambda: DynamicTariff([0.10]).get_price(-1)),
    ]
    for case_id, action in invalid_cases:
        expect_error(action, case_id)

    print(f"Strategy tests: {len(cases) + len(invalid_cases)}/{len(cases) + len(invalid_cases)} passed")


if __name__ == "__main__":
    main()
