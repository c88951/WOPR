"""Target database for Global Thermonuclear War."""

from dataclasses import dataclass


@dataclass
class Target:
    """A potential nuclear target."""
    name: str
    side: str  # US or USSR
    target_type: str  # CITY, MILITARY, INDUSTRIAL
    latitude: float
    longitude: float
    population: int = 0
    strategic_value: int = 1


class TargetDatabase:
    """Database of Cold War era targets."""

    def __init__(self) -> None:
        self._targets: list[Target] = []
        self._load_targets()

    def _load_targets(self) -> None:
        """Load target data."""
        # US Cities
        us_cities = [
            ("NEW YORK", 40.7128, -74.0060, 7_900_000),
            ("LOS ANGELES", 34.0522, -118.2437, 3_500_000),
            ("CHICAGO", 41.8781, -87.6298, 3_000_000),
            ("HOUSTON", 29.7604, -95.3698, 1_600_000),
            ("PHILADELPHIA", 39.9526, -75.1652, 1_700_000),
            ("PHOENIX", 33.4484, -112.0740, 800_000),
            ("SAN ANTONIO", 29.4241, -98.4936, 800_000),
            ("SAN DIEGO", 32.7157, -117.1611, 900_000),
            ("DALLAS", 32.7767, -96.7970, 1_000_000),
            ("SAN JOSE", 37.3382, -121.8863, 600_000),
            ("DETROIT", 42.3314, -83.0458, 1_200_000),
            ("SAN FRANCISCO", 37.7749, -122.4194, 700_000),
            ("BOSTON", 42.3601, -71.0589, 600_000),
            ("SEATTLE", 47.6062, -122.3321, 500_000),
            ("DENVER", 39.7392, -104.9903, 500_000),
            ("WASHINGTON DC", 38.9072, -77.0369, 700_000),
            ("ATLANTA", 33.7490, -84.3880, 400_000),
            ("MIAMI", 25.7617, -80.1918, 400_000),
            ("MINNEAPOLIS", 44.9778, -93.2650, 400_000),
            ("ST LOUIS", 38.6270, -90.1994, 500_000),
        ]

        for name, lat, lon, pop in us_cities:
            self._targets.append(Target(
                name=name, side="US", target_type="CITY",
                latitude=lat, longitude=lon, population=pop
            ))

        # US Military
        us_military = [
            ("NORAD CHEYENNE MOUNTAIN", 38.7442, -104.8467),
            ("OFFUTT AFB OMAHA", 41.1183, -95.9125),
            ("MINUTEMAN SILOS MONTANA", 47.5, -111.0),
            ("MINUTEMAN SILOS WYOMING", 41.0, -104.0),
            ("MINUTEMAN SILOS NORTH DAKOTA", 48.0, -101.0),
            ("NORFOLK NAVAL BASE", 36.9460, -76.3088),
            ("KINGS BAY SUBMARINE BASE", 30.7969, -81.5153),
            ("BANGOR SUBMARINE BASE", 47.7432, -122.7149),
            ("NELLIS AFB", 36.2360, -115.0340),
            ("WRIGHT-PATTERSON AFB", 39.8261, -84.0446),
        ]

        for name, lat, lon in us_military:
            self._targets.append(Target(
                name=name, side="US", target_type="MILITARY",
                latitude=lat, longitude=lon, strategic_value=5
            ))

        # USSR Cities
        ussr_cities = [
            ("MOSCOW", 55.7558, 37.6173, 8_000_000),
            ("LENINGRAD", 59.9311, 30.3609, 4_500_000),
            ("KIEV", 50.4501, 30.5234, 2_500_000),
            ("TASHKENT", 41.2995, 69.2401, 2_000_000),
            ("BAKU", 40.4093, 49.8671, 1_700_000),
            ("KHARKOV", 49.9935, 36.2304, 1_500_000),
            ("MINSK", 53.9006, 27.5590, 1_400_000),
            ("GORKY", 56.2965, 43.9361, 1_300_000),
            ("NOVOSIBIRSK", 55.0084, 82.9357, 1_400_000),
            ("SVERDLOVSK", 56.8389, 60.6057, 1_200_000),
            ("KUIBYSHEV", 53.1959, 50.1003, 1_200_000),
            ("TBILISI", 41.7151, 44.8271, 1_100_000),
            ("ODESSA", 46.4825, 30.7233, 1_000_000),
            ("CHELYABINSK", 55.1644, 61.4368, 1_000_000),
            ("DNEPROPETROVSK", 48.4647, 35.0462, 1_000_000),
            ("KAZAN", 55.8304, 49.0661, 1_000_000),
            ("VOLGOGRAD", 48.7080, 44.5133, 950_000),
            ("ALMA-ATA", 43.2220, 76.8512, 900_000),
            ("RIGA", 56.9496, 24.1052, 850_000),
            ("VLADIVOSTOK", 43.1332, 131.9113, 600_000),
        ]

        for name, lat, lon, pop in ussr_cities:
            self._targets.append(Target(
                name=name, side="USSR", target_type="CITY",
                latitude=lat, longitude=lon, population=pop
            ))

        # USSR Military
        ussr_military = [
            ("MOSCOW COMMAND BUNKER", 55.75, 37.62),
            ("PLESETSK COSMODROME", 62.9271, 40.5775),
            ("BAIKONUR COSMODROME", 45.9650, 63.3050),
            ("SEVEROMORSK NAVAL BASE", 69.0728, 33.4234),
            ("PETROPAVLOVSK SUB BASE", 53.0167, 158.6500),
            ("ENGELS AIR BASE", 51.4833, 46.2000),
            ("DOMBAROVSKY ICBM BASE", 50.7667, 59.5333),
            ("ALEYSK ICBM BASE", 52.5000, 83.4167),
            ("KARTALY ICBM BASE", 53.0667, 60.6500),
            ("TATISHCHEVO ICBM BASE", 51.7000, 45.7500),
        ]

        for name, lat, lon in ussr_military:
            self._targets.append(Target(
                name=name, side="USSR", target_type="MILITARY",
                latitude=lat, longitude=lon, strategic_value=5
            ))

        # Industrial targets
        us_industrial = [
            ("PITTSBURGH STEEL WORKS", 40.4406, -79.9959),
            ("GARY STEEL MILLS", 41.5934, -87.3464),
            ("HOUSTON REFINERIES", 29.76, -95.37),
            ("SILICON VALLEY", 37.3861, -122.0839),
            ("OAK RIDGE FACILITY", 36.0104, -84.2696),
        ]

        for name, lat, lon in us_industrial:
            self._targets.append(Target(
                name=name, side="US", target_type="INDUSTRIAL",
                latitude=lat, longitude=lon, strategic_value=3
            ))

        ussr_industrial = [
            ("MAGNITOGORSK STEEL", 53.3933, 59.0386),
            ("NIZHNY TAGIL TANK FACTORY", 57.9119, 59.9650),
            ("KRASNOYARSK-26 PLANT", 56.2500, 93.5000),
            ("CHELYABINSK-40 COMPLEX", 55.75, 60.75),
            ("TOMSK-7 FACILITY", 56.4833, 85.0500),
        ]

        for name, lat, lon in ussr_industrial:
            self._targets.append(Target(
                name=name, side="USSR", target_type="INDUSTRIAL",
                latitude=lat, longitude=lon, strategic_value=3
            ))

    def get_all_targets(self) -> list[Target]:
        """Get all targets."""
        return self._targets.copy()

    def get_targets_for_side(self, side: str) -> list[Target]:
        """Get targets for a specific side."""
        side = side.upper()
        return [t for t in self._targets if t.side == side]

    def find_target(self, name: str, side: str = "") -> Target | None:
        """Find a target by name."""
        name = name.upper()
        for target in self._targets:
            if side and target.side != side.upper():
                continue
            if name in target.name or target.name.startswith(name):
                return target
        return None

    def get_targets_by_type(self, target_type: str, side: str = "") -> list[Target]:
        """Get targets by type."""
        target_type = target_type.upper()
        results = [t for t in self._targets if t.target_type == target_type]
        if side:
            results = [t for t in results if t.side == side.upper()]
        return results
