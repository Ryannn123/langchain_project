from collections.abc import Callable

from src.state import AgentState
from src.types import Area

STEP_DERIVERS: dict[tuple[str, str], Callable[[AgentState], str]] = {}

def step(area: str | Area, strategy: str):
    def decorator(func: Callable[[AgentState], str]) -> Callable[[AgentState], str]:
        area_str = area.value if isinstance(area, Area) else area
        STEP_DERIVERS[(area_str, strategy)] = func
        return func
    return decorator

def get_step(state: AgentState, area: str, strategy: str):    
    deriver = STEP_DERIVERS.get((area, strategy))
    if deriver:
        return deriver(state)
    
    return 'unknown'