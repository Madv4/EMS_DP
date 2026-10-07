from abc import ABC, abstractmethod


class TariffStrategy(ABC):
    @abstractmethod
    def get_price(self, time_index: int) -> float:
        raise NotImplementedError


class FlatTariff(TariffStrategy):
    def __init__(self, price: float):
        if price < 0:
            raise ValueError("price must be non-negative")
        self.price = price

    def get_price(self, time_index: int) -> float:
        return self.price


class TimeOfUseTariff(TariffStrategy):
    def __init__(
        self,
        peak_price: float,
        off_peak_price: float,
        peak_start: int = 18,
        peak_end: int = 22,
    ):
        if min(peak_price, off_peak_price) < 0:
            raise ValueError("prices must be non-negative")
        if not 0 <= peak_start < peak_end <= 24:
            raise ValueError("peak window must fall within a day")
        self.peak_price = peak_price
        self.off_peak_price = off_peak_price
        self.peak_start = peak_start
        self.peak_end = peak_end

    def get_price(self, time_index: int) -> float:
        if time_index < 0:
            raise ValueError("time_index must be non-negative")
        hour = time_index % 24
        return self.peak_price if self.peak_start <= hour < self.peak_end else self.off_peak_price


class DynamicTariff(TariffStrategy):
    def __init__(self, prices: list[float]):
        if not prices or any(price < 0 for price in prices):
            raise ValueError("prices must be a non-empty, non-negative series")
        self.prices = list(prices)

    def get_price(self, time_index: int) -> float:
        if time_index < 0:
            raise ValueError("time_index must be non-negative")
        return self.prices[time_index % len(self.prices)]


class TariffContext:
    def __init__(self, strategy: TariffStrategy):
        self.set_strategy(strategy)

    def set_strategy(self, strategy: TariffStrategy) -> None:
        if not isinstance(strategy, TariffStrategy):
            raise TypeError("strategy must implement TariffStrategy")
        self._strategy = strategy

    def get_price(self, time_index: int) -> float:
        return self._strategy.get_price(time_index)
