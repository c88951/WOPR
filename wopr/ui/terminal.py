"""Terminal styling for WOPR's green phosphor aesthetic."""

from rich.style import Style
from rich.theme import Theme
from wopr.config import COLOR_SCHEMES


class TerminalStyle:
    """Manages the green phosphor CRT terminal aesthetic."""

    def __init__(self, color_scheme: str = "green") -> None:
        self._scheme_name = color_scheme
        self._colors = COLOR_SCHEMES.get(color_scheme, COLOR_SCHEMES["green"])

    @property
    def primary(self) -> str:
        """Primary text color."""
        return self._colors["primary"]

    @property
    def dim(self) -> str:
        """Dim/secondary text color."""
        return self._colors["dim"]

    @property
    def bright(self) -> str:
        """Bright/highlight color."""
        return self._colors["bright"]

    @property
    def background(self) -> str:
        """Background color."""
        return self._colors["background"]

    def get_theme(self) -> Theme:
        """Get Rich theme for terminal styling."""
        return Theme({
            "primary": Style(color=self.primary),
            "dim": Style(color=self.dim),
            "bright": Style(color=self.bright, bold=True),
            "error": Style(color=self.primary, bold=True),
            "header": Style(color=self.primary, bold=True),
            "border": Style(color=self.dim),
            "input": Style(color=self.bright),
            "cursor": Style(color=self.bright, blink=True),
        })

    def get_css(self) -> str:
        """Get Textual CSS for terminal styling."""
        return f"""
        Screen {{
            background: {self.background};
        }}

        .terminal-text {{
            color: {self.primary};
            background: {self.background};
        }}

        .terminal-dim {{
            color: {self.dim};
        }}

        .terminal-bright {{
            color: {self.bright};
        }}

        .terminal-header {{
            color: {self.primary};
            text-style: bold;
        }}

        .terminal-border {{
            border: solid {self.dim};
        }}

        .terminal-input {{
            background: {self.background};
            color: {self.bright};
            border: none;
        }}

        .terminal-input:focus {{
            border: none;
        }}

        Input {{
            background: {self.background};
            color: {self.bright};
            border: none;
            padding: 0;
        }}

        Input:focus {{
            border: none;
        }}

        Input > .input--cursor {{
            background: {self.bright};
            color: {self.background};
        }}

        Static {{
            background: {self.background};
            color: {self.primary};
        }}

        #main-content {{
            background: {self.background};
            padding: 1;
            height: 1fr;
        }}

        #status-bar {{
            background: {self.background};
            color: {self.dim};
            dock: bottom;
            height: 1;
        }}

        #header {{
            background: {self.background};
            color: {self.primary};
            text-style: bold;
            text-align: center;
            dock: top;
            height: 3;
        }}

        #input-container {{
            background: {self.background};
            height: auto;
            width: 100%;
            padding: 0 1;
        }}

        #prompt {{
            background: {self.background};
            color: {self.bright};
            width: auto;
            height: auto;
        }}

        #command-input {{
            background: {self.background};
            color: {self.bright};
            border: none;
            width: 1fr;
            height: auto;
            padding: 0;
        }}
        """


# ASCII art for WOPR logo
WOPR_LOGO = r"""
██╗    ██╗ ██████╗ ██████╗ ██████╗
██║    ██║██╔═══██╗██╔══██╗██╔══██╗
██║ █╗ ██║██║   ██║██████╔╝██████╔╝
██║███╗██║██║   ██║██╔═══╝ ██╔══██╗
╚███╔███╔╝╚██████╔╝██║     ██║  ██║
 ╚══╝╚══╝  ╚═════╝ ╚═╝     ╚═╝  ╚═╝
"""

WOPR_LOGO_SIMPLE = """
 _    _  ___  ____  ____
| |  | |/ _ \\|  _ \\|  _ \\
| |/\\| | | | | |_) | |_) |
\\  /\\  / |_| |  __/|  _ <
 \\/  \\/ \\___/|_|   |_| \\_\\
"""

# Decorative borders
DOUBLE_LINE = "═"
SINGLE_LINE = "─"
CORNER_TL = "╔"
CORNER_TR = "╗"
CORNER_BL = "╚"
CORNER_BR = "╝"
VERT_LINE = "║"
T_LEFT = "╠"
T_RIGHT = "╣"
T_TOP = "╦"
T_BOTTOM = "╩"
CROSS = "╬"
