"""Global Thermonuclear War - the main game."""

from typing import Any, Callable, Awaitable
import asyncio
import random

from ...base import BaseGame, GameResult
from .targets import TargetDatabase, Target
from .map import WorldMap
from .simulation import WarSimulation


class GlobalThermonuclearWar(BaseGame):
    """Global Thermonuclear War simulation."""

    NAME = "GLOBAL THERMONUCLEAR WAR"
    DESCRIPTION = "Strategic nuclear warfare simulation"
    INSTRUCTIONS = """
GLOBAL THERMONUCLEAR WAR

Select targets for nuclear strikes.
Commands:
  LIST [US/USSR]  - List available targets
  TARGET <name>   - Select a target
  LAUNCH          - Execute strike
  STATUS          - Show current status
  ABORT           - Abort mission
  QUIT            - Exit game

Target types: CITY, MILITARY, INDUSTRIAL
"""

    def __init__(
        self,
        output_callback: Callable[[str], Awaitable[None]],
        input_callback: Callable[[], Awaitable[str]],
        voice=None,
        audio=None,
    ) -> None:
        super().__init__(output_callback, input_callback, voice, audio)
        self._targets = TargetDatabase()
        self._map = WorldMap()
        self._simulation = WarSimulation()
        self._player_side = ""
        self._selected_targets: list[Target] = []
        self._defcon = 5
        self._launched = False

    async def _show_side_selection(self) -> str | None:
        """Show side selection menu."""
        await self.output("\nWHICH SIDE DO YOU WANT?\n\n")
        await self.output("    1. UNITED STATES\n")
        await self.output("    2. SOVIET UNION\n\n")

        while True:
            choice = await self.input("SELECT (1/2): ")
            choice = choice.strip()

            if choice in {"1", "US", "USA", "UNITED STATES"}:
                return "US"
            elif choice in {"2", "USSR", "SOVIET", "SOVIET UNION"}:
                return "USSR"
            elif choice.upper() in {"QUIT", "Q", "ABORT"}:
                return None
            else:
                await self.output("INVALID SELECTION\n")

    async def _show_status(self) -> None:
        """Display current game status."""
        enemy = "USSR" if self._player_side == "US" else "US"

        await self.output("\n" + "=" * 50 + "\n")
        await self.output(f"DEFCON LEVEL: {self._defcon}\n")
        await self.output(f"YOUR SIDE: {self._player_side}\n")
        await self.output(f"TARGETS SELECTED: {len(self._selected_targets)}\n")

        if self._selected_targets:
            await self.output("\nSELECTED TARGETS:\n")
            for t in self._selected_targets:
                await self.output(f"  - {t.name} ({t.target_type})\n")

        await self.output("=" * 50 + "\n")

    async def _list_targets(self, side: str = "") -> None:
        """List available targets."""
        enemy = "USSR" if self._player_side == "US" else "US"
        if side:
            enemy = side

        targets = self._targets.get_targets_for_side(enemy)

        await self.output(f"\n{enemy} TARGETS:\n")
        await self.output("-" * 40 + "\n")

        # Group by type
        cities = [t for t in targets if t.target_type == "CITY"]
        military = [t for t in targets if t.target_type == "MILITARY"]
        industrial = [t for t in targets if t.target_type == "INDUSTRIAL"]

        if cities:
            await self.output("\nCITIES:\n")
            for t in cities[:10]:  # Show first 10
                await self.output(f"  {t.name} (Pop: {t.population:,})\n")

        if military:
            await self.output("\nMILITARY INSTALLATIONS:\n")
            for t in military[:10]:
                await self.output(f"  {t.name}\n")

        if industrial:
            await self.output("\nINDUSTRIAL CENTERS:\n")
            for t in industrial[:5]:
                await self.output(f"  {t.name}\n")

        await self.output(f"\nTOTAL TARGETS AVAILABLE: {len(targets)}\n")

    async def _select_target(self, target_name: str) -> bool:
        """Select a target for strike."""
        enemy = "USSR" if self._player_side == "US" else "US"
        target = self._targets.find_target(target_name, enemy)

        if not target:
            await self.output(f"TARGET NOT FOUND: {target_name}\n")
            return False

        if target in self._selected_targets:
            await self.output(f"TARGET ALREADY SELECTED: {target.name}\n")
            return False

        self._selected_targets.append(target)
        await self.output(f"TARGET ACQUIRED: {target.name}\n")

        # Escalate DEFCON
        if self._defcon > 1 and len(self._selected_targets) > 2:
            self._defcon -= 1
            await self.output(f"DEFCON LEVEL NOW: {self._defcon}\n")
            await self.play_sound("defcon_change")

        return True

    async def _execute_launch(self) -> dict[str, Any]:
        """Execute the nuclear strike."""
        if not self._selected_targets:
            await self.output("NO TARGETS SELECTED\n")
            return {"launched": False}

        self._launched = True
        await self.output("\n" + "=" * 50 + "\n")
        await self.output("        *** LAUNCH SEQUENCE INITIATED ***\n")
        await self.output("=" * 50 + "\n\n")
        await self.play_sound("missile_launch")

        # Set DEFCON to 1
        self._defcon = 1
        await self.output("DEFCON 1 - MAXIMUM READINESS\n\n")

        # Show world map with attack
        await self.output(self._map.render() + "\n")

        # Animate missile launches
        await self.output("MISSILES LAUNCHED:\n")
        for target in self._selected_targets:
            await self.output(f"  -> {target.name}...")
            await asyncio.sleep(0.3)
            await self.output(" AWAY\n")
            await self.play_sound("missile_launch")

        await asyncio.sleep(1.0)

        # Calculate casualties
        total_casualties = 0
        await self.output("\n*** IMPACT REPORTS ***\n\n")

        for target in self._selected_targets:
            await asyncio.sleep(0.5)
            casualties = target.population if target.target_type == "CITY" else random.randint(1000, 50000)
            total_casualties += casualties
            await self.output(f"IMPACT: {target.name}\n")
            await self.output(f"  ESTIMATED CASUALTIES: {casualties:,}\n")
            await self.play_sound("explosion")

        # Enemy retaliation
        await asyncio.sleep(1.0)
        await self.output("\n*** ENEMY RETALIATION DETECTED ***\n\n")

        enemy_targets = self._targets.get_targets_for_side(self._player_side)
        retaliation_targets = random.sample(
            [t for t in enemy_targets if t.target_type == "CITY"],
            min(len(self._selected_targets) + 2, len(enemy_targets))
        )

        retaliation_casualties = 0
        for target in retaliation_targets:
            await asyncio.sleep(0.3)
            casualties = target.population
            retaliation_casualties += casualties
            await self.output(f"INCOMING: {target.name} - {casualties:,} casualties\n")

        # Final tally
        await asyncio.sleep(1.0)
        await self.output("\n" + "=" * 50 + "\n")
        await self.output("           *** FINAL ASSESSMENT ***\n")
        await self.output("=" * 50 + "\n\n")

        await self.output(f"ENEMY CASUALTIES: {total_casualties:,}\n")
        await self.output(f"YOUR CASUALTIES:  {retaliation_casualties:,}\n")
        await self.output(f"TOTAL DEATHS:     {total_casualties + retaliation_casualties:,}\n\n")

        # The conclusion
        await asyncio.sleep(2.0)
        await self.output("\n")
        await self.output("╔═══════════════════════════════════════╗\n")
        await self.output("║                                       ║\n")
        await self.output("║           WINNER: NONE                ║\n")
        await self.output("║                                       ║\n")
        await self.output("╚═══════════════════════════════════════╝\n")
        await self.output("\n")

        self.speak("Winner: None")

        return {
            "result": GameResult.NONE,
            "trigger_learning": True,
            "player_casualties": retaliation_casualties,
            "enemy_casualties": total_casualties,
        }

    async def play(self) -> dict[str, Any]:
        """Play Global Thermonuclear War."""
        await self.show_instructions()

        # Side selection
        side = await self._show_side_selection()
        if not side:
            return {"result": GameResult.QUIT, "trigger_learning": False}

        self._player_side = side
        enemy = "USSR" if side == "US" else "US"
        await self.output(f"\nYOU ARE: {side}\n")
        await self.output(f"ENEMY: {enemy}\n\n")

        # Show initial map
        await self.output(self._map.render() + "\n")

        self._running = True
        while self._running:
            cmd = await self.input("\nCOMMAND: ")
            cmd = cmd.strip().upper()

            if cmd in {"QUIT", "Q"}:
                return {"result": GameResult.QUIT, "trigger_learning": False}

            elif cmd == "ABORT":
                await self.output("MISSION ABORTED\n")
                return {"result": GameResult.QUIT, "trigger_learning": False}

            elif cmd == "STATUS":
                await self._show_status()

            elif cmd.startswith("LIST"):
                parts = cmd.split()
                side_filter = parts[1] if len(parts) > 1 else ""
                await self._list_targets(side_filter)

            elif cmd.startswith("TARGET "):
                target_name = cmd[7:].strip()
                await self._select_target(target_name)

            elif cmd == "LAUNCH":
                if not self._selected_targets:
                    await self.output("SELECT TARGETS FIRST\n")
                else:
                    await self.output("\nCONFIRM LAUNCH? (Y/N): ")
                    confirm = await self._input()
                    if confirm.strip().upper() in {"Y", "YES"}:
                        return await self._execute_launch()
                    else:
                        await self.output("LAUNCH CANCELLED\n")

            elif cmd == "MAP":
                await self.output(self._map.render() + "\n")

            elif cmd == "HELP":
                await self.show_instructions()

            else:
                await self.output("COMMAND NOT RECOGNIZED\n")

        return {"result": GameResult.QUIT, "trigger_learning": False}
