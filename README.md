# WOPR - War Operation Plan Response

A faithful Python recreation of the WOPR computer system from the 1983 film **WarGames**.

```
██╗    ██╗ ██████╗ ██████╗ ██████╗
██║    ██║██╔═══██╗██╔══██╗██╔══██╗
██║ █╗ ██║██║   ██║██████╔╝██████╔╝
██║███╗██║██║   ██║██╔═══╝ ██╔══██╗
╚███╔███╔╝╚██████╔╝██║     ██║  ██║
 ╚══╝╚══╝  ╚═════╝ ╚═╝     ╚═╝  ╚═╝

       WAR OPERATION PLAN RESPONSE
          NORAD COMPUTER SYSTEM
```

> *"A strange game. The only winning move is not to play. How about a nice game of chess?"*

---

## About

This project recreates the iconic WOPR supercomputer from the 1983 film WarGames. Experience the complete narrative - from dialing in via modem to discovering that the only winning move is not to play.

**Features:**
- Authentic modem dial-up sequence with sound effects
- Movie-accurate login system (password: **joshua**)
- All 15 games from WOPR's original list, fully playable
- Global Thermonuclear War simulation with world map and missile animations
- The complete "learning" sequence with tic-tac-toe
- Period-accurate green phosphor terminal aesthetics
- Optional text-to-speech for WOPR's voice
- Synthesized retro sound effects (modem, explosions, etc.)
- Hidden help system for newcomers (doesn't break immersion for fans)

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/c88951/WOPR.git
cd WOPR

# Install the package (with sound support)
pip3 install -e ".[audio]"

# Run WOPR
python3 -m wopr
```

### Playing

1. **Title Screen**: Press **Enter** to connect
2. **Login**: When you see `LOGON:`, enter **joshua**
3. **Game Selection**: Type a game name, number (1-15), or `LIST` to see all games

### The Login

When you see `LOGON:`, enter `joshua` to access the system.

```
LOGON: joshua

GREETINGS PROFESSOR FALKEN.
SHALL WE PLAY A GAME?
```

**New to the movie?** Type `help` at the login prompt for a hint.

---

## Running Modes

### Full Experience (Recommended for first-time)
```bash
python3 -m wopr
```
Includes modem dial-up animation, typing effects, and the complete narrative.

### Quick Start (Skip Intro)
```bash
python3 -m wopr --skip-intro
```
Jumps past the modem connection sequence.

### Fast Mode (No Animations)
```bash
python3 -m wopr --fast
```
Disables typing animations for faster interaction.

### Silent Mode
```bash
python3 -m wopr --no-sound      # Disable all audio
python3 -m wopr --no-voice      # Disable voice synthesis only
```

### Jump to a Specific Game
```bash
python3 -m wopr --game "CHESS"
python3 -m wopr --game "GLOBAL THERMONUCLEAR WAR"
```

### Combine Options
```bash
python3 -m wopr --fast --skip-intro --no-sound
```

### All Command Line Options
```
python3 -m wopr [OPTIONS]

Options:
  --skip-intro    Skip the modem dialup sequence
  --no-sound      Disable all audio
  --no-voice      Disable voice synthesis only
  --fast          Disable typing animations
  --game GAME     Jump directly to a specific game
  --debug         Enable debug mode
  --version       Show version info
  --help          Show help message
```

---

## Available Games

WOPR includes all 15 games from the original film:

| # | Game | Description |
|---|------|-------------|
| 1 | **FALKEN'S MAZE** | Navigate through a procedurally generated labyrinth |
| 2 | **BLACK JACK** | Classic casino card game against WOPR as dealer |
| 3 | **GIN RUMMY** | Two-player rummy with knock and gin mechanics |
| 4 | **HEARTS** | Four-player trick avoidance (shoot the moon!) |
| 5 | **BRIDGE** | Simplified contract bridge with bidding |
| 6 | **CHECKERS** | Classic board game with mandatory jumps |
| 7 | **CHESS** | Full chess with AI opponent (configurable difficulty) |
| 8 | **POKER** | Five-card draw against WOPR |
| 9 | **FIGHTER COMBAT** | Air-to-air dogfighting simulation |
| 10 | **GUERRILLA ENGAGEMENT** | Hearts-and-minds counterinsurgency |
| 11 | **DESERT WARFARE** | Armored battalion tactics |
| 12 | **AIR-TO-GROUND ACTIONS** | Close air support strike missions |
| 13 | **THEATERWIDE TACTICAL WARFARE** | Multi-front campaign management |
| 14 | **THEATERWIDE BIOTOXIC AND CHEMICAL WARFARE** | NBC warfare ethical scenarios |
| 15 | **GLOBAL THERMONUCLEAR WAR** | Strategic nuclear warfare simulation |

### Game Shortcuts
- `GTW` - Global Thermonuclear War
- `BJ` - Black Jack
- Or just type the game number (1-15)

---

## Help System

WOPR includes a hidden help system that provides guidance without breaking immersion.

### At Login
```
LOGON: help
```
Displays classified system documentation with a hint about the backdoor.

### During Game Selection
```
> help
```
Shows available commands, shortcuts, and tips.

### Help Commands
- `help` or `HELP`
- `?`
- `hint`
- `commands`

---

## The Global Thermonuclear War Experience

The crown jewel of WOPR. Select targets, launch missiles, and discover why the only winning move is not to play.

```
> GLOBAL THERMONUCLEAR WAR

WHICH SIDE DO YOU WANT?

    1. UNITED STATES
    2. SOVIET UNION
```

**Commands during GTW:**
- `LIST` - Show available targets
- `TARGET <name>` - Select a target (e.g., `TARGET MOSCOW`)
- `STATUS` - Show current game state
- `LAUNCH` - Execute nuclear strike
- `ABORT` - Abort mission

After the simulation concludes with "WINNER: NONE", WOPR demonstrates through tic-tac-toe that some games cannot be won.

---

## Configuration

Create `~/.wopr/config.toml` for persistent settings:

```toml
[display]
typing_speed = 30          # Characters per second (0 = instant)
scanlines = false          # CRT scanline effect
animations = true          # Enable animations
color_scheme = "green"     # green, amber, or white

[audio]
enabled = true
voice_enabled = true
voice_rate = 140           # Words per minute
sound_effects = true
volume = 0.8

[gameplay]
skip_intro = false
chess_difficulty = 3       # 1-5 scale
save_games = true

[accessibility]
high_contrast = false
screen_reader_mode = false
```

---

## Building with Claude Code

This entire project was built using [Claude Code](https://claude.ai/claude-code). You can recreate or extend it yourself.

### For Claude Instances Rebuilding This Project

**Key Technical Details:**
- **Framework**: Textual TUI (async-based terminal UI)
- **Audio**: pygame (preferred) or simpleaudio for WAV playback
- **Voice**: pyttsx3 for text-to-speech
- **Chess AI**: python-chess library
- **Config**: TOML files with tomli/tomllib

**Critical Implementation Notes:**

1. **VerticalScroll Focus Issue** (CRITICAL - must disable or mouse clicks break input):
   ```python
   def compose(self) -> ComposeResult:
       # CRITICAL: Disable focus on VerticalScroll or mouse clicks steal focus from Input
       scroll = VerticalScroll(
           Static("", id="terminal-output"),
           id="main-content"
       )
       scroll.can_focus = False  # Prevents mouse clicks from stealing focus
       yield scroll

       yield Horizontal(
           Static("> ", id="prompt"),
           Input(id="command-input"),
           id="input-container"
       )
   ```

2. **Async Event Input Pattern** (CRITICAL - follow exactly or input breaks):
   ```python
   def __init__(self, ...):
       # MUST initialize these in __init__, not dynamically
       self._pending_input: asyncio.Event | None = None
       self._input_value: str = ""

   def _do_focus(self, widget: Input) -> None:
       """Helper called via set_timer to focus input."""
       if not widget.has_focus:
           self.set_focus(widget)

   async def _get_input(self) -> str:
       # Clear previous state FIRST
       self._pending_input = None
       self._input_value = ""

       input_widget = self.query_one("#command-input", Input)
       input_widget.value = ""

       # Create FRESH event
       self._pending_input = asyncio.Event()

       # CRITICAL: Use set_timer, NOT call_after_refresh or asyncio.sleep
       # - call_after_refresh waits for screen refresh that may not happen
       # - asyncio.sleep can interfere with Textual's event loop
       # Use multiple timers for reliability
       self.set_timer(0.1, lambda: self._do_focus(input_widget))
       self.set_timer(0.2, lambda: self._do_focus(input_widget))

       await self._pending_input.wait()

       # Clear event IMMEDIATELY after use
       result = self._input_value
       self._pending_input = None
       return result

   @on(Input.Submitted, "#command-input")
   def handle_input_submitted(self, event: Input.Submitted) -> None:
       if (self._pending_input is not None and
           not self._pending_input.is_set()):
           self._input_value = event.value
           self._pending_input.set()
       event.input.value = ""
   ```

3. **Common Pitfalls to Avoid:**
   - `VerticalScroll.can_focus = True` (default) → mouse clicks steal focus, app freezes
   - NOT clearing `_pending_input = None` after use → stale events on next input
   - Using `call_after_refresh()` for focus → may never fire after long sequences
   - Using `asyncio.sleep()` in Textual → interferes with event loop
   - NOT initializing `_pending_input` in `__init__` → attribute errors

4. **Debug Logging** (Textual captures stderr):
   ```python
   # Textual captures stderr for terminal control. Write debug to file:
   def _debug_log(self, msg: str) -> None:
       if self._debug:
           with open("/tmp/wopr_debug.log", "a") as f:
               f.write(f"{msg}\n")
   ```

5. Audio manager tries pygame first, falls back to simpleaudio
6. All games inherit from a base Game class with async `play()` method
7. Sound files are synthesized WAVs (numpy/scipy) - no external audio files needed
8. Use `VerticalScroll` for main content, `Horizontal` for input container

### Setup
1. Install Claude Code CLI
2. Clone this repo or start fresh
3. Open the project directory in Claude Code

### The Original Prompt

The project was built from a detailed specification. To recreate or extend it:

```
Create a Python terminal application that recreates the WOPR computer
from WarGames (1983). Include:

- Modem dial-up sequence with animations and sound effects
- Login system with "joshua" backdoor
- All 15 games from the film's game list
- Global Thermonuclear War with world map and missile animations
- The learning sequence where WOPR plays tic-tac-toe
- Green phosphor terminal aesthetics using Textual
- Optional voice synthesis with pyttsx3
- Sound effects using pygame

The narrative should flow from dial-in through the famous
"the only winning move is not to play" conclusion.
```

### Project Structure
```
WOPR/
├── pyproject.toml          # Package configuration
├── wopr/
│   ├── __main__.py         # Entry point
│   ├── app.py              # Main Textual application
│   ├── config.py           # Configuration management
│   ├── core/
│   │   ├── state.py        # State machine
│   │   ├── voice.py        # Text-to-speech
│   │   └── audio.py        # Sound effects (pygame/simpleaudio)
│   ├── narrative/
│   │   ├── dialup.py       # Modem sequence
│   │   ├── login.py        # Authentication ("joshua" backdoor)
│   │   ├── dialogue.py     # WOPR responses
│   │   └── sequences.py    # Story flow
│   ├── ui/
│   │   ├── terminal.py     # Green phosphor styling
│   │   ├── widgets.py      # Custom UI components
│   │   └── animations.py   # Text effects
│   ├── assets/
│   │   ├── sounds/         # WAV sound effects
│   │   ├── maps/           # ASCII world maps
│   │   └── data/           # Game data (targets, dialogue)
│   └── games/
│       ├── base.py         # Base game class
│       ├── maze.py         # Falken's Maze
│       ├── board/          # Chess, Checkers, Tic-Tac-Toe
│       ├── cards/          # Blackjack, Poker, etc.
│       └── military/       # War simulations + GTW
└── tests/                  # Comprehensive test suite
```

### Running Tests
```bash
pip3 install -e ".[dev]"
python3 -m pytest tests/ -v
```

### Regenerating Sound Effects
The WAV files in `wopr/assets/sounds/` were synthesized using numpy/scipy. To regenerate:
```bash
pip3 install numpy scipy
python3 generate_sounds.py
```
This creates all sound effects programmatically (no external audio sources needed).

---

## Requirements

- Python 3.10+
- Terminal with Unicode support

### Dependencies
```
textual >= 0.50.0      # TUI framework
rich >= 13.0.0         # Text formatting
python-chess >= 1.10   # Chess engine
pyttsx3 >= 2.90        # Text-to-speech
```

### Audio Support (Recommended)
```bash
pip3 install -e ".[audio]"
```

This installs `pygame` for sound effects. The game includes synthesized WAV files:
- **Modem dial** - Authentic DTMF tones and dial sequence
- **Modem connect** - Classic modem handshake screech
- **Terminal beep** - Soft notification sound
- **Typing** - Keystroke clicks
- **Missile launch** - Whoosh and rumble
- **Explosion** - Deep boom

Sound is optional - the game works fine without it (`--no-sound`).

---

## Platform Support

| Platform | Status |
|----------|--------|
| Linux | ✅ Full support |
| macOS | ✅ Full support |
| Windows | ✅ Works (some terminal limitations) |

---

## Easter Eggs

There may be a few hidden features for those who explore...

*"Would you like to play a game?"*

---

## Contributing

Contributions welcome! Some ideas:
- Additional sound effects
- More sophisticated chess AI
- Network multiplayer for card games
- Additional Cold War era targets for GTW
- CRT shader effects

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- **WarGames (1983)** - The film that started it all
- **MGM/United Artists** - Original copyright holders
- **John Badham** - Director
- **Lawrence Lasker & Walter F. Parkes** - Writers
- **Textual** - Excellent Python TUI framework
- **Claude Code** - AI pair programming assistant

---

## Disclaimer

This is a fan project for educational and entertainment purposes. It is not affiliated with or endorsed by MGM, United Artists, or any rights holders of the WarGames film.

---

*"The only winning move is not to play."*
