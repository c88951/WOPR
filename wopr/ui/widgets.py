"""Custom Textual widgets for WOPR."""

from textual.app import ComposeResult
from textual.widgets import Static, Input
from textual.reactive import reactive
from textual.message import Message
from textual import events
import asyncio


class TypingText(Static):
    """A Static widget that displays text with a typing animation."""

    text_content: reactive[str] = reactive("")
    displayed_text: reactive[str] = reactive("")

    class TypingComplete(Message):
        """Message sent when typing animation completes."""
        pass

    def __init__(
        self,
        text: str = "",
        chars_per_second: int = 30,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._target_text = text
        self._chars_per_second = chars_per_second
        self._typing_task: asyncio.Task | None = None
        self._instant = False

    async def _type_text(self) -> None:
        """Animate typing the text character by character."""
        if self._instant or self._chars_per_second <= 0:
            self.displayed_text = self._target_text
            self.post_message(self.TypingComplete())
            return

        delay = 1.0 / self._chars_per_second
        self.displayed_text = ""

        for i, char in enumerate(self._target_text):
            self.displayed_text = self._target_text[:i + 1]
            await asyncio.sleep(delay)

        self.post_message(self.TypingComplete())

    def set_text(self, text: str, instant: bool = False) -> None:
        """Set text to display, optionally without animation."""
        self._target_text = text
        self._instant = instant
        if self._typing_task and not self._typing_task.done():
            self._typing_task.cancel()
        self._typing_task = asyncio.create_task(self._type_text())

    def skip_animation(self) -> None:
        """Skip to the end of the typing animation."""
        if self._typing_task and not self._typing_task.done():
            self._typing_task.cancel()
        self.displayed_text = self._target_text
        self.post_message(self.TypingComplete())

    def watch_displayed_text(self, text: str) -> None:
        """Update the widget when displayed_text changes."""
        self.update(text)

    def on_mount(self) -> None:
        """Start typing animation when mounted."""
        if self._target_text:
            self._typing_task = asyncio.create_task(self._type_text())


class BlinkingCursor(Static):
    """A blinking cursor widget."""

    visible: reactive[bool] = reactive(True)

    def __init__(
        self,
        cursor_char: str = "█",
        blink_rate: float = 0.5,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._cursor_char = cursor_char
        self._blink_rate = blink_rate
        self._blink_task: asyncio.Task | None = None

    async def _blink(self) -> None:
        """Toggle cursor visibility."""
        while True:
            await asyncio.sleep(self._blink_rate)
            self.visible = not self.visible

    def on_mount(self) -> None:
        """Start blinking when mounted."""
        self._blink_task = asyncio.create_task(self._blink())

    def on_unmount(self) -> None:
        """Stop blinking when unmounted."""
        if self._blink_task:
            self._blink_task.cancel()

    def watch_visible(self, visible: bool) -> None:
        """Update display when visibility changes."""
        self.update(self._cursor_char if visible else " ")


class TerminalInput(Input):
    """Terminal-styled input field."""

    class CommandSubmitted(Message):
        """Message sent when a command is submitted."""

        def __init__(self, command: str) -> None:
            self.command = command
            super().__init__()

    def __init__(
        self,
        prompt: str = "",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._prompt = prompt

    def on_mount(self) -> None:
        """Set up the input when mounted."""
        self.placeholder = self._prompt

    async def _on_key(self, event: events.Key) -> None:
        """Handle key presses."""
        if event.key == "enter":
            command = self.value.strip()
            self.value = ""
            self.post_message(self.CommandSubmitted(command))
            event.stop()


class StatusBar(Static):
    """Status bar showing system status, DEFCON level, and time."""

    defcon: reactive[int] = reactive(5)
    status: reactive[str] = reactive("ACTIVE")

    def __init__(
        self,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._time_task: asyncio.Task | None = None

    def _render_status(self) -> str:
        """Render the status bar content."""
        from datetime import datetime
        current_time = datetime.utcnow().strftime("%H:%M:%S")
        defcon_display = "█ " * (6 - self.defcon) + "░ " * (self.defcon - 1)
        return f"  STATUS: {self.status}     DEFCON: {defcon_display}[{self.defcon}]     TIME: {current_time} UTC"

    async def _update_time(self) -> None:
        """Update the time display every second."""
        while True:
            self.update(self._render_status())
            await asyncio.sleep(1)

    def on_mount(self) -> None:
        """Start time updates when mounted."""
        self._time_task = asyncio.create_task(self._update_time())

    def on_unmount(self) -> None:
        """Stop time updates when unmounted."""
        if self._time_task:
            self._time_task.cancel()

    def watch_defcon(self, defcon: int) -> None:
        """Update display when DEFCON changes."""
        self.update(self._render_status())

    def watch_status(self, status: str) -> None:
        """Update display when status changes."""
        self.update(self._render_status())


class GameDisplay(Static):
    """Widget for displaying game content with optional border."""

    def __init__(
        self,
        content: str = "",
        title: str = "",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._content = content
        self._title = title

    def set_content(self, content: str, title: str = "") -> None:
        """Set the display content."""
        self._content = content
        self._title = title
        self._render()

    def _render(self) -> None:
        """Render the display with optional title."""
        if self._title:
            output = f"═══ {self._title} ═══\n\n{self._content}"
        else:
            output = self._content
        self.update(output)

    def on_mount(self) -> None:
        """Render content when mounted."""
        self._render()
