"""Animation effects for WOPR terminal."""

import asyncio
import random
from typing import Callable, Awaitable


class AnimationEngine:
    """Engine for terminal animations and effects."""

    # Modem connection noise characters
    NOISE_CHARS = "░▒▓█▀▄▌▐│┤╡╢╖╕╣║╗╝╜╛┐└┴┬├─┼╞╟╚╔╩╦╠═╬╧╨╤╥╙╘╒╓╫╪┘┌"

    def __init__(self, output_callback: Callable[[str], Awaitable[None]]) -> None:
        """Initialize with an async callback for output."""
        self._output = output_callback

    async def type_text(
        self,
        text: str,
        chars_per_second: int = 30,
        add_newline: bool = True
    ) -> None:
        """Type text character by character."""
        if chars_per_second <= 0:
            await self._output(text + ("\n" if add_newline else ""))
            return

        delay = 1.0 / chars_per_second
        for char in text:
            await self._output(char)
            await asyncio.sleep(delay)

        if add_newline:
            await self._output("\n")

    async def line_noise(self, duration: float = 0.5, intensity: int = 5) -> None:
        """Display random noise characters."""
        end_time = asyncio.get_event_loop().time() + duration
        while asyncio.get_event_loop().time() < end_time:
            noise = "".join(random.choices(self.NOISE_CHARS, k=intensity))
            await self._output(f"\r{noise}")
            await asyncio.sleep(0.05)
        await self._output("\r" + " " * intensity + "\r")

    async def progress_dots(self, count: int = 3, delay: float = 0.5) -> None:
        """Display loading dots."""
        for _ in range(count):
            await self._output(".")
            await asyncio.sleep(delay)
        await self._output("\n")

    async def flash_screen(self, times: int = 1, flash_char: str = "█") -> None:
        """Flash the screen (for explosions, etc.)."""
        for _ in range(times):
            # This would ideally flash the whole screen
            await self._output(flash_char * 40 + "\n")
            await asyncio.sleep(0.1)
            await self._output("\033[2K\033[A")  # Clear line and move up
            await asyncio.sleep(0.1)

    async def countdown(self, start: int, delay: float = 1.0) -> None:
        """Display a countdown."""
        for i in range(start, 0, -1):
            await self._output(f"\r{i:3d}")
            await asyncio.sleep(delay)
        await self._output("\r  0\n")

    async def scroll_text(self, lines: list[str], delay: float = 0.1) -> None:
        """Scroll through lines of text."""
        for line in lines:
            await self._output(line + "\n")
            await asyncio.sleep(delay)

    async def blink_text(
        self,
        text: str,
        times: int = 3,
        on_time: float = 0.5,
        off_time: float = 0.3
    ) -> None:
        """Blink text on and off."""
        blank = " " * len(text)
        for _ in range(times):
            await self._output(f"\r{text}")
            await asyncio.sleep(on_time)
            await self._output(f"\r{blank}")
            await asyncio.sleep(off_time)
        await self._output(f"\r{text}\n")

    async def modem_handshake(self) -> None:
        """Simulate modem connection handshake visuals."""
        phases = [
            ("DIALING", 1.5),
            ("RINGING", 2.0),
            ("CONNECTING", 1.5),
            ("HANDSHAKE", 1.0),
            ("CONNECTED 2400", 0.5),
        ]

        for phase, duration in phases:
            await self._output(f"\r{phase}")
            await asyncio.sleep(duration / 3)
            await self.line_noise(duration * 0.6, intensity=20)
            await asyncio.sleep(duration / 3)

        await self._output("\n\nCONNECTION ESTABLISHED\n\n")

    async def war_map_missile(
        self,
        start_pos: tuple[int, int],
        end_pos: tuple[int, int],
        steps: int = 20,
        delay: float = 0.1
    ) -> list[tuple[int, int]]:
        """Calculate missile trajectory points for animation."""
        trajectory = []
        for i in range(steps + 1):
            t = i / steps
            x = int(start_pos[0] + (end_pos[0] - start_pos[0]) * t)
            y = int(start_pos[1] + (end_pos[1] - start_pos[1]) * t)
            trajectory.append((x, y))
        return trajectory


class TextEffects:
    """Static text effect utilities."""

    @staticmethod
    def center_text(text: str, width: int) -> str:
        """Center text within a given width."""
        lines = text.split("\n")
        centered = [line.center(width) for line in lines]
        return "\n".join(centered)

    @staticmethod
    def box_text(text: str, title: str = "") -> str:
        """Wrap text in a decorative box."""
        lines = text.split("\n")
        max_width = max(len(line) for line in lines)
        if title:
            max_width = max(max_width, len(title) + 4)

        top = "╔" + "═" * (max_width + 2) + "╗"
        if title:
            title_line = "║ " + title.center(max_width) + " ║"
            separator = "╠" + "═" * (max_width + 2) + "╣"
            top = top + "\n" + title_line + "\n" + separator
        bottom = "╚" + "═" * (max_width + 2) + "╝"

        content_lines = ["║ " + line.ljust(max_width) + " ║" for line in lines]

        return top + "\n" + "\n".join(content_lines) + "\n" + bottom

    @staticmethod
    def create_progress_bar(
        current: int,
        total: int,
        width: int = 30,
        filled: str = "█",
        empty: str = "░"
    ) -> str:
        """Create a text progress bar."""
        if total == 0:
            percentage = 0
        else:
            percentage = current / total
        filled_width = int(width * percentage)
        empty_width = width - filled_width
        bar = filled * filled_width + empty * empty_width
        return f"[{bar}] {percentage * 100:.1f}%"
