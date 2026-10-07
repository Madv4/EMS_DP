from ems.domain.ports.portfolio_repository import PortfolioRepository
from ems.domain.models.portfolio import Portfolio
from typing import Optional
import uuid


class SimplePortfolioRepository(PortfolioRepository):
    """Mock file-based portfolio storage"""

    def save_portfolio(self, portfolio: Portfolio) -> None:
        return

    def open_portfolio(self, folio_id: uuid.UUID) -> Optional[Portfolio]:
        return Portfolio()

    def delete_portfolio(self, folio_id: uuid.UUID) -> None:
        return
