"""World map rendering for Global Thermonuclear War."""

from dataclasses import dataclass, field
import math


@dataclass
class Missile:
    """A missile in flight."""
    origin: tuple[int, int]  # Screen coordinates (x, y)
    target: tuple[int, int]  # Screen coordinates (x, y)
    progress: float = 0.0    # 0.0 = launched, 1.0 = impact
    trail: list[tuple[int, int]] = field(default_factory=list)
    impacted: bool = False
    side: str = "US"  # Which side fired this missile

    def advance(self, step: float = 0.1) -> bool:
        """Advance missile along trajectory. Returns True if just impacted."""
        if self.impacted:
            return False

        # Store current position in trail before moving
        current_pos = self.current_position()
        if current_pos not in self.trail:
            self.trail.append(current_pos)

        self.progress = min(1.0, self.progress + step)
        if self.progress >= 1.0:
            self.impacted = True
            return True
        return False

    def current_position(self) -> tuple[int, int]:
        """Get current screen position."""
        x = int(self.origin[0] + (self.target[0] - self.origin[0]) * self.progress)
        y = int(self.origin[1] + (self.target[1] - self.origin[1]) * self.progress)
        return (x, y)


class WorldMap:
    """ASCII world map for GTW display with animation support."""

    # Map dimensions (inside the border)
    MAP_WIDTH = 77
    MAP_HEIGHT = 18

    # Base map as lines (no title, just the map area for easier manipulation)
    BASE_MAP = [
        "    +-----------------------------------------------------------------------------+",
        "    |                                                                             |",
        "    |         _____                                   ___                         |",
        "    |      ,-'     `-.                              ,'   `._                      |",
        "    |    ,'           `.    ,--.                  ,'        `.   ,---.            |",
        "    |   /               \\  |    |                /            \\ /      `.         |",
        "    |  |     U S A       | |    |               |              |         |        |",
        "    |  |        @        | `----'               |      @       /         |        |",
        "    |   \\               /                        \\            /          |        |",
        "    |    `._         _,'                          `._      _,'          /         |",
        "    |       `--.___,-'                               `----'       _.--'          |",
        "    |          |                ,--.                          ,-'                |",
        "    |          |               /    \\                       ,'                   |",
        "    |    ,-----|              |      |                    ,'      ,----.         |",
        "    |   /      |               \\    /                   ,'       /      \\        |",
        "    |  |       |                `--'                   /        |        |        |",
        "    |   \\     /                                       /          `------'         |",
        "    |    `---'                                                                    |",
        "    |                                                                             |",
        "    +-----------------------------------------------------------------------------+",
    ]

    TITLE = "                              GLOBAL THERMONUCLEAR WAR"

    # Screen coordinates for key locations (x, y) - tuned for this ASCII map
    # x is column (0-80), y is row (0-19) within BASE_MAP
    LOCATIONS = {
        # US targets (left side of map)
        "WASHINGTON": (21, 7),
        "NEW YORK": (24, 6),
        "LOS ANGELES": (12, 8),
        "CHICAGO": (19, 6),
        "SEATTLE": (11, 5),
        "US_CENTER": (18, 7),  # General US launch point

        # USSR/Russia targets (right side of map)
        "MOSCOW": (53, 7),
        "LENINGRAD": (51, 5),
        "KIEV": (50, 8),
        "VLADIVOSTOK": (68, 8),
        "NOVOSIBIRSK": (60, 6),
        "USSR_CENTER": (55, 7),  # General USSR launch point
    }

    def __init__(self) -> None:
        self._missiles: list[Missile] = []
        self._explosions: list[tuple[int, int, int]] = []  # (x, y, frame)
        self._impacts: list[tuple[int, int]] = []  # Permanent impact markers

    def get_map_array(self) -> list[list[str]]:
        """Get the base map as a 2D character array."""
        return [list(line) for line in self.BASE_MAP]

    def add_missile(self, origin: str | tuple[int, int], target: str | tuple[int, int], side: str = "US") -> Missile:
        """Add a missile to the simulation.

        Args:
            origin: Location name or (x, y) coordinates
            target: Location name or (x, y) coordinates
            side: "US" or "USSR"

        Returns:
            The created Missile object
        """
        # Resolve location names to coordinates
        if isinstance(origin, str):
            origin = self.LOCATIONS.get(origin.upper(), self.LOCATIONS["US_CENTER"])
        if isinstance(target, str):
            target = self.LOCATIONS.get(target.upper(), self.LOCATIONS["USSR_CENTER"])

        missile = Missile(origin=origin, target=target, side=side)
        self._missiles.append(missile)
        return missile

    def add_explosion(self, x: int, y: int) -> None:
        """Add an explosion at the given position."""
        self._explosions.append((x, y, 0))
        self._impacts.append((x, y))

    def advance_all(self, step: float = 0.15) -> list[Missile]:
        """Advance all missiles. Returns list of missiles that just impacted."""
        newly_impacted = []
        for missile in self._missiles:
            if missile.advance(step):
                newly_impacted.append(missile)
                self.add_explosion(missile.target[0], missile.target[1])

        # Advance explosion animations
        self._explosions = [(x, y, frame + 1) for x, y, frame in self._explosions if frame < 5]

        return newly_impacted

    def clear_missiles(self) -> None:
        """Clear all missiles and explosions."""
        self._missiles = []
        self._explosions = []
        self._impacts = []

    def render_frame(self) -> str:
        """Render the current frame with all missiles and effects."""
        # Start with base map
        map_array = self.get_map_array()

        # Draw missile trails
        for missile in self._missiles:
            for tx, ty in missile.trail:
                if 5 <= tx < 78 and 1 <= ty < 19:
                    if map_array[ty][tx] == ' ':
                        map_array[ty][tx] = '.'

        # Draw active missiles (not yet impacted)
        for missile in self._missiles:
            if not missile.impacted:
                x, y = missile.current_position()
                if 5 <= x < 78 and 1 <= y < 19:
                    map_array[y][x] = '*'

        # Draw explosions
        explosion_chars = ['*', '#', 'X', '#', '*', '.']
        for x, y, frame in self._explosions:
            if 5 <= x < 78 and 1 <= y < 19 and frame < len(explosion_chars):
                map_array[y][x] = explosion_chars[frame]

        # Draw permanent impact markers (after explosion animation)
        for x, y in self._impacts:
            still_exploding = any(ex == x and ey == y for ex, ey, _ in self._explosions)
            if not still_exploding and 5 <= x < 78 and 1 <= y < 19:
                map_array[y][x] = 'X'

        # Convert back to string
        lines = [''.join(row) for row in map_array]
        return self.TITLE + "\n" + "\n".join(lines)

    def render(self) -> str:
        """Render the static map (no missiles)."""
        return self.TITLE + "\n" + "\n".join(self.BASE_MAP)

    def get_location(self, name: str) -> tuple[int, int] | None:
        """Get screen coordinates for a named location."""
        return self.LOCATIONS.get(name.upper())

    def has_active_missiles(self) -> bool:
        """Check if there are any missiles still in flight."""
        return any(not m.impacted for m in self._missiles)


class WarAnimator:
    """Manages the escalating war animation sequence."""

    def __init__(self, world_map: WorldMap):
        self.map = world_map
        self.us_casualties = 0
        self.ussr_casualties = 0

    def get_us_targets(self) -> list[str]:
        """Get list of US target location names."""
        return ["WASHINGTON", "NEW YORK", "LOS ANGELES", "CHICAGO", "SEATTLE"]

    def get_ussr_targets(self) -> list[str]:
        """Get list of USSR target location names."""
        return ["MOSCOW", "LENINGRAD", "KIEV", "VLADIVOSTOK", "NOVOSIBIRSK"]

    def launch_wave(self, from_side: str, count: int, targets_hit: set[str]) -> list[tuple[str, int]]:
        """Launch a wave of missiles from one side.

        Args:
            from_side: "US" or "USSR"
            count: Number of missiles to launch
            targets_hit: Set of targets already hit (to avoid duplicates)

        Returns:
            List of (target_name, estimated_casualties) for this wave
        """
        if from_side == "US":
            origin = "US_CENTER"
            available_targets = [t for t in self.get_ussr_targets() if t not in targets_hit]
        else:
            origin = "USSR_CENTER"
            available_targets = [t for t in self.get_us_targets() if t not in targets_hit]

        # If we've hit all unique targets, allow repeats
        if not available_targets:
            available_targets = self.get_ussr_targets() if from_side == "US" else self.get_us_targets()

        wave_results = []
        for i in range(min(count, len(available_targets))):
            target = available_targets[i]
            targets_hit.add(target)

            # Add missile
            self.map.add_missile(origin, target, side=from_side)

            # Estimate casualties (rough numbers for drama)
            casualties = {
                "WASHINGTON": 850_000,
                "NEW YORK": 8_200_000,
                "LOS ANGELES": 4_000_000,
                "CHICAGO": 2_700_000,
                "SEATTLE": 750_000,
                "MOSCOW": 8_500_000,
                "LENINGRAD": 4_200_000,
                "KIEV": 2_600_000,
                "VLADIVOSTOK": 600_000,
                "NOVOSIBIRSK": 1_400_000,
            }.get(target, 500_000)

            wave_results.append((target, casualties))

            if from_side == "US":
                self.ussr_casualties += casualties
            else:
                self.us_casualties += casualties

        return wave_results
