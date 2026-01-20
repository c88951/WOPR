"""ASCII world map with Drawille missile trajectory overlays."""

from drawille import Canvas
from dataclasses import dataclass
import math


@dataclass
class Missile:
    """A missile in flight with arc trajectory."""
    start: tuple[int, int]  # Pixel coordinates (for Drawille)
    end: tuple[int, int]    # Pixel coordinates (for Drawille)
    progress: float = 0.0   # 0.0 = launched, 1.0 = impact
    side: str = "US"        # Which side fired
    arc_height: float = 0.30  # Arc height as fraction of distance

    @property
    def impacted(self) -> bool:
        return self.progress >= 1.0

    def get_position(self) -> tuple[int, int]:
        """Get current position along the arc in pixel coordinates."""
        x1, y1 = self.start
        x2, y2 = self.end
        t = self.progress

        # Linear interpolation for x
        x = x1 + (x2 - x1) * t

        # Parabolic arc for y (negative because screen y increases downward)
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        arc_h = distance * self.arc_height
        arc_offset = -4 * arc_h * t * (t - 1)
        y = y1 + (y2 - y1) * t - arc_offset

        return int(x), int(y)

    def get_arc_points(self, steps: int = 60) -> list[tuple[int, int]]:
        """Get all points along the FULL arc trajectory (shown like WarGames)."""
        points = []
        x1, y1 = self.start
        x2, y2 = self.end
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        arc_h = distance * self.arc_height

        # Draw the complete predicted arc path
        for i in range(steps + 1):
            t = i / steps
            x = x1 + (x2 - x1) * t
            arc_offset = -4 * arc_h * t * (t - 1)
            y = y1 + (y2 - y1) * t - arc_offset
            points.append((int(x), int(y)))

        return points


@dataclass
class Explosion:
    """An explosion animation at a location."""
    x: int  # Pixel x
    y: int  # Pixel y
    frame: int = 0
    max_frames: int = 8

    @property
    def finished(self) -> bool:
        return self.frame >= self.max_frames

    def get_radius(self) -> int:
        """Get current explosion radius in pixels."""
        if self.frame < 4:
            return (self.frame + 1) * 2
        else:
            return max(2, 8 - (self.frame - 4) * 2)


class DrawilleWarMap:
    """ASCII world map with Drawille braille missile trajectories overlaid."""

    # Vertical offset to make room for missile arcs above the map
    # 32 pixels = 8 character rows of arc space
    Y_OFFSET = 32

    # Drawille canvas dimensions (2x width, 4x height of ASCII for braille)
    # Extra height added for arc space above map
    CANVAS_WIDTH = 156   # 78 * 2
    CANVAS_HEIGHT = 128  # (24 + 8) * 4 = 32 * 4

    # ASCII map dimensions
    ASCII_WIDTH = 78
    ASCII_HEIGHT = 24
    ARC_ROWS = 8  # Extra rows above map for arcs

    # Key locations in PIXEL coordinates (for Drawille)
    # Y values offset by Y_OFFSET to leave room for arcs above
    # Positioned on the map: x = ascii_col * 2, y = (ascii_row * 4) + Y_OFFSET
    LOCATIONS = {
        # USA (left side of map)
        "WASHINGTON": (44, 52),    # col 22, row 5 + offset
        "NEW_YORK": (52, 48),      # col 26, row 4 + offset
        "LOS_ANGELES": (20, 56),   # col 10, row 6 + offset
        "CHICAGO": (40, 48),       # col 20, row 4 + offset
        "SEATTLE": (16, 44),       # col 8, row 3 + offset
        "US_CENTER": (36, 52),     # col 18, row 5 + offset

        # USSR/Russia (right side of map)
        "MOSCOW": (110, 44),       # col 55, row 3 + offset
        "LENINGRAD": (100, 40),    # col 50, row 2 + offset
        "KIEV": (104, 52),         # col 52, row 5 + offset
        "VLADIVOSTOK": (144, 56),  # col 72, row 6 + offset
        "NOVOSIBIRSK": (124, 48),  # col 62, row 4 + offset
        "USSR_CENTER": (116, 48),  # col 58, row 4 + offset

        # Other
        "LONDON": (84, 44),        # col 42, row 3 + offset
        "BEIJING": (130, 60),      # col 65, row 7 + offset
    }

    # ASCII World Map - 78 chars wide x 24 lines
    ASCII_MAP = [
        "                                                                              ",
        "          . _..::__:  ,-\"-\"._               ,_._._          _,_             ",
        "  _.___ _ _<_>`!(._`.`-.    /        _._     `_ ,_/  '  '-._.---.-.___        ",
        ">.{     \" \" `-==,',_ \\{  \\  / {)     / _ \">_,-' `                           ",
        "  \\_.:--.       `._ )`^-. \"'       , [_/(  __,/-'                           ",
        " '\"'     \\         \"    _L        _,--'                 )     /. (|         ",
        "          |           ,'         _)_.\\\\._                  _,' /  '          ",
        "          `.         /          [_/_'` `\"(               <'}  )             ",
        "           \\\\    .-. )           /   `-'\"..' `:.          _)  '              ",
        "    `        \\  (  `(           /         `:\\  > \\  ,-^.  /' '               ",
        "              `._,   \"\"        |           \\`'   \\|   ?_)  {\\                ",
        "                 `=.---.       `._        ,'     \"`  |' ,- '.               ",
        "                   |    `-.         |     /          `:`<__|--.\\_            ",
        "                   (        >       .     | ,          `=.__.`-'\\            ",
        "                    `.     /        |     |{|              ,-.,\\     .       ",
        "                     |   ,'          \\   / `'            ,\"     \\            ",
        "                     |  /            |_'                |  __  /             ",
        "                     | |                                '-'  `-'   \\.        ",
        "                     |/                                        \"   /         ",
        "                     \\.                                          '          ",
        "                                                                              ",
        "                      ,/   ______.--.-._  _..--..-----.--._.                  ",
        "     ,-----\"-..?----_/ ),-'\"             \"                  (               ",
        "-.._                   `-----'                               `-              ",
    ]

    def __init__(self):
        self.missiles: list[Missile] = []
        self.explosions: list[Explosion] = []
        self.impact_sites: list[tuple[int, int]] = []  # Pixel coordinates

    def add_missile(self, origin: str, target: str, side: str = "US") -> Missile:
        """Add a missile from origin to target location."""
        start = self.LOCATIONS.get(origin.upper(), self.LOCATIONS["US_CENTER"])
        end = self.LOCATIONS.get(target.upper(), self.LOCATIONS["USSR_CENTER"])
        missile = Missile(start=start, end=end, side=side)
        self.missiles.append(missile)
        return missile

    def advance(self, step: float = 0.08) -> list[Missile]:
        """Advance all missiles and explosions. Returns newly impacted missiles."""
        newly_impacted = []

        for missile in self.missiles:
            if not missile.impacted:
                missile.progress = min(1.0, missile.progress + step)
                if missile.impacted:
                    newly_impacted.append(missile)
                    # Add explosion at impact site
                    x, y = missile.end
                    self.explosions.append(Explosion(x, y))
                    self.impact_sites.append((x, y))

        # Advance explosions
        for exp in self.explosions:
            exp.frame += 1

        # Remove finished explosions
        self.explosions = [e for e in self.explosions if not e.finished]

        return newly_impacted

    def has_active_missiles(self) -> bool:
        """Check if any missiles are still in flight."""
        return any(not m.impacted for m in self.missiles)

    def has_active_animations(self) -> bool:
        """Check if any animations are running."""
        return self.has_active_missiles() or len(self.explosions) > 0

    def clear(self) -> None:
        """Clear all missiles and explosions."""
        self.missiles = []
        self.explosions = []
        self.impact_sites = []

    def _draw_circle(self, canvas: Canvas, cx: int, cy: int, radius: int) -> None:
        """Draw a filled circle on the canvas."""
        for angle in range(0, 360, 8):
            rad = math.radians(angle)
            for r in range(1, radius + 1):
                x = int(cx + r * math.cos(rad))
                y = int(cy + r * math.sin(rad))
                if 0 <= x < self.CANVAS_WIDTH and 0 <= y < self.CANVAS_HEIGHT:
                    canvas.set(x, y)

    def _pixel_to_char(self, px: int, py: int) -> tuple[int, int]:
        """Convert pixel coordinates to ASCII character coordinates."""
        return px // 2, py // 4

    def render_frame(self) -> str:
        """Render the current frame with Drawille missiles overlaid on ASCII map."""
        # Create Drawille canvas for missile trajectories
        canvas = Canvas()
        min_y_pixel = self.CANVAS_HEIGHT  # Track minimum y for alignment

        # Draw all missile arc trajectories (full predicted paths like WarGames)
        for missile in self.missiles:
            for px, py in missile.get_arc_points():
                if 0 <= px < self.CANVAS_WIDTH and 0 <= py < self.CANVAS_HEIGHT:
                    canvas.set(px, py)
                    min_y_pixel = min(min_y_pixel, py)

        # Draw missile heads (current position) - larger dot
        for missile in self.missiles:
            if not missile.impacted:
                mx, my = missile.get_position()
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        px, py = mx + dx, my + dy
                        if 0 <= px < self.CANVAS_WIDTH and 0 <= py < self.CANVAS_HEIGHT:
                            canvas.set(px, py)
                            min_y_pixel = min(min_y_pixel, py)

        # Draw explosions as expanding circles
        for exp in self.explosions:
            self._draw_circle(canvas, exp.x, exp.y, exp.get_radius())
            min_y_pixel = min(min_y_pixel, exp.y - exp.get_radius())

        # Get the Drawille frame as lines
        # Note: canvas.frame() starts from the minimum y with content, not y=0
        # We need to track this offset to align the overlay correctly
        drawille_frame = canvas.frame()
        drawille_lines = drawille_frame.split('\n')
        min_y_char = max(0, min_y_pixel // 4)  # Starting char row of drawille content

        # Start with blank lines for arc space, then ASCII map
        map_chars = []
        # Add blank lines at top for missile arc space
        for _ in range(self.ARC_ROWS):
            map_chars.append([' '] * self.ASCII_WIDTH)
        # Add the actual map
        for line in self.ASCII_MAP:
            map_chars.append(list(line))

        # Ensure all lines are same length
        max_len = max(len(line) for line in map_chars)
        for line in map_chars:
            while len(line) < max_len:
                line.append(' ')

        # Track positions with colored content (braille missiles and impacts)
        colored_content: dict[tuple[int, int], str] = {}

        # Overlay Drawille braille characters onto ASCII map (RED for missiles)
        # drawille_lines[0] corresponds to character row min_y_char, not row 0
        for dy, dline in enumerate(drawille_lines):
            actual_row = dy + min_y_char  # Offset to get actual map_chars row
            if actual_row >= len(map_chars):
                break
            for dx, dchar in enumerate(dline):
                if dx >= max_len:
                    break
                # Only overlay if the braille character has dots (not blank)
                if dchar != ' ' and ord(dchar) >= 0x2800:
                    colored_content[(dx, actual_row)] = f'[red]{dchar}[/red]'

        # Mark permanent impact sites with X (bold red)
        for px, py in self.impact_sites:
            cx, cy = self._pixel_to_char(px, py)
            if 0 <= cx < max_len and 0 <= cy < len(map_chars):
                # Don't overwrite active explosions
                still_exploding = any(
                    self._pixel_to_char(e.x, e.y) == (cx, cy)
                    for e in self.explosions
                )
                if not still_exploding:
                    colored_content[(cx, cy)] = '[bold red]X[/bold red]'

        # Build result with proper escaping for Textual markup
        # Textual uses \[ to escape brackets (not [[ like Rich)
        result_lines = []
        result_lines.append("                    [bold]GLOBAL THERMONUCLEAR WAR[/bold]")
        result_lines.append("")
        # Arc space is built into map_chars (first ARC_ROWS lines are blank)

        for y, line in enumerate(map_chars):
            output_chars = []
            for x, char in enumerate(line):
                if (x, y) in colored_content:
                    # Colored markup (red braille or red X)
                    # Make sure previous char isn't a backslash that would escape it
                    if output_chars and output_chars[-1].endswith('\\'):
                        output_chars.append(' ')  # Add space to break escape
                    output_chars.append(colored_content[(x, y)])
                else:
                    # Escape special chars for Textual markup (uses \[ not [[)
                    if char == '[':
                        output_chars.append('\\[')
                    elif char == ']':
                        output_chars.append('\\]')
                    elif char == '\\':
                        output_chars.append('\\\\')
                    else:
                        output_chars.append(char)
            result_lines.append(''.join(output_chars))

        return '\n'.join(result_lines)

    def render_static(self) -> str:
        """Render just the static map with Textual markup escaping."""
        # Title, then arc space, then map
        lines = ["                    [bold]GLOBAL THERMONUCLEAR WAR[/bold]", ""]
        # Add arc space (blank lines where missile arcs can render)
        for _ in range(self.ARC_ROWS):
            lines.append("")
        for line in self.ASCII_MAP:
            # Escape special chars for Textual markup (uses \[ not [[)
            escaped = line.replace('\\', '\\\\').replace('[', '\\[').replace(']', '\\]')
            lines.append(escaped)
        return '\n'.join(lines)


class DrawilleWarAnimator:
    """Manages the escalating war animation."""

    # Casualty estimates by city
    CASUALTIES = {
        "WASHINGTON": 850_000,
        "NEW_YORK": 8_200_000,
        "LOS_ANGELES": 4_000_000,
        "CHICAGO": 2_700_000,
        "SEATTLE": 750_000,
        "MOSCOW": 8_500_000,
        "LENINGRAD": 4_200_000,
        "KIEV": 2_600_000,
        "VLADIVOSTOK": 600_000,
        "NOVOSIBIRSK": 1_400_000,
    }

    US_TARGETS = ["WASHINGTON", "NEW_YORK", "LOS_ANGELES", "CHICAGO", "SEATTLE"]
    USSR_TARGETS = ["MOSCOW", "LENINGRAD", "KIEV", "VLADIVOSTOK", "NOVOSIBIRSK"]

    def __init__(self, war_map: DrawilleWarMap):
        self.map = war_map
        self.us_casualties = 0
        self.ussr_casualties = 0
        self.targets_hit: set[str] = set()

    def launch_wave(self, from_side: str, count: int) -> list[tuple[str, int]]:
        """Launch a wave of missiles.

        Returns list of (target_name, casualties) for this wave.
        """
        if from_side == "US":
            origin = "US_CENTER"
            available = [t for t in self.USSR_TARGETS if t not in self.targets_hit]
            if not available:
                available = self.USSR_TARGETS
        else:
            origin = "USSR_CENTER"
            available = [t for t in self.US_TARGETS if t not in self.targets_hit]
            if not available:
                available = self.US_TARGETS

        results = []
        for i in range(min(count, len(available))):
            target = available[i]
            self.targets_hit.add(target)
            self.map.add_missile(origin, target, side=from_side)

            casualties = self.CASUALTIES.get(target, 500_000)
            results.append((target, casualties))

            if from_side == "US":
                self.ussr_casualties += casualties
            else:
                self.us_casualties += casualties

        return results
