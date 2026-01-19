"""Integration tests for the WOPR Textual application."""

import pytest
from textual.pilot import Pilot

# Import the app
from wopr.app import WOPRApp
from wopr.config import WOPRConfig


@pytest.mark.asyncio
async def test_app_launches():
    """Test that the app can be instantiated and run."""
    app = WOPRApp(
        skip_intro=True,
        no_sound=True,
        no_voice=True,
        fast_mode=True,
    )

    async with app.run_test() as pilot:
        # App should launch
        assert app.is_running

        # Should have main UI elements
        assert app.query_one("#header")
        assert app.query_one("#main-content")


@pytest.mark.asyncio
async def test_app_with_config():
    """Test app respects configuration."""
    config = WOPRConfig()
    config.display.typing_speed = 0
    config.audio.enabled = False
    config.gameplay.skip_intro = True

    app = WOPRApp(
        config=config,
        fast_mode=True,
    )

    async with app.run_test() as pilot:
        assert app.is_running


@pytest.mark.asyncio
async def test_app_quit():
    """Test app can quit cleanly."""
    app = WOPRApp(
        skip_intro=True,
        no_sound=True,
        fast_mode=True,
    )

    async with app.run_test() as pilot:
        # Press Ctrl+C to quit
        await pilot.press("ctrl+c")
        # App should be marked for exit


@pytest.mark.asyncio
async def test_terminal_styling():
    """Test terminal styling is applied."""
    app = WOPRApp(
        skip_intro=True,
        no_sound=True,
        fast_mode=True,
    )

    async with app.run_test() as pilot:
        # Check that CSS is applied
        assert "background" in app.CSS.lower() or "color" in app.CSS.lower()


@pytest.mark.asyncio
async def test_status_bar_exists():
    """Test status bar is present."""
    app = WOPRApp(
        skip_intro=True,
        no_sound=True,
        fast_mode=True,
    )

    async with app.run_test() as pilot:
        status_bar = app.query_one("#status-bar")
        assert status_bar is not None
