from dataclasses import dataclass, field
import uuid

from ems.domain.models.types import LoadStatus


@dataclass(slots=True)
class Load:
    """Represents a power drawing asset"""

    load_id: uuid.UUID = field(default_factory=uuid.uuid4)
    status: LoadStatus = LoadStatus.OFF
    priority: int = 1
    throughput: tuple[float, float] = (0.1, 0.1)
    run_duration: int = 1

    def toggle_on(self) -> None:
        if self.status == LoadStatus.OFF:
            self.status = LoadStatus.PENDING

    def toggle_off(self) -> None:
        """Can be turned off from any state"""
        self.status = LoadStatus.OFF

    def confirm_schedule(self) -> None:
        if self.status == LoadStatus.PENDING:
            self.status = LoadStatus.CONFIRMED

    def unconfirm_schedule(self) -> None:
        if self.status == LoadStatus.CONFIRMED:
            self.status = LoadStatus.PENDING

    def start_running(self) -> None:
        """Can only run if the load's schedule is confirmed,
        and the start time is immediate
        """
        if self.status == LoadStatus.CONFIRMED:
            self.status = LoadStatus.RUNNING


@dataclass(slots=True)
class Portfolio:
    """A collection of Loads with schedule optimization configuration"""

    folio_id: uuid.UUID = field(default_factory=uuid.uuid4)
    loads: dict[uuid.UUID, Load] = field(default_factory=dict)
    cost_vs_emission_weight: float = 0.5
    emission_coeff: float = 0.2
    priority_coeff: float = 0.1
    is_optimized: bool = False

    def get_active_loads(self):
        """Returns all loads which are currently not OFF"""
        return {
            load_id: load
            for load_id, load in self.loads.items()
            if load.status != LoadStatus.OFF
        }
    
    def get_running_loads(self):
        """Returns all loads which are currently RUNNING"""
        return {
            load_id: load
            for load_id, load in self.loads.items()
            if load.status == LoadStatus.RUNNING
        }

    def mark_dirty(self):
        self.is_optimized = False

    def clear_dirty(self):
        self.is_optimized = True
