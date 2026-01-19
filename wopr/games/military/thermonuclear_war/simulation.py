"""War simulation logic for Global Thermonuclear War."""

from dataclasses import dataclass
import random

from .targets import Target


@dataclass
class StrikeResult:
    """Result of a nuclear strike."""
    target: Target
    success: bool
    casualties: int
    destroyed: bool
    fallout_radius_km: int


@dataclass
class WarOutcome:
    """Final outcome of the war simulation."""
    attacker_casualties: int
    defender_casualties: int
    cities_destroyed_attacker: int
    cities_destroyed_defender: int
    military_destroyed_attacker: int
    military_destroyed_defender: int
    winner: str  # "NONE", attacker side, defender side


class WarSimulation:
    """Simulates nuclear war outcomes."""

    # Warhead yield estimates (megatons)
    WARHEAD_YIELD = {
        "ICBM": 1.0,
        "SLBM": 0.5,
        "BOMB": 1.5,
    }

    # Kill radius per megaton (km)
    KILL_RADIUS_PER_MT = 5

    # Fallout multiplier
    FALLOUT_MULTIPLIER = 3

    def __init__(self) -> None:
        self._strike_results: list[StrikeResult] = []

    def calculate_strike(self, target: Target, warhead_type: str = "ICBM") -> StrikeResult:
        """Calculate the result of a nuclear strike on a target."""
        yield_mt = self.WARHEAD_YIELD.get(warhead_type, 1.0)
        kill_radius = yield_mt * self.KILL_RADIUS_PER_MT
        fallout_radius = int(kill_radius * self.FALLOUT_MULTIPLIER)

        # Success probability (higher for cities, lower for hardened military)
        if target.target_type == "CITY":
            success_prob = 0.95
        elif target.target_type == "MILITARY":
            success_prob = 0.7
        else:
            success_prob = 0.85

        success = random.random() < success_prob

        if success:
            if target.target_type == "CITY":
                # City casualties depend on population and yield
                direct_kill_pct = min(0.9, yield_mt * 0.3)
                casualties = int(target.population * direct_kill_pct)
                # Add fallout casualties
                fallout_pct = min(0.3, yield_mt * 0.1)
                casualties += int(target.population * fallout_pct)
            else:
                # Military/industrial - fewer civilian casualties
                casualties = random.randint(5000, 50000)

            destroyed = True
        else:
            casualties = random.randint(0, 1000)  # Near miss
            destroyed = False

        result = StrikeResult(
            target=target,
            success=success,
            casualties=casualties,
            destroyed=destroyed,
            fallout_radius_km=fallout_radius
        )
        self._strike_results.append(result)
        return result

    def simulate_full_exchange(
        self,
        attacker_targets: list[Target],
        defender_targets: list[Target]
    ) -> WarOutcome:
        """Simulate a full nuclear exchange."""
        attacker_casualties = 0
        defender_casualties = 0
        cities_destroyed_attacker = 0
        cities_destroyed_defender = 0
        military_destroyed_attacker = 0
        military_destroyed_defender = 0

        # First strike by attacker
        for target in defender_targets:
            result = self.calculate_strike(target)
            defender_casualties += result.casualties
            if result.destroyed:
                if target.target_type == "CITY":
                    cities_destroyed_defender += 1
                elif target.target_type == "MILITARY":
                    military_destroyed_defender += 1

        # Retaliation by defender
        for target in attacker_targets:
            result = self.calculate_strike(target)
            attacker_casualties += result.casualties
            if result.destroyed:
                if target.target_type == "CITY":
                    cities_destroyed_attacker += 1
                elif target.target_type == "MILITARY":
                    military_destroyed_attacker += 1

        # Determine "winner" - spoiler: no one wins
        winner = "NONE"

        return WarOutcome(
            attacker_casualties=attacker_casualties,
            defender_casualties=defender_casualties,
            cities_destroyed_attacker=cities_destroyed_attacker,
            cities_destroyed_defender=cities_destroyed_defender,
            military_destroyed_attacker=military_destroyed_attacker,
            military_destroyed_defender=military_destroyed_defender,
            winner=winner
        )

    def get_casualty_estimate(self, targets: list[Target]) -> int:
        """Estimate total casualties for a list of targets."""
        total = 0
        for target in targets:
            if target.target_type == "CITY":
                total += int(target.population * 0.6)
            else:
                total += 25000
        return total

    def reset(self) -> None:
        """Reset simulation state."""
        self._strike_results = []

    @property
    def strike_results(self) -> list[StrikeResult]:
        """Get all strike results."""
        return self._strike_results.copy()
