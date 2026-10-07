from abc import ABC, abstractmethod
from typing import Optional
import uuid

from ems.domain.models.portfolio import Portfolio


class PortfolioRepository(ABC):
    """Abstract interface for portfolio persistence"""

    @abstractmethod
    def save_portfolio(self, portfolio: Portfolio) -> None:
        pass

    @abstractmethod
    def open_portfolio(self, folio_id: uuid.UUID) -> Optional[Portfolio]:
        pass

    @abstractmethod
    def delete_portfolio(self, folio_id: uuid.UUID) -> None:
        pass
