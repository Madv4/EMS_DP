import time
import asyncio
from typing import Optional
from typing import Any, List
from ems.application.services.ems_service import EMSContext, boot, advance
from ems.domain.ports.forecast_provider import ForecastProvider
from ems.domain.ports.portfolio_repository import PortfolioRepository
from ems.infrastructure.serializer import serial_portfolio, serial_metrics


class EMSRuntime:
    """Queue-based runtime to safely wrap EMSContext"""

    def __init__(self, context: EMSContext, timestep: float = 2.0):
        self.context = context
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=20)
        self.subscribers: List[Any] = []
        self.timestep = timestep
        self._running_event = asyncio.Event()
        self._context_lock = asyncio.Lock()
        self._subscribers_lock = asyncio.Lock()

    async def submit(self, fn, *args):
        """Submit a command to the runtime queue and await its result"""
        fut = asyncio.get_event_loop().create_future()
        await self.queue.put((fn, args, fut))
        return await fut

    async def run(self):
        """Main runtime loop processing queued commands and managing timed advancement"""

        # start running
        self._running_event.set()

        # Start the advance task
        advance_task = asyncio.create_task(self._timed_advance())

        while self._running_event.is_set():
            # Ensure command is obtainable
            try:
                cmd, args, fut = await asyncio.wait_for(self.queue.get(), timeout=0.1)
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Unexpected error getting queue item: {e}")
                continue

            # Process the command safely
            try:
                async with self._context_lock:
                    res = cmd(self.context, *args)
                fut.set_result(res)
                await self.broadcast()
            except Exception as e:
                fut.set_exception(e)

        # guaranteed cleanup of advance task
        advance_task.cancel()
        try:
            await advance_task
        except asyncio.CancelledError:
            pass

    async def _timed_advance(self):
        """Periodically advance the EMS context at fixed timestep intervals"""
        next_advance = time.monotonic()
        while self._running_event.is_set():
            async with self._context_lock:
                advance(self.context)
            await self.broadcast()
            # schedule next tick
            next_advance += self.timestep
            delay = max(0, next_advance - time.monotonic())
            await asyncio.sleep(delay)

    async def broadcast(self):
        """Send current context snapshot to all active subscribers,
        avoids locking during io operations
        
        contains portfolio staleness flag to let users know when to
        "refresh" the scheduling plan
        """
        async with self._context_lock:
            snapshot = {
                "portfolio": serial_portfolio(self.context.portfolio),
                "forward": serial_metrics(self.context.forward),
                "backward": serial_metrics(self.context.backward),
            }
        async with self._subscribers_lock:
            subscribers = list(self.subscribers)
        for ws in subscribers:
            try:
                await ws.send_json(snapshot)
            except Exception as e:
                print(f"Failed to send to subscriber: {e}")
                async with self._subscribers_lock:
                    if ws in self.subscribers:
                        self.subscribers.remove(ws)

    async def stop(self):
        self._running_event.clear()


# Create context & runtime on import
runtime: Optional[EMSRuntime] = None
runtime_task: Optional[asyncio.Task] = None


async def start_services(
    duration: int, provider: ForecastProvider, repository: PortfolioRepository
):
    """Initialize and start the global EMS runtime services"""
    global runtime, runtime_task
    if runtime is None:
        context = boot(duration=duration, provider=provider, repository=repository)
        runtime = EMSRuntime(context)
        runtime_task = asyncio.create_task(runtime.run())


async def stop_services():
    """Gracefully shutdown the global EMS runtime services"""
    global runtime, runtime_task
    if runtime is not None:
        await runtime.stop()
        if runtime_task:
            try:
                await runtime_task
            except asyncio.CancelledError:
                pass
            runtime_task = None
        runtime = None


def get_runtime() -> EMSRuntime:
    assert runtime is not None, "runtime not initialized. Did you forget startup?"
    return runtime
