# tr_engine.py - The Core EGC + TR Engine (v2.0 - Production Ready)
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
    config: dict = field(default_factory=lambda: {"MAX_TOLERANCE": 3.0, "NOISE_COEFFICIENT": 0.05})
    constitution: Constitution = field(default_factory=Constitution)

# --- Core Functions ---

def split(total_state: float, num_phases: int) -> List[Phase]:
    """Splits the total state evenly across phases."""
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

def recombine(system: System) -> List[Entity]:
    """Distributes the new stable state across entities, handling discretization."""
    total_new_state = sum(p.adjusted_state for p in system.phases)
    if not system.entities: return []
    ideal_per_entity_state = total_new_state / len(system.entities)
    final_entities = []
    for entity in system.entities:
        if not entity.stable_states: raise ValueError(f"Entity {entity.id} has no defined stable states.")
        closest_state = min(entity.stable_states, key=lambda s: abs(s - ideal_per_entity_state))
        if abs(closest_state - ideal_per_entity_state) > system.config.get("MAX_TOLERANCE", 3.0):
            raise ValueError(f"No stable state within tolerance for entity {entity.id}.")
        final_entities.append(Entity(id=entity.id, state=closest_state, stable_states=entity.stable_states))
    return final_entities
    
def Consequence_Simulator(system: System) -> bool:
    """Simulates next cycle to check for secondary peaks. Returns True if safe."""
    simulated_total_new_state = system.target_state * system.cycle.phases
    base_target_total = system.target_state * len(system.entities)
    max_allowed_peak = base_target_total * 1.5
    return simulated_total_new_state <= max_allowed_peak

def TR_execute(system: System, cycle_increment: int = 1) -> Tuple[System, bool]:
    """Main wrapper function to execute the full TR operation."""
    try:
        if not system.entities: raise ValueError("Entity list cannot be empty.")
        for entity in system.entities:
            if not entity.stable_states:
                raise ValueError(f"Entity {entity.id} has no defined stable states.")

        total_state = sum(e.state for e in system.entities)
        system.phases = split(total_state, system.cycle.phases)
        
        system.phases, excess = refract(system)
        
        if not Consequence_Simulator(system):
            raise ValueError("Proposed refraction creates an unstable secondary peak.")

        updated_entities = recombine(system)
        
        final_total_state = sum(e.state for e in updated_entities)
        total_new_state_from_phases = sum(p.adjusted_state for p in system.phases)
        rounding_dust = total_new_state_from_phases - final_total_state
        
        system.entities = updated_entities
        system.ledger.excess = excess + rounding_dust
        system.ledger.cycle_id += cycle_increment
        system.ledger.target_cycle = system.ledger.cycle_id + 1
        return (system, True)
    except ValueError as e:
        # Pass the specific error message for better debugging
        raise ValueError(f"TR_execute failed: {e}") from e
