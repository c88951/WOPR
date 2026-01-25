#!/usr/bin/env python3
"""Prototype: Drawille-based world map with arcing missile trajectories."""

from drawille import Canvas
import math
import time
import os

# Canvas size (in braille pixels - each char is 2x4 pixels)
# For a ~100 char wide display, we need ~200 pixels
WIDTH = 180
HEIGHT = 80

# Key locations in pixel coordinates (x, y)
# Scaled for our canvas size
LOCATIONS = {
    # North America
    "WASHINGTON": (35, 28),
    "NEW_YORK": (42, 26),
    "LOS_ANGELES": (22, 32),
    "CHICAGO": (38, 25),

    # Europe/Russia
    "MOSCOW": (120, 22),
    "LONDON": (95, 20),
    "PARIS": (96, 24),

    # Asia
    "BEIJING": (145, 30),
    "TOKYO": (160, 32),
}


def draw_world_map(canvas: Canvas) -> None:
    """Draw a simplified world map outline."""

    # North America (rough outline)
    na_points = [
        (20, 15), (25, 12), (35, 10), (45, 12), (50, 15),
        (48, 20), (52, 25), (48, 30), (45, 35), (40, 38),
        (35, 42), (28, 40), (22, 38), (18, 35), (15, 30),
        (18, 25), (20, 20), (20, 15)
    ]
    draw_polygon(canvas, na_points)

    # South America
    sa_points = [
        (38, 45), (45, 42), (50, 48), (52, 55), (50, 62),
        (45, 70), (40, 72), (35, 68), (32, 60), (34, 52),
        (36, 48), (38, 45)
    ]
    draw_polygon(canvas, sa_points)

    # Europe
    eu_points = [
        (88, 18), (95, 15), (105, 14), (110, 16), (108, 22),
        (100, 26), (92, 28), (88, 25), (88, 18)
    ]
    draw_polygon(canvas, eu_points)

    # Africa
    af_points = [
        (90, 32), (100, 30), (110, 32), (115, 40), (112, 50),
        (105, 58), (95, 60), (88, 55), (85, 45), (88, 38),
        (90, 32)
    ]
    draw_polygon(canvas, af_points)

    # Russia/Asia
    ru_points = [
        (110, 16), (120, 12), (140, 10), (160, 12), (170, 18),
        (168, 25), (160, 28), (150, 30), (140, 28), (130, 26),
        (120, 24), (112, 22), (110, 16)
    ]
    draw_polygon(canvas, ru_points)

    # Australia
    au_points = [
        (148, 55), (158, 52), (165, 55), (168, 62), (162, 68),
        (152, 68), (145, 64), (145, 58), (148, 55)
    ]
    draw_polygon(canvas, au_points)

    # Add location markers
    for name, (x, y) in LOCATIONS.items():
        # Small cross for cities
        canvas.set(x, y)
        canvas.set(x-1, y)
        canvas.set(x+1, y)
        canvas.set(x, y-1)
        canvas.set(x, y+1)


def draw_polygon(canvas: Canvas, points: list[tuple[int, int]]) -> None:
    """Draw a polygon by connecting points with lines."""
    for i in range(len(points)):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % len(points)]
        draw_line(canvas, x1, y1, x2, y2)


def draw_line(canvas: Canvas, x1: int, y1: int, x2: int, y2: int) -> None:
    """Draw a line between two points."""
    steps = max(abs(x2 - x1), abs(y2 - y1), 1)
    for i in range(steps + 1):
        t = i / steps
        x = int(x1 + (x2 - x1) * t)
        y = int(y1 + (y2 - y1) * t)
        canvas.set(x, y)


def draw_arc(canvas: Canvas, x1: int, y1: int, x2: int, y2: int,
             height: float = 0.3, progress: float = 1.0) -> tuple[int, int]:
    """Draw a parabolic arc between two points.

    Args:
        canvas: The drawille canvas
        x1, y1: Start point
        x2, y2: End point
        height: Arc height as fraction of distance (0.3 = 30%)
        progress: How much of the arc to draw (0.0 to 1.0)

    Returns:
        Current position (x, y) of the missile head
    """
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    arc_height = distance * height

    steps = int(distance / 2)
    current_x, current_y = x1, y1

    for i in range(int(steps * progress) + 1):
        t = i / steps

        # Linear interpolation for x
        x = x1 + (x2 - x1) * t

        # Parabolic arc for y (goes up then down)
        # -4 * height * t * (t - 1) gives a nice parabola peaking at t=0.5
        arc_offset = -4 * arc_height * t * (t - 1)
        y = y1 + (y2 - y1) * t - arc_offset

        current_x, current_y = int(x), int(y)
        canvas.set(current_x, current_y)

    return current_x, current_y


def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name != 'nt' else 'cls')


def demo_static_map():
    """Show a static map with all locations marked."""
    print("=" * 60)
    print("STATIC WORLD MAP WITH LOCATIONS")
    print("=" * 60)

    c = Canvas()
    draw_world_map(c)
    print(c.frame())

    print("\nLocations marked with + symbols")
    print("Press Enter to continue...")
    input()


def demo_single_arc():
    """Show a single missile arc."""
    print("=" * 60)
    print("SINGLE MISSILE ARC: Washington -> Moscow")
    print("=" * 60)

    c = Canvas()
    draw_world_map(c)

    # Draw full arc
    x1, y1 = LOCATIONS["WASHINGTON"]
    x2, y2 = LOCATIONS["MOSCOW"]
    draw_arc(c, x1, y1, x2, y2, height=0.4)

    print(c.frame())
    print("\nArc trajectory shown as dotted line")
    print("Press Enter to continue...")
    input()


def demo_animated_missile():
    """Animate a missile flying along an arc."""
    print("=" * 60)
    print("ANIMATED MISSILE: Washington -> Moscow")
    print("=" * 60)
    print("Watch the missile fly...")
    time.sleep(1)

    x1, y1 = LOCATIONS["WASHINGTON"]
    x2, y2 = LOCATIONS["MOSCOW"]

    frames = 20
    for frame in range(frames + 1):
        clear_screen()
        c = Canvas()
        draw_world_map(c)

        progress = frame / frames

        # Draw the trail (arc up to current position)
        missile_x, missile_y = draw_arc(c, x1, y1, x2, y2, height=0.4, progress=progress)

        # Draw missile head (make it bigger)
        if progress < 1.0:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    c.set(missile_x + dx, missile_y + dy)

        print("                    GLOBAL THERMONUCLEAR WAR")
        print(c.frame())
        print(f"\nMissile progress: {int(progress * 100)}%")

        if progress >= 1.0:
            print("*** IMPACT: MOSCOW ***")

        time.sleep(0.15)

    print("\nPress Enter to continue...")
    input()


def demo_escalation():
    """Demo escalating war with multiple missiles."""
    print("=" * 60)
    print("ESCALATION DEMO")
    print("=" * 60)
    time.sleep(1)

    # Waves: (from_locations, to_locations)
    waves = [
        # US fires 1
        ([("WASHINGTON", "MOSCOW")], "US LAUNCHES 1 MISSILE"),
        # USSR fires 2
        ([("MOSCOW", "WASHINGTON"), ("MOSCOW", "NEW_YORK")], "USSR RETALIATES: 2 MISSILES"),
        # US fires 3
        ([("WASHINGTON", "MOSCOW"), ("LOS_ANGELES", "BEIJING"), ("CHICAGO", "LONDON")],
         "US COUNTER-STRIKE: 3 MISSILES"),
    ]

    all_trails = []  # Keep track of all missile trails

    for wave_missiles, wave_title in waves:
        print(f"\n*** {wave_title} ***")
        time.sleep(0.5)

        # Animate this wave
        frames = 15
        for frame in range(frames + 1):
            clear_screen()
            c = Canvas()
            draw_world_map(c)

            # Draw all previous trails
            for (trail_start, trail_end) in all_trails:
                x1, y1 = LOCATIONS[trail_start]
                x2, y2 = LOCATIONS[trail_end]
                draw_arc(c, x1, y1, x2, y2, height=0.4, progress=1.0)
                # Mark impact
                c.set(x2, y2)
                c.set(x2-1, y2)
                c.set(x2+1, y2)
                c.set(x2, y2-1)
                c.set(x2, y2+1)

            progress = frame / frames

            # Draw current wave missiles
            for (start_loc, end_loc) in wave_missiles:
                x1, y1 = LOCATIONS[start_loc]
                x2, y2 = LOCATIONS[end_loc]
                missile_x, missile_y = draw_arc(c, x1, y1, x2, y2, height=0.4, progress=progress)

                # Draw missile head
                if progress < 1.0:
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            c.set(missile_x + dx, missile_y + dy)

            print("                    GLOBAL THERMONUCLEAR WAR")
            print(c.frame())
            print(f"\n{wave_title} - Progress: {int(progress * 100)}%")

            time.sleep(0.1)

        # Add this wave's missiles to the trail history
        all_trails.extend(wave_missiles)

        print("*** IMPACTS ***")
        time.sleep(0.8)

    print("\n" + "=" * 60)
    print("WINNER: NONE")
    print("=" * 60)


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("DRAWILLE WORLD MAP PROTOTYPE")
    print("Testing Braille graphics for missile trajectories")
    print("=" * 60)
    print("\nThis prototype demonstrates:")
    print("1. World map rendered with Braille characters")
    print("2. Parabolic arc missile trajectories")
    print("3. Animated missiles in flight")
    print("4. Escalating war simulation")
    print("\nPress Enter to start...")
    input()

    demo_static_map()
    demo_single_arc()
    demo_animated_missile()
    demo_escalation()

    print("\n" + "=" * 60)
    print("PROTOTYPE COMPLETE")
    print("=" * 60)
    print("\nWhat do you think? Should we integrate this into GTW?")


if __name__ == "__main__":
    main()
