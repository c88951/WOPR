"""World map rendering for Global Thermonuclear War."""


class WorldMap:
    """ASCII world map for GTW display."""

    # Simplified ASCII world map
    MAP = r"""
                              GLOBAL THERMONUCLEAR WAR
    ╭────────────────────────────────────────────────────────────────────────╮
    │                                    .                                   │
    │            ▄▄▄▄▄▄                 ███                                  │
    │     ▄▄█████████████▄▄        ▄██████████▄                             │
    │   ▄███████████████████▄    ▄████████████████▄         ▄▄▄             │
    │  ████████████████████████████████████████████████▄  ▄█████            │
    │  █████████████████████████████████████████████████████████▄           │
    │   ▀███████████████████████████████████████████████████████▓           │
    │     ▀█████████████████████████████████████████████████████            │
    │       ▀███████████████████████████████████████████████▀▀              │
    │          ▀▀█████████████████████████████████████▀▀                    │
    │              ▀▀███████████████████████████▀▀                          │
    │                   ▀▀▀███████  ███████▀▀▀                              │
    │                          ▀▀    ▀▀                                     │
    │                                         ▄▄▄▄                          │
    │                                     ▄████████▄                        │
    │                                    ██████████████                     │
    │                                     ▀██████████▀                      │
    │                                        ▀▀▀▀▀                          │
    ╰────────────────────────────────────────────────────────────────────────╯"""

    # Alternative compact map
    MAP_COMPACT = r"""
                         GLOBAL THERMONUCLEAR WAR
   ╭──────────────────────────────────────────────────────────╮
   │      __                     _____                        │
   │   .-'  `'.    .--.        .'     '.    .---.             │
   │  /   USA  \  |    |      /  USSR   \  /     \            │
   │  |        |  |    |     |          | |       |           │
   │   \      /    '--'       \        /   \     /            │
   │    '----'                  '----'      '---'             │
   │                                                          │
   │    ____                                    ___           │
   │   /    \                                  /   \          │
   │  |      |                                |     |         │
   │   \____/                                  \___/          │
   ╰──────────────────────────────────────────────────────────╯"""

    def __init__(self, style: str = "default") -> None:
        self._style = style
        self._markers: list[tuple[int, int, str]] = []

    def render(self) -> str:
        """Render the world map."""
        if self._style == "compact":
            return self.MAP_COMPACT
        return self.MAP

    def add_marker(self, x: int, y: int, char: str = "*") -> None:
        """Add a marker to the map."""
        self._markers.append((x, y, char))

    def clear_markers(self) -> None:
        """Clear all markers."""
        self._markers = []

    def render_with_markers(self) -> str:
        """Render map with markers."""
        lines = self.render().split("\n")

        for x, y, char in self._markers:
            if 0 <= y < len(lines) and 0 <= x < len(lines[y]):
                line = list(lines[y])
                line[x] = char
                lines[y] = "".join(line)

        return "\n".join(lines)

    @staticmethod
    def render_strike_animation_frame(frame: int) -> str:
        """Render a single frame of strike animation."""
        # Simple expanding explosion
        explosions = [
            "·",
            "*",
            "✦",
            "★",
            "✸",
            "💥",
            "◉",
            "○",
            "·",
        ]
        return explosions[frame % len(explosions)]


class MissileTrajectory:
    """Calculate and render missile trajectories."""

    @staticmethod
    def calculate_path(
        start: tuple[float, float],
        end: tuple[float, float],
        steps: int = 20
    ) -> list[tuple[float, float]]:
        """Calculate great circle path between two points.

        For simplicity, using linear interpolation.
        A real implementation would use spherical coordinates.
        """
        path = []
        for i in range(steps + 1):
            t = i / steps
            lat = start[0] + (end[0] - start[0]) * t
            lon = start[1] + (end[1] - start[1]) * t
            path.append((lat, lon))
        return path

    @staticmethod
    def lat_lon_to_map(lat: float, lon: float, map_width: int, map_height: int) -> tuple[int, int]:
        """Convert latitude/longitude to map coordinates."""
        # Simple Mercator-ish projection
        x = int((lon + 180) / 360 * map_width)
        y = int((90 - lat) / 180 * map_height)
        return (x, y)
