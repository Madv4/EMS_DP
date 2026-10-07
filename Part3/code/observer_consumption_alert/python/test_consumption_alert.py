import math

from consumption_alert import ConsumptionAlertObserver, ConsumptionEvent, ConsumptionSubject


def run_case(
    case_id: str,
    threshold: float,
    time_index: int,
    load_id: str,
    grid_draw: float,
    renewable_draw: float,
    expected_alert_count: int,
    expected_consumption: float,
) -> None:
    subject = ConsumptionSubject()
    observer = ConsumptionAlertObserver(threshold)
    subject.subscribe(observer)
    consumption = grid_draw + renewable_draw
    if not math.isclose(consumption, expected_consumption, abs_tol=1e-9):
        raise AssertionError(f"{case_id}: consumption mismatch")
    subject.notify(ConsumptionEvent(time_index, {load_id: consumption}))
    if len(observer.alerts) != expected_alert_count:
        raise AssertionError(f"{case_id}: expected {expected_alert_count} alerts")
    if observer.alerts and not math.isclose(observer.alerts[0].consumption, expected_consumption):
        raise AssertionError(f"{case_id}: recorded consumption mismatch")


def main() -> None:
    cases = [
        ("CA01", 10.0, 0, "load-a", 5.0, 0.0, 0, 5.0),
        ("CA02", 10.0, 1, "load-a", 7.0, 5.0, 1, 12.0),
        ("CA03", 10.0, 2, "load-a", 10.0, 0.0, 0, 10.0),
        ("CA04", 0.05, 3, "load-b", 0.04, 0.02, 1, 0.06),
        ("CA05", 20.0, 4, "load-c", 12.0, 9.0, 1, 21.0),
    ]
    for case in cases:
        run_case(*case)

    subject = ConsumptionSubject()
    observer = ConsumptionAlertObserver(10.0)
    subject.subscribe(observer)
    subject.subscribe(observer)
    subject.notify(ConsumptionEvent(5, {"load-a": 11.0}))
    assert len(observer.alerts) == 1, "duplicate subscription must not duplicate alerts"

    subject.unsubscribe(observer)
    subject.notify(ConsumptionEvent(6, {"load-a": 12.0}))
    assert len(observer.alerts) == 1, "unsubscribed observer must not receive events"

    multi = ConsumptionAlertObserver(10.0)
    subject.subscribe(multi)
    subject.notify(ConsumptionEvent(7, {"load-a": 11.0, "load-b": 10.0, "load-c": 12.0}))
    assert [item.load_id for item in multi.alerts] == ["load-a", "load-c"]

    for invalid in (0.0, -1.0):
        try:
            ConsumptionAlertObserver(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("non-positive threshold must fail")

    total = len(cases) + 5
    print(f"Observer tests: {total}/{total} passed")


if __name__ == "__main__":
    main()
