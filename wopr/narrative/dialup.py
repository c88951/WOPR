"""Modem dialup sequence for WOPR."""

import asyncio
import random
from typing import Callable, Awaitable


class DialupSequence:
    """Simulates modem dial-up connection to WOPR."""

    # Modem status messages
    DIAL_TONE = "DIAL TONE DETECTED"
    DIALING = "DIALING..."
    RINGING = "RINGING..."
    CARRIER = "CARRIER DETECTED"
    CONNECTING = "CONNECTING..."
    HANDSHAKE = "HANDSHAKE IN PROGRESS"
    CONNECTED = "CONNECTED 2400"
    ESTABLISHED = "CONNECTION ESTABLISHED"

    # Phone number (for display)
    PHONE_NUMBER = "311-555-8723"

    # Noise characters for modem sound visualization
    NOISE_CHARS = "░▒▓█▀▄▌▐│┤╡╢╖╕╣║╗╝╜╛┐└┴┬├─┼╞╟╚╔╩╦╠═╬"

    def __init__(
        self,
        output_callback: Callable[[str], Awaitable[None]],
        audio_manager=None
    ) -> None:
        """Initialize dialup sequence.

        Args:
            output_callback: Async function to call with output text
            audio_manager: Optional AudioManager for sound effects
        """
        self._output = output_callback
        self._audio = audio_manager

    async def _display(self, text: str, delay: float = 0) -> None:
        """Display text with optional delay."""
        await self._output(text)
        if delay > 0:
            await asyncio.sleep(delay)

    async def _noise(self, duration: float, intensity: int = 30) -> None:
        """Display modem noise characters."""
        end_time = asyncio.get_event_loop().time() + duration
        while asyncio.get_event_loop().time() < end_time:
            noise = "".join(random.choices(self.NOISE_CHARS, k=intensity))
            await self._output(f"\r{noise}")
            await asyncio.sleep(0.05)
        await self._output("\r" + " " * intensity + "\r")

    async def _play_sound(self, sound_name: str, blocking: bool = False) -> None:
        """Play a sound effect if audio manager is available."""
        if self._audio:
            self._audio.play(sound_name, blocking=blocking)

    async def run(self) -> bool:
        """Run the full dialup sequence.

        Returns:
            True if connection successful
        """
        await self._display("\n")
        await self._display("╔═══════════════════════════════════════╗\n")
        await self._display("║       MODEM CONNECTION INTERFACE      ║\n")
        await self._display("╚═══════════════════════════════════════╝\n\n")

        # Dial tone
        await self._display(f"STATUS: {self.DIAL_TONE}\n", 0.5)
        await self._play_sound("modem_dial")

        # Show phone number being dialed
        await self._display(f"\nDIALING: ", 0.3)
        for digit in self.PHONE_NUMBER:
            await self._display(digit, 0.15)
        await self._display("\n\n")

        # Ringing
        for i in range(3):
            await self._display(f"STATUS: {self.RINGING} ({i + 1})\n", 1.0)

        # Carrier detected
        await self._display(f"\nSTATUS: {self.CARRIER}\n", 0.5)
        await self._play_sound("modem_connect")

        # Handshake with noise
        await self._display(f"STATUS: {self.HANDSHAKE}\n\n")
        await self._noise(2.0, intensity=40)

        # Connection progress
        await self._display(f"\nSTATUS: {self.CONNECTING}\n")
        for i in range(5):
            progress = "█" * (i + 1) + "░" * (4 - i)
            await self._display(f"\r[{progress}] {(i + 1) * 20}%")
            await asyncio.sleep(0.3)
        await self._display("\n")

        # Connected
        await self._display(f"\n{self.CONNECTED}\n", 0.5)
        await self._display(f"BAUD RATE: 2400\n", 0.2)
        await self._display(f"DATA BITS: 8\n", 0.2)
        await self._display(f"PARITY: NONE\n", 0.2)
        await self._display(f"STOP BITS: 1\n\n", 0.5)

        # Final connection message
        await self._display("═" * 40 + "\n")
        await self._display(f"    {self.ESTABLISHED}\n")
        await self._display("═" * 40 + "\n\n")

        await asyncio.sleep(0.5)
        return True


class QuickDialup:
    """Abbreviated dialup for skip-intro mode."""

    def __init__(self, output_callback: Callable[[str], Awaitable[None]]) -> None:
        self._output = output_callback

    async def run(self) -> bool:
        """Quick connection message."""
        await self._output("\nCONNECTION ESTABLISHED - 2400 BAUD\n\n")
        return True
