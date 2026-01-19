"""Screen layouts for WOPR application."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Static, Input, Header, Footer
from textual.binding import Binding
from .widgets import TypingText, StatusBar, TerminalInput, GameDisplay


class WOPRScreen(Screen):
    """Base screen with WOPR styling."""

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=False),
        Binding("escape", "back", "Back", show=False),
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._style_name = kwargs.get("style", "green")

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield Static(
            "  WOPR - WAR OPERATION PLAN RESPONSE\n  NORAD COMPUTER SYSTEM",
            id="header"
        )
        yield Container(id="main-content")
        yield StatusBar(id="status-bar")

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    def action_back(self) -> None:
        """Go back to previous screen."""
        pass


class TitleScreen(Screen):
    """Initial title screen."""

    BINDINGS = [
        Binding("any", "start", "Start", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield Container(
            Static(
                """
██╗    ██╗ ██████╗ ██████╗ ██████╗
██║    ██║██╔═══██╗██╔══██╗██╔══██╗
██║ █╗ ██║██║   ██║██████╔╝██████╔╝
██║███╗██║██║   ██║██╔═══╝ ██╔══██╗
╚███╔███╔╝╚██████╔╝██║     ██║  ██║
 ╚══╝╚══╝  ╚═════╝ ╚═╝     ╚═╝  ╚═╝

       WAR OPERATION PLAN RESPONSE
          NORAD COMPUTER SYSTEM

      [PRESS ANY KEY TO CONNECT...]
                """,
                classes="terminal-text",
            ),
            id="title-container",
        )

    def on_key(self, event) -> None:
        """Handle any key press to start."""
        self.app.start_connection()


class DialupScreen(Screen):
    """Modem dialup sequence screen."""

    def compose(self) -> ComposeResult:
        yield Container(
            Static("INITIATING CONNECTION...\n", id="dialup-status"),
            TypingText(id="dialup-text", chars_per_second=50),
            id="dialup-container",
        )


class LoginScreen(Screen):
    """Login prompt screen."""

    def compose(self) -> ComposeResult:
        yield Container(
            Static("", id="login-output"),
            Horizontal(
                Static("LOGON: ", classes="terminal-text"),
                Input(id="login-input", classes="terminal-input"),
            ),
            id="login-container",
        )

    def on_mount(self) -> None:
        """Focus the input when mounted."""
        self.query_one("#login-input", Input).focus()


class GameListScreen(Screen):
    """Game selection screen."""

    GAME_LIST = """
FALKEN'S MAZE
BLACK JACK
GIN RUMMY
HEARTS
BRIDGE
CHECKERS
CHESS
POKER
FIGHTER COMBAT
GUERRILLA ENGAGEMENT
DESERT WARFARE
AIR-TO-GROUND ACTIONS
THEATERWIDE TACTICAL WARFARE
THEATERWIDE BIOTOXIC AND CHEMICAL WARFARE
GLOBAL THERMONUCLEAR WAR
"""

    def compose(self) -> ComposeResult:
        yield Container(
            ScrollableContainer(
                Static("", id="dialogue-output"),
                id="dialogue-scroll",
            ),
            Horizontal(
                Static("> ", classes="terminal-text"),
                Input(id="command-input", classes="terminal-input"),
            ),
            id="game-list-container",
        )

    def on_mount(self) -> None:
        """Focus the input when mounted."""
        self.query_one("#command-input", Input).focus()

    def show_game_list(self) -> None:
        """Display the list of available games."""
        output = self.query_one("#dialogue-output", Static)
        output.update(self.GAME_LIST)


class GameScreen(Screen):
    """Screen for playing games."""

    BINDINGS = [
        Binding("escape", "exit_game", "Exit Game"),
    ]

    def compose(self) -> ComposeResult:
        yield Container(
            Static("", id="game-title"),
            GameDisplay(id="game-display"),
            Static("", id="game-status"),
            Horizontal(
                Static("> ", classes="terminal-text"),
                Input(id="game-input", classes="terminal-input"),
            ),
            id="game-container",
        )

    def on_mount(self) -> None:
        """Focus the input when mounted."""
        self.query_one("#game-input", Input).focus()

    def action_exit_game(self) -> None:
        """Exit the current game."""
        self.app.exit_game()


class WarScreen(Screen):
    """Screen for Global Thermonuclear War simulation."""

    def compose(self) -> ComposeResult:
        yield Container(
            Static("GLOBAL THERMONUCLEAR WAR", id="war-title"),
            Static("", id="war-map"),
            Horizontal(
                Container(
                    Static("US STRATEGIC FORCES", classes="terminal-bright"),
                    Static("", id="us-forces"),
                    id="us-panel",
                ),
                Container(
                    Static("USSR STRATEGIC FORCES", classes="terminal-bright"),
                    Static("", id="ussr-forces"),
                    id="ussr-panel",
                ),
            ),
            StatusBar(id="war-status"),
            Horizontal(
                Static("> ", classes="terminal-text"),
                Input(id="war-input", classes="terminal-input"),
            ),
            id="war-container",
        )


class LearningScreen(Screen):
    """Screen for the tic-tac-toe learning sequence."""

    def compose(self) -> ComposeResult:
        yield Container(
            Static("TIC-TAC-TOE", id="learning-title"),
            Static("", id="ttt-display"),
            Static("", id="learning-status"),
            id="learning-container",
        )


class WisdomScreen(Screen):
    """Final wisdom screen."""

    def compose(self) -> ComposeResult:
        yield Container(
            TypingText(
                "A STRANGE GAME.\n\n"
                "THE ONLY WINNING MOVE IS NOT TO PLAY.\n\n"
                "HOW ABOUT A NICE GAME OF CHESS?",
                chars_per_second=20,
                id="wisdom-text",
            ),
            id="wisdom-container",
        )
