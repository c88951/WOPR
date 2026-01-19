"""Main WOPR Textual application."""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, ScrollableContainer
from textual.widgets import Static, Input
from textual.binding import Binding
from textual import events
import asyncio

from .config import WOPRConfig, COLOR_SCHEMES, APP_TITLE
from .core.state import GameState, WOPRStateMachine
from .core.voice import VoiceSynthesizer
from .core.audio import AudioManager
from .ui.terminal import TerminalStyle
from .ui.widgets import StatusBar
from .narrative.sequences import NarrativeSequences
from .narrative.login import LoginResult
from .games import GAME_LIST


class WOPRApp(App):
    """Main WOPR application."""

    TITLE = APP_TITLE
    CSS = ""  # Will be set dynamically

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=False),
        Binding("ctrl+q", "quit", "Quit", show=False),
    ]

    def __init__(
        self,
        config: WOPRConfig | None = None,
        skip_intro: bool = False,
        no_sound: bool = False,
        no_voice: bool = False,
        fast_mode: bool = False,
        start_game: str | None = None,
    ) -> None:
        super().__init__()

        # Load config
        self._config = config or WOPRConfig.load()

        # Apply command line overrides
        if skip_intro:
            self._config.gameplay.skip_intro = True
        if no_sound:
            self._config.audio.enabled = False
            self._config.audio.voice_enabled = False
        if no_voice:
            self._config.audio.voice_enabled = False
        if fast_mode:
            self._config.display.animations = False
            self._config.display.typing_speed = 0

        self._start_game = start_game

        # Initialize components
        self._style = TerminalStyle(self._config.display.color_scheme)
        self._state = WOPRStateMachine()

        # Initialize audio (may be None if not available)
        from .config import SOUNDS_DIR
        self._audio = AudioManager(
            SOUNDS_DIR,
            enabled=self._config.audio.enabled and self._config.audio.sound_effects,
            volume=self._config.audio.volume
        ) if self._config.audio.enabled else None

        # Initialize voice
        self._voice = VoiceSynthesizer(
            enabled=self._config.audio.voice_enabled,
            rate=self._config.audio.voice_rate
        ) if self._config.audio.voice_enabled else None

        # Text output buffer
        self._output_buffer: list[str] = []
        self._current_game = None

        # Set up CSS
        self.CSS = self._style.get_css()

    def compose(self) -> ComposeResult:
        """Compose the main screen layout."""
        yield Static(
            f"  {APP_TITLE}\n  NORAD COMPUTER SYSTEM",
            id="header"
        )
        yield ScrollableContainer(
            Static("", id="terminal-output"),
            id="main-content"
        )
        yield Container(
            Static("> ", id="prompt"),
            Input(id="command-input", classes="terminal-input"),
            id="input-container"
        )
        yield StatusBar(id="status-bar")

    def on_mount(self) -> None:
        """Initialize the application when mounted."""
        # Start voice synthesis worker
        if self._voice:
            self._voice.start()

        # Start the narrative
        asyncio.create_task(self._run_narrative())

    def on_unmount(self) -> None:
        """Clean up when unmounting."""
        if self._voice:
            self._voice.stop()

    async def _output(self, text: str) -> None:
        """Output text to the terminal."""
        output_widget = self.query_one("#terminal-output", Static)
        self._output_buffer.append(text)
        full_text = "".join(self._output_buffer)
        output_widget.update(full_text)

        # Auto-scroll to bottom
        scroll_container = self.query_one("#main-content", ScrollableContainer)
        scroll_container.scroll_end(animate=False)

    async def _clear_output(self) -> None:
        """Clear the terminal output."""
        self._output_buffer = []
        output_widget = self.query_one("#terminal-output", Static)
        output_widget.update("")

    async def _get_input(self) -> str:
        """Wait for user input."""
        input_widget = self.query_one("#command-input", Input)
        input_widget.value = ""
        input_widget.focus()

        # Wait for input submission
        self._pending_input = asyncio.Event()
        self._input_value = ""
        await self._pending_input.wait()
        return self._input_value

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if hasattr(self, "_pending_input"):
            self._input_value = event.value
            self._pending_input.set()
            event.input.value = ""

    async def _run_narrative(self) -> None:
        """Run the main narrative flow."""
        # Initialize narrative sequences
        typing_speed = (
            0 if not self._config.display.animations
            else self._config.display.typing_speed
        )
        narrative = NarrativeSequences(
            output_callback=self._output,
            voice_synthesizer=self._voice,
            audio_manager=self._audio,
            skip_intro=self._config.gameplay.skip_intro,
            typing_speed=typing_speed
        )

        # Title screen
        if not self._config.gameplay.skip_intro:
            await self._show_title_screen()

        # State: DIAL_UP
        self._state.transition(GameState.DIAL_UP)
        await narrative.run_full_intro()

        # State: CONNECTED -> LOGIN
        self._state.transition(GameState.CONNECTED)
        self._state.transition(GameState.LOGIN)

        # Login loop
        while True:
            await self._output("LOGON: ")
            username = await self._get_input()
            await self._output(f"{username}\n")

            self._state.transition(GameState.AUTHENTICATE)
            result = await narrative.run_login(username)

            if result == LoginResult.BACKDOOR:
                break

            # Help doesn't count as failed attempt, just continue
            if result == LoginResult.HELP:
                self._state.transition(GameState.LOGIN)
                continue

            # Back to login
            self._state.transition(GameState.LOGIN)

        # State: GREETING
        self._state.transition(GameState.GREETING)
        await narrative.run_greeting()

        # State: GAME_LIST - main game loop
        self._state.transition(GameState.GAME_LIST)
        await self._game_loop(narrative)

    async def _show_title_screen(self) -> None:
        """Display the title screen."""
        title = """
██╗    ██╗ ██████╗ ██████╗ ██████╗
██║    ██║██╔═══██╗██╔══██╗██╔══██╗
██║ █╗ ██║██║   ██║██████╔╝██████╔╝
██║███╗██║██║   ██║██╔═══╝ ██╔══██╗
╚███╔███╔╝╚██████╔╝██║     ██║  ██║
 ╚══╝╚══╝  ╚═════╝ ╚═╝     ╚═╝  ╚═╝

       WAR OPERATION PLAN RESPONSE
          NORAD COMPUTER SYSTEM


"""
        await self._output(title)
        await self._output("      [PRESS ENTER TO CONNECT...]\n\n")
        await self._get_input()
        await self._clear_output()

    async def _game_loop(self, narrative: NarrativeSequences) -> None:
        """Main game selection loop."""
        while True:
            user_input = await self._get_input()
            await self._output(f"{user_input}\n")

            game, suggest_chess = await narrative.handle_game_selection(user_input)

            if game == "QUIT":
                self.exit()
                return

            if suggest_chess:
                # WOPR suggested chess, wait for response
                response = await self._get_input()
                await self._output(f"{response}\n")
                if response.strip().upper() in {"NO", "N", "LATER"}:
                    # User insists on original game
                    game, _ = await narrative.handle_game_selection(user_input)

            if game:
                self._state.transition(GameState.PLAYING)
                await self._play_game(game, narrative)
                self._state.transition(GameState.GAME_LIST)

    async def _play_game(self, game_name: str, narrative: NarrativeSequences) -> None:
        """Launch and play a game."""
        await self._output(f"\n{game_name}\n")
        await self._output("=" * len(game_name) + "\n\n")

        # Import and run the appropriate game
        if game_name == "GLOBAL THERMONUCLEAR WAR":
            await self._play_gtw(narrative)
        elif game_name == "CHESS":
            await self._play_chess()
        elif game_name == "FALKEN'S MAZE":
            await self._play_maze()
        elif game_name == "BLACK JACK":
            await self._play_blackjack()
        elif game_name == "CHECKERS":
            await self._play_checkers()
        elif game_name == "POKER":
            await self._play_poker()
        elif game_name == "GIN RUMMY":
            await self._play_gin_rummy()
        elif game_name == "HEARTS":
            await self._play_hearts()
        elif game_name == "BRIDGE":
            await self._play_bridge()
        else:
            # Military simulations and other games
            await self._play_military_sim(game_name)

        await self._output("\n[GAME ENDED - PRESS ENTER TO CONTINUE]\n")
        await self._get_input()

    async def _play_gtw(self, narrative: NarrativeSequences) -> None:
        """Play Global Thermonuclear War."""
        from .games.military.thermonuclear_war import GlobalThermonuclearWar

        game = GlobalThermonuclearWar(
            output_callback=self._output,
            input_callback=self._get_input,
            voice=self._voice,
            audio=self._audio
        )
        result = await game.play()

        # After GTW, trigger learning sequence
        if result.get("trigger_learning", True):
            self._state.transition(GameState.LEARNING)
            await narrative.run_winner_none()
            await self._run_learning_sequence(narrative)

    async def _run_learning_sequence(self, narrative: NarrativeSequences) -> None:
        """Run the tic-tac-toe learning sequence."""
        await narrative.run_learning_intro()

        from .games.board.tictactoe import TicTacToeLearning

        learning = TicTacToeLearning(output_callback=self._output)
        await learning.run_demonstration()

        # Wisdom
        self._state.transition(GameState.WISDOM)
        await narrative.run_wisdom()

    async def _play_chess(self) -> None:
        """Play Chess."""
        from .games.board.chess import ChessGame

        game = ChessGame(
            output_callback=self._output,
            input_callback=self._get_input,
            difficulty=self._config.gameplay.chess_difficulty
        )
        await game.play()

    async def _play_maze(self) -> None:
        """Play Falken's Maze."""
        from .games.maze import FalkensMaze

        game = FalkensMaze(
            output_callback=self._output,
            input_callback=self._get_input
        )
        await game.play()

    async def _play_blackjack(self) -> None:
        """Play Blackjack."""
        from .games.cards.blackjack import Blackjack

        game = Blackjack(
            output_callback=self._output,
            input_callback=self._get_input
        )
        await game.play()

    async def _play_checkers(self) -> None:
        """Play Checkers."""
        from .games.board.checkers import Checkers

        game = Checkers(
            output_callback=self._output,
            input_callback=self._get_input
        )
        await game.play()

    async def _play_poker(self) -> None:
        """Play Poker."""
        from .games.cards.poker import Poker

        game = Poker(
            output_callback=self._output,
            input_callback=self._get_input
        )
        await game.play()

    async def _play_gin_rummy(self) -> None:
        """Play Gin Rummy."""
        from .games.cards.gin_rummy import GinRummy

        game = GinRummy(
            output_callback=self._output,
            input_callback=self._get_input
        )
        await game.play()

    async def _play_hearts(self) -> None:
        """Play Hearts."""
        from .games.cards.hearts import Hearts

        game = Hearts(
            output_callback=self._output,
            input_callback=self._get_input
        )
        await game.play()

    async def _play_bridge(self) -> None:
        """Play Bridge."""
        from .games.cards.bridge import Bridge

        game = Bridge(
            output_callback=self._output,
            input_callback=self._get_input
        )
        await game.play()

    async def _play_military_sim(self, game_name: str) -> None:
        """Play a military simulation game."""
        from .games.military.simulations import MilitarySimulation

        game = MilitarySimulation(
            game_name=game_name,
            output_callback=self._output,
            input_callback=self._get_input
        )
        await game.play()

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()


def run_app(
    skip_intro: bool = False,
    no_sound: bool = False,
    no_voice: bool = False,
    fast_mode: bool = False,
    start_game: str | None = None,
    debug: bool = False,
) -> None:
    """Run the WOPR application.

    Args:
        skip_intro: Skip the dialup sequence
        no_sound: Disable all audio
        no_voice: Disable voice synthesis
        fast_mode: Disable typing animations
        start_game: Jump directly to a specific game
        debug: Enable debug mode
    """
    app = WOPRApp(
        skip_intro=skip_intro,
        no_sound=no_sound,
        no_voice=no_voice,
        fast_mode=fast_mode,
        start_game=start_game,
    )
    app.run()
