# Cross-language analysis

## Strategy - Dynamic Tariff Selection

All four implementations preserve the same roles: `TariffStrategy`, three concrete strategies, and `TariffContext`. Flat pricing returns one constant. Time-of-use pricing repeats a half-open daily peak window. Dynamic pricing repeats a supplied non-negative series.

| Language | Representation | Dispatch and state observations |
|---|---|---|
| Java | Interface with nested concrete classes | Nominal interface conformance and explicit object references; arrays require defensive copying. |
| Python | Abstract base class with concrete subclasses | Concise runtime polymorphism; type annotations document the contract but runtime checks remain dynamic. |
| JavaScript | Base class and subclasses exported with CommonJS | Dynamic object model; the context checks the base-class relationship at runtime. |
| C++ | Abstract class with virtual method and header-only implementations | Compile-time type checking and virtual dispatch; `shared_ptr` makes strategy ownership explicit. |

The pattern reduces tariff-selection conditionals in the context. A new tariff type can be added without changing existing strategies or tariff clients.

## Observer - Consumption Threshold Alerts

All four implementations preserve the same roles: `ConsumptionSubject`, `ConsumptionObserver`, `ConsumptionAlertObserver`, and `ConsumptionEvent`. Duplicate subscriptions are ignored, unsubscribe stops later delivery, and equality with the threshold does not create an alert.

| Language | Representation | Dispatch and state observations |
|---|---|---|
| Java | Observer interface, subject-owned list, immutable-style event and alert objects | Nominal typing and defensive collection copies provide a clear event contract. |
| Python | Abstract observer, dataclass events, list-based subscriptions | Dataclasses make immutable event records concise; subscriber management is direct and readable. |
| JavaScript | Base observer class, frozen event object, array-based subscriptions | Runtime checks and object copying provide the contract without a static interface. |
| C++ | Abstract observer and subject storing non-owning observer pointers | Virtual dispatch is explicit; caller-managed observer lifetime must exceed the subscription. |

Observer keeps alert evaluation separate from event publication. More reactions can subscribe without changing the subject.

## Comparison

- Java and C++ express pattern roles most explicitly through static types.
- Python provides the smallest Strategy implementation by source LOC.
- JavaScript remains concise but relies on runtime checks for invalid collaborators.
- C++ requires explicit ownership and lifetime decisions that the garbage-collected languages avoid.
- The observed process times mostly measure runtime startup and test-runner work because the pattern examples are small.

The functional result is consistent across all languages according to automated Python/JavaScript runs and the team's Java/C++ verification.
