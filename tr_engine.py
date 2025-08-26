# tr_engine.py - The Core EGC + TR Engine (v1.4 - Tolerance Fix)
from dataclasses import dataclass, field
from typing import List, Set, Tuple

# --- Data Structures ---
@dataclass
class Entity:
    id: str
    state: float
    stable_states: Set[float]

@dataclass
class Cycle:
    length: int
    phases: int
    @property
    def phase_duration(self) -> float:
        return self.length / self.phases if self.phases > 0 else 0

@dataclass
class Phase:
    index: int
    state: float
    adjusted_state: float = 0.0

@dataclass
class TaskCreditLedger:
    cycle_id: int
    excess: float
    target_cycle: int

@dataclass
class Constitution:
    priorities: List[dict] = field(default_factory=list)

@dataclass
class System:
    entities: List[Entity]
    cycle: Cycle
    target_state: float
    phases: List[Phase] = field(default_factory=list)
    ledger: TaskCreditLedger = field(default_factory=lambda: TaskCreditLedger(0, 0.0, 1))
    config: dict = field(default_factory=lambda: {"MAX_TOLERANCE": 3.0, "NOISE_COEFFICIENT": 0.05})  # Tolerance increased to 3.0
    constitution: Constitution = field(default_factory=Constitution)

# --- Core Functions ---

def split(total_state: float, num_phases: int) -> List[Phase]:
    """Splits the total state, handling non-divisible remainders."""
    if total_state <= 0: raise ValueError("Total state must be positive.")
    if num_phases <= 0: raise ValueError("Number of phases must be positive.")
    phase_state = total_state / num_phases
    return [Phase(index=i, state=phase_state) for i in range(num_phases)]

def refract(system: System) -> Tuple[List[Phase], float]:
    """Adjusts each phase to the target state and calculates the excess."""
    if not all(system.target_state in e.stable_states for e in system.entities):
        raise ValueError(f"Target state {system.target_state} not in all entities' stable states.")
    excess = 0.0
    adjusted_phases = []
    for phase in system.phases:
        shift = phase.state - system.target_state
        phase.adjusted_state = system.target_state
        excess += shift
        adjusted_phases.append(phase)
    return (adjusted_phases, excess)

def recombine(system: System) -> List[Entity
