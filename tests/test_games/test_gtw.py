"""Tests for Global Thermonuclear War."""

import pytest
from wopr.games.military.thermonuclear_war.game import GlobalThermonuclearWar
from wopr.games.military.thermonuclear_war.targets import TargetDatabase, Target
from wopr.games.military.thermonuclear_war.simulation import WarSimulation
from wopr.games.military.thermonuclear_war.map import WorldMap


class MockIO:
    def __init__(self, inputs: list[str]):
        self.inputs = inputs.copy()
        self.input_index = 0
        self.output = []

    async def output_callback(self, text: str) -> None:
        self.output.append(text)

    async def input_callback(self) -> str:
        if self.input_index < len(self.inputs):
            result = self.inputs[self.input_index]
            self.input_index += 1
            return result
        return "QUIT"

    def get_output(self) -> str:
        return "".join(self.output)


class TestTargetDatabase:
    """Tests for target database."""

    def test_targets_loaded(self):
        """Test that targets are loaded."""
        db = TargetDatabase()
        all_targets = db.get_all_targets()

        assert len(all_targets) > 0

    def test_us_targets(self):
        """Test US targets exist."""
        db = TargetDatabase()
        us_targets = db.get_targets_for_side("US")

        assert len(us_targets) > 0
        assert all(t.side == "US" for t in us_targets)

    def test_ussr_targets(self):
        """Test USSR targets exist."""
        db = TargetDatabase()
        ussr_targets = db.get_targets_for_side("USSR")

        assert len(ussr_targets) > 0
        assert all(t.side == "USSR" for t in ussr_targets)

    def test_find_target(self):
        """Test finding targets by name."""
        db = TargetDatabase()

        moscow = db.find_target("MOSCOW", "USSR")
        assert moscow is not None
        assert "MOSCOW" in moscow.name

        nyc = db.find_target("NEW YORK", "US")
        assert nyc is not None

    def test_target_types(self):
        """Test different target types."""
        db = TargetDatabase()

        cities = db.get_targets_by_type("CITY")
        assert len(cities) > 0

        military = db.get_targets_by_type("MILITARY")
        assert len(military) > 0

        industrial = db.get_targets_by_type("INDUSTRIAL")
        assert len(industrial) > 0

    def test_city_has_population(self):
        """Test cities have population data."""
        db = TargetDatabase()
        cities = db.get_targets_by_type("CITY")

        for city in cities:
            assert city.population > 0


class TestWarSimulation:
    """Tests for war simulation."""

    def test_calculate_strike(self):
        """Test strike calculation."""
        sim = WarSimulation()
        target = Target(
            name="TEST CITY",
            side="US",
            target_type="CITY",
            latitude=40.0,
            longitude=-74.0,
            population=1_000_000
        )

        result = sim.calculate_strike(target)

        assert result.target == target
        assert isinstance(result.casualties, int)

    def test_casualty_estimate(self):
        """Test casualty estimation."""
        sim = WarSimulation()
        db = TargetDatabase()

        us_cities = db.get_targets_by_type("CITY", "US")[:5]
        estimate = sim.get_casualty_estimate(us_cities)

        assert estimate > 0


class TestWorldMap:
    """Tests for world map."""

    def test_map_render(self):
        """Test map renders."""
        world_map = WorldMap()
        rendered = world_map.render()

        assert len(rendered) > 0
        assert "GLOBAL THERMONUCLEAR WAR" in rendered

    def test_map_missiles(self):
        """Test map missile functionality."""
        world_map = WorldMap()

        # Add a missile
        missile = world_map.add_missile("US_CENTER", "MOSCOW", side="US")
        assert missile is not None
        assert len(world_map._missiles) == 1

        # Advance missiles
        world_map.advance_all()
        assert world_map.has_active_missiles()

        # Clear missiles
        world_map.clear_missiles()
        assert len(world_map._missiles) == 0


@pytest.mark.asyncio
async def test_gtw_quit():
    """Test quitting GTW."""
    io = MockIO(["QUIT"])

    game = GlobalThermonuclearWar(io.output_callback, io.input_callback)
    result = await game.play()

    from wopr.games.base import GameResult
    assert result["result"] == GameResult.QUIT
    assert result["trigger_learning"] is False


@pytest.mark.asyncio
async def test_gtw_side_selection():
    """Test side selection."""
    io = MockIO([
        "1",      # Select US
        "QUIT",   # Quit
    ])

    game = GlobalThermonuclearWar(io.output_callback, io.input_callback)
    result = await game.play()

    output = io.get_output()
    assert "UNITED STATES" in output


@pytest.mark.asyncio
async def test_gtw_target_selection():
    """Test target selection."""
    io = MockIO([
        "1",              # Select US
        "TARGET MOSCOW",  # Select target
        "STATUS",         # Check status
        "QUIT",           # Quit
    ])

    game = GlobalThermonuclearWar(io.output_callback, io.input_callback)
    result = await game.play()

    output = io.get_output()
    assert "TARGET ACQUIRED" in output or "MOSCOW" in output


@pytest.mark.asyncio
async def test_gtw_list_targets():
    """Test listing targets."""
    io = MockIO([
        "1",      # Select US
        "LIST",   # List targets
        "QUIT",   # Quit
    ])

    game = GlobalThermonuclearWar(io.output_callback, io.input_callback)
    result = await game.play()

    output = io.get_output()
    assert "TARGETS" in output
    assert "MOSCOW" in output or "CITY" in output


@pytest.mark.asyncio
async def test_gtw_launch_sequence():
    """Test launch sequence leads to WINNER: NONE."""
    io = MockIO([
        "1",              # Select US
        "TARGET MOSCOW",  # Select target
        "LAUNCH",         # Launch
        "Y",              # Confirm
    ])

    game = GlobalThermonuclearWar(io.output_callback, io.input_callback)
    result = await game.play()

    output = io.get_output()
    assert "WINNER: NONE" in output
    assert result["trigger_learning"] is True
