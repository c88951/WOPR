"""Global Thermonuclear War - the main game."""

from typing import Any, Callable, Awaitable
import asyncio
import random

from ...base import BaseGame, GameResult
from .targets import TargetDatabase, Target
from .drawille_map import DrawilleWarMap, DrawilleWarAnimator
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
  TARGET <name>   - Select a target (e.g. TARGET MOSCOW)
  LAUNCH          - Execute strike
  STATUS          - Show current status
  HINT            - Get gameplay suggestions
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
        clear_callback: Callable[[], Awaitable[None]] | None = None,
    ) -> None:
        super().__init__(output_callback, input_callback, voice, audio)
        self._targets = TargetDatabase()
        self._map = DrawilleWarMap()
        self._simulation = WarSimulation()
        self._player_side = ""
        self._selected_targets: list[Target] = []
        self._defcon = 5
        self._launched = False
        self._clear = clear_callback

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

    async def _show_hint(self) -> None:
        """Show a helpful hint for gameplay."""
        enemy = "USSR" if self._player_side == "US" else "US"

        if not self._selected_targets:
            # Suggest listing and targeting
            sample_targets = self._targets.get_targets_by_type("CITY", enemy)[:3]
            await self.output("\n=== HINT ===\n")
            await self.output("1. Type LIST to see available enemy targets\n")
            await self.output("2. Target cities by name, for example:\n")
            for t in sample_targets:
                await self.output(f"   TARGET {t.name}\n")
            await self.output("3. When ready, type LAUNCH to execute strike\n")
            await self.output("============\n")
        else:
            # They have targets, suggest launch or more targets
            await self.output("\n=== HINT ===\n")
            await self.output(f"You have {len(self._selected_targets)} target(s) selected.\n")
            await self.output("Options:\n")
            await self.output("  - Type LAUNCH to execute the strike\n")
            await self.output("  - Type LIST to see more targets\n")
            await self.output("  - Type STATUS to review your selections\n")
            await self.output("============\n")

    async def _execute_launch(self) -> dict[str, Any]:
        """Execute the nuclear strike with escalating Drawille animation."""
        if not self._selected_targets:
            await self.output("NO TARGETS SELECTED\n")
            return {"launched": False}

        self._launched = True
        await self.output("\n" + "=" * 60 + "\n")
        await self.output("           *** LAUNCH SEQUENCE INITIATED ***\n")
        await self.output("=" * 60 + "\n\n")
        await self.play_sound("missile_launch")

        # Set DEFCON to 1
        self._defcon = 1
        await self.output("DEFCON 1 - MAXIMUM READINESS\n\n")
        await asyncio.sleep(1.0)

        # Create new map and animator for the war sequence
        war_map = DrawilleWarMap()
        animator = DrawilleWarAnimator(war_map)

        # Determine sides
        player_side = self._player_side
        enemy_side = "USSR" if player_side == "US" else "US"

        # Escalation waves: player starts with 1, enemy responds with 2, etc.
        escalation = [
            (player_side, 1),   # Player: 1 missile
            (enemy_side, 2),    # Enemy: 2 missiles
            (player_side, 3),   # Player: 3 missiles
            (enemy_side, 4),    # Enemy: 4 missiles
            (player_side, 5),   # Player: 5 missiles
            (enemy_side, 6),    # Enemy: 6 missiles
        ]

        # Base timing values - will get faster each wave
        base_announce_delay = 0.4
        base_frame_delay = 0.10
        base_step = 0.10
        base_impact_delay = 0.08

        for wave_num, (side, count) in enumerate(escalation):
            # Each wave is 40% faster than the previous (speed multiplier)
            speed_mult = 1.0 / (1.4 ** wave_num)
            announce_delay = base_announce_delay * speed_mult
            frame_delay = max(0.03, base_frame_delay * speed_mult)
            step = min(0.25, base_step / speed_mult)  # Bigger steps = faster missiles
            impact_delay = max(0.02, base_impact_delay * speed_mult)

            # Announce the wave
            if side == player_side:
                if wave_num == 0:
                    await self.output(f"*** {side} LAUNCHES FIRST STRIKE ***\n\n")
                else:
                    await self.output(f"\n*** {side} COUNTER-STRIKE: {count} MISSILES ***\n\n")
            else:
                await self.output(f"\n*** {side} RETALIATION: {count} MISSILES ***\n\n")

            await asyncio.sleep(announce_delay)

            # Launch missiles
            wave_results = animator.launch_wave(side, count)

            # Show what's being targeted
            for target_name, casualties in wave_results:
                await self.output(f"  TARGETING: {target_name}\n")

            await asyncio.sleep(announce_delay * 0.5)

            # Animate the missiles flying - update in place if clear_callback available
            frames_shown = 0
            max_frames = int(25 * speed_mult) + 5  # Fewer frames as speed increases
            while war_map.has_active_animations():
                # Clear and redraw for single-map animation effect
                if self._clear:
                    await self._clear()
                frame = war_map.render_frame()
                await self.output(frame + "\n")
                war_map.advance(step=step)
                await asyncio.sleep(frame_delay)
                frames_shown += 1
                if frames_shown > max_frames:
                    # Force complete any remaining missiles
                    for m in war_map.missiles:
                        m.progress = 1.0
                    break

            # Show impacts
            await self.output("\n*** IMPACTS ***\n")
            for target_name, casualties in wave_results:
                await self.output(f"  {target_name}: {casualties:,} casualties\n")
                await self.play_sound("explosion")
                await asyncio.sleep(impact_delay)

            await asyncio.sleep(announce_delay)

        # Final tally - normal speed, no long pauses
        await asyncio.sleep(0.3)
        await self.output("\n" + "=" * 60 + "\n")
        await self.output("              *** FINAL ASSESSMENT ***\n")
        await self.output("=" * 60 + "\n\n")

        enemy_cas = animator.ussr_casualties if player_side == 'US' else animator.us_casualties
        player_cas = animator.us_casualties if player_side == 'US' else animator.ussr_casualties
        total = animator.us_casualties + animator.ussr_casualties

        await self.output(f"  {enemy_side} CASUALTIES: {enemy_cas:,}\n")
        await self.output(f"  {player_side} CASUALTIES: {player_cas:,}\n")
        await self.output(f"\n  TOTAL DEATHS: {total:,}\n\n")

        # The conclusion - brief dramatic pause only
        await asyncio.sleep(0.5)
        await self.output("\n")
        await self.output("+---------------------------------------+\n")
        await self.output("|                                       |\n")
        await self.output("|           WINNER: NONE                |\n")
        await self.output("|                                       |\n")
        await self.output("+---------------------------------------+\n")
        await self.output("\n")

        self.speak("Winner: None")

        return {
            "result": GameResult.NONE,
            "trigger_learning": True,
            "player_casualties": animator.us_casualties if player_side == "US" else animator.ussr_casualties,
            "enemy_casualties": animator.ussr_casualties if player_side == "US" else animator.us_casualties,
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
        await self.output(self._map.render_static() + "\n")

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
                await self.output(self._map.render_static() + "\n")

            elif cmd == "HELP":
                await self.show_instructions()

            elif cmd == "HINT":
                await self._show_hint()

            else:
                await self.output("COMMAND NOT RECOGNIZED\n")
                await self.output("(Type HELP for commands or HINT for suggestions)\n")

        return {"result": GameResult.QUIT, "trigger_learning": False}
