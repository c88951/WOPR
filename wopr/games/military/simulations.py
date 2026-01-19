"""Military simulation games for WOPR."""

from typing import Any
import random
import asyncio

from ..base import BaseGame, GameResult


class MilitarySimulation(BaseGame):
    """Generic military simulation framework."""

    GAMES = {
        "FIGHTER COMBAT": {
            "description": "Air-to-air combat simulation",
            "units": ["F-15", "F-16", "MIG-29", "SU-27"],
            "mechanics": "energy",  # Energy management dogfighting
        },
        "GUERRILLA ENGAGEMENT": {
            "description": "Counterinsurgency operations",
            "units": ["Infantry", "Special Forces", "Local Militia"],
            "mechanics": "hearts_minds",
        },
        "DESERT WARFARE": {
            "description": "Armored desert operations",
            "units": ["M1 Abrams", "Bradley", "Apache"],
            "mechanics": "maneuver",
        },
        "AIR-TO-GROUND ACTIONS": {
            "description": "Close air support missions",
            "units": ["A-10", "F-111", "AC-130"],
            "mechanics": "strike",
        },
        "THEATERWIDE TACTICAL WARFARE": {
            "description": "Large-scale conventional warfare",
            "units": ["Division", "Brigade", "Regiment"],
            "mechanics": "campaign",
        },
        "THEATERWIDE BIOTOXIC AND CHEMICAL WARFARE": {
            "description": "NBC warfare simulation",
            "units": ["Chemical Unit", "Decontamination Team"],
            "mechanics": "ethical",
        },
    }

    def __init__(
        self,
        game_name: str,
        output_callback,
        input_callback,
        **kwargs
    ) -> None:
        super().__init__(output_callback, input_callback, **kwargs)
        self._game_name = game_name.upper()
        self._game_config = self.GAMES.get(self._game_name, self.GAMES["FIGHTER COMBAT"])
        self._turn = 0
        self._player_score = 0
        self._enemy_score = 0
        self._resources = 100

    async def play(self) -> dict[str, Any]:
        """Play the military simulation."""
        mechanics = self._game_config["mechanics"]

        if mechanics == "energy":
            return await self._play_fighter_combat()
        elif mechanics == "hearts_minds":
            return await self._play_guerrilla()
        elif mechanics == "maneuver":
            return await self._play_desert_warfare()
        elif mechanics == "strike":
            return await self._play_air_to_ground()
        elif mechanics == "campaign":
            return await self._play_tactical_warfare()
        elif mechanics == "ethical":
            return await self._play_biotoxic_warfare()
        else:
            return await self._play_generic()

    async def _play_fighter_combat(self) -> dict[str, Any]:
        """Fighter combat simulation - energy management dogfighting."""
        await self.output(f"\n{self._game_name}\n")
        await self.output("=" * len(self._game_name) + "\n\n")
        await self.output("You are piloting an F-15 Eagle.\n")
        await self.output("Enemy MIG-29 detected!\n\n")

        energy = 100  # Player's energy state
        enemy_energy = 100
        altitude = 20000  # feet
        distance = 10  # nautical miles

        actions = {
            "1": ("CLIMB", "Gain altitude and energy"),
            "2": ("DIVE", "Trade altitude for speed"),
            "3": ("TURN", "Turn to engage"),
            "4": ("FIRE", "Fire missile"),
            "5": ("EVADE", "Defensive maneuver"),
        }

        while True:
            await self.output(f"\n--- TURN {self._turn + 1} ---\n")
            await self.output(f"YOUR ENERGY: {energy}%  ALTITUDE: {altitude}ft\n")
            await self.output(f"ENEMY ENERGY: {enemy_energy}%  DISTANCE: {distance}nm\n\n")

            for key, (name, desc) in actions.items():
                await self.output(f"  {key}. {name} - {desc}\n")

            await self.output("\nACTION (or Q to quit): ")
            cmd = (await self._input()).strip().upper()

            if cmd in {"Q", "QUIT"}:
                return {"result": GameResult.QUIT}

            if cmd == "1":  # Climb
                altitude += 5000
                energy -= 20
                await self.output("CLIMBING...\n")
            elif cmd == "2":  # Dive
                altitude = max(1000, altitude - 5000)
                energy = min(100, energy + 30)
                distance -= 1
                await self.output("DIVING TO ENGAGE...\n")
            elif cmd == "3":  # Turn
                energy -= 15
                distance -= 2
                await self.output("TURNING TO ENGAGE...\n")
            elif cmd == "4":  # Fire
                if distance <= 5 and energy >= 30:
                    hit_chance = 50 + (energy - enemy_energy) // 2
                    if random.randint(1, 100) <= hit_chance:
                        await self.output("*** MISSILE AWAY... HIT! ***\n")
                        await self.output("SPLASH ONE BANDIT!\n")
                        return {"result": GameResult.WIN}
                    else:
                        await self.output("MISSILE MISSED!\n")
                        energy -= 20
                else:
                    await self.output("OUT OF RANGE OR LOW ENERGY\n")
            elif cmd == "5":  # Evade
                energy -= 25
                distance += 3
                await self.output("BREAKING!\n")

            # Enemy AI turn
            if enemy_energy > 30 and distance <= 5:
                if random.randint(1, 100) <= 30:
                    await self.output("\nENEMY FIRES!\n")
                    if random.randint(1, 100) <= 40 - (energy // 5):
                        await self.output("*** YOU'VE BEEN HIT! ***\n")
                        await self.output("EJECT! EJECT! EJECT!\n")
                        return {"result": GameResult.LOSE}
                    else:
                        await self.output("MISSILE EVADED!\n")
            else:
                enemy_energy = min(100, enemy_energy + 10)
                distance -= 1

            self._turn += 1
            if self._turn > 20:
                await self.output("\nBINGO FUEL - RETURNING TO BASE\n")
                return {"result": GameResult.DRAW}

    async def _play_guerrilla(self) -> dict[str, Any]:
        """Guerrilla engagement - hearts and minds."""
        await self.output(f"\n{self._game_name}\n")
        await self.output("=" * len(self._game_name) + "\n\n")
        await self.output("You command counterinsurgency operations.\n")
        await self.output("Win the population's support while neutralizing threats.\n\n")

        population_support = 50  # 0-100
        insurgent_strength = 50  # 0-100
        resources = 100

        actions = {
            "1": ("PATROL", "Secure area, moderate support gain"),
            "2": ("AID", "Provide humanitarian aid, high support gain"),
            "3": ("STRIKE", "Military strike, reduces insurgents but may lose support"),
            "4": ("INTEL", "Gather intelligence"),
        }

        while population_support > 0 and population_support < 100:
            await self.output(f"\n--- MONTH {self._turn + 1} ---\n")
            await self.output(f"POPULATION SUPPORT: {population_support}%\n")
            await self.output(f"INSURGENT STRENGTH: {insurgent_strength}%\n")
            await self.output(f"RESOURCES: {resources}\n\n")

            for key, (name, desc) in actions.items():
                await self.output(f"  {key}. {name} - {desc}\n")

            await self.output("\nACTION (or Q to quit): ")
            cmd = (await self._input()).strip()

            if cmd.upper() in {"Q", "QUIT"}:
                return {"result": GameResult.QUIT}

            if cmd == "1":  # Patrol
                resources -= 10
                population_support += random.randint(2, 8)
                insurgent_strength -= random.randint(0, 5)
                await self.output("PATROLS CONDUCTED\n")
            elif cmd == "2":  # Aid
                resources -= 25
                population_support += random.randint(5, 15)
                await self.output("AID DISTRIBUTED\n")
            elif cmd == "3":  # Strike
                resources -= 20
                insurgent_strength -= random.randint(10, 25)
                civilian_casualties = random.randint(0, 10)
                population_support -= civilian_casualties
                if civilian_casualties > 5:
                    await self.output(f"STRIKE SUCCESSFUL BUT {civilian_casualties} CIVILIAN CASUALTIES\n")
                else:
                    await self.output("STRIKE SUCCESSFUL\n")
            elif cmd == "4":  # Intel
                resources -= 5
                await self.output(f"INTEL GATHERED: INSURGENT HQ LOCATED\n")
                insurgent_strength -= 5

            # Insurgent turn
            if insurgent_strength > 30:
                attack = random.randint(1, insurgent_strength // 10)
                population_support -= attack
                if attack > 3:
                    await self.output(f"INSURGENT ATTACK! SUPPORT DROPS {attack}%\n")

            population_support = max(0, min(100, population_support))
            insurgent_strength = max(0, min(100, insurgent_strength))
            self._turn += 1

            if insurgent_strength <= 10:
                await self.output("\nINSURGENCY DEFEATED!\n")
                return {"result": GameResult.WIN}

        if population_support >= 80:
            await self.output("\nPEACE ACHIEVED THROUGH POPULAR SUPPORT!\n")
            return {"result": GameResult.WIN}
        else:
            await self.output("\nMISSION FAILED - LOST POPULAR SUPPORT\n")
            return {"result": GameResult.LOSE}

    async def _play_desert_warfare(self) -> dict[str, Any]:
        """Desert warfare - armored maneuver."""
        await self.output(f"\n{self._game_name}\n")
        await self.output("=" * len(self._game_name) + "\n\n")
        await self.output("Command your armored battalion across the desert.\n")
        await self.output("Capture objectives while preserving your forces.\n\n")

        tanks = 12
        enemy_tanks = 15
        objectives = 0
        total_objectives = 3

        while tanks > 0 and objectives < total_objectives:
            await self.output(f"\n--- PHASE {self._turn + 1} ---\n")
            await self.output(f"YOUR TANKS: {tanks}\n")
            await self.output(f"ENEMY TANKS: {enemy_tanks}\n")
            await self.output(f"OBJECTIVES: {objectives}/{total_objectives}\n\n")

            await self.output("  1. ADVANCE - Push toward objective\n")
            await self.output("  2. FLANK - Risky maneuver, high reward\n")
            await self.output("  3. DEFEND - Hold position\n")
            await self.output("  4. ARTILLERY - Call fire support\n")

            await self.output("\nORDERS (or Q to quit): ")
            cmd = (await self._input()).strip()

            if cmd.upper() in {"Q", "QUIT"}:
                return {"result": GameResult.QUIT}

            if cmd == "1":  # Advance
                lost = random.randint(1, 3)
                enemy_lost = random.randint(2, 4)
                tanks -= lost
                enemy_tanks -= enemy_lost
                if random.random() < 0.4:
                    objectives += 1
                    await self.output(f"OBJECTIVE CAPTURED! Lost {lost} tanks, destroyed {enemy_lost} enemy.\n")
                else:
                    await self.output(f"ADVANCE STALLED. Lost {lost} tanks, destroyed {enemy_lost} enemy.\n")

            elif cmd == "2":  # Flank
                if random.random() < 0.5:
                    enemy_lost = random.randint(4, 7)
                    enemy_tanks -= enemy_lost
                    objectives += 1
                    await self.output(f"FLANKING ATTACK SUCCESSFUL! Destroyed {enemy_lost} enemy tanks.\n")
                else:
                    lost = random.randint(3, 5)
                    tanks -= lost
                    await self.output(f"FLANKING ATTACK FAILED! Lost {lost} tanks.\n")

            elif cmd == "3":  # Defend
                enemy_lost = random.randint(1, 3)
                enemy_tanks -= enemy_lost
                await self.output(f"HOLDING POSITION. Destroyed {enemy_lost} enemy tanks.\n")

            elif cmd == "4":  # Artillery
                enemy_lost = random.randint(2, 5)
                enemy_tanks -= enemy_lost
                await self.output(f"ARTILLERY STRIKE! Destroyed {enemy_lost} enemy tanks.\n")

            enemy_tanks = max(0, enemy_tanks)
            self._turn += 1

            if enemy_tanks <= 0:
                await self.output("\nENEMY FORCES DESTROYED!\n")
                objectives = total_objectives

        if objectives >= total_objectives:
            await self.output("\nVICTORY! ALL OBJECTIVES CAPTURED!\n")
            return {"result": GameResult.WIN}
        else:
            await self.output("\nDEFEAT - BATTALION DESTROYED\n")
            return {"result": GameResult.LOSE}

    async def _play_air_to_ground(self) -> dict[str, Any]:
        """Air-to-ground actions - strike missions."""
        await self.output(f"\n{self._game_name}\n")
        await self.output("=" * len(self._game_name) + "\n\n")
        await self.output("Plan and execute close air support missions.\n\n")

        sorties = 8
        targets_destroyed = 0
        targets_total = 5
        friendly_losses = 0

        targets = ["ARMOR COLUMN", "SAM SITE", "SUPPLY DEPOT", "COMMAND POST", "BRIDGE"]

        while sorties > 0 and targets_destroyed < targets_total:
            target = targets[targets_destroyed]
            await self.output(f"\n--- MISSION {targets_destroyed + 1} ---\n")
            await self.output(f"TARGET: {target}\n")
            await self.output(f"SORTIES REMAINING: {sorties}\n")
            await self.output(f"TARGETS DESTROYED: {targets_destroyed}/{targets_total}\n\n")

            await self.output("  1. A-10 LOW PASS - High accuracy, vulnerable to AAA\n")
            await self.output("  2. F-111 STANDOFF - Medium accuracy, safer\n")
            await self.output("  3. AC-130 ORBIT - Sustained fire, slow\n")

            await self.output("\nSELECT AIRCRAFT (or Q to quit): ")
            cmd = (await self._input()).strip()

            if cmd.upper() in {"Q", "QUIT"}:
                return {"result": GameResult.QUIT}

            success_chance = 0
            loss_chance = 0

            if cmd == "1":
                success_chance = 85
                loss_chance = 20
                sorties -= 1
            elif cmd == "2":
                success_chance = 60
                loss_chance = 5
                sorties -= 1
            elif cmd == "3":
                success_chance = 75
                loss_chance = 10
                sorties -= 2

            if random.randint(1, 100) <= success_chance:
                targets_destroyed += 1
                await self.output(f"*** {target} DESTROYED! ***\n")
            else:
                await self.output("ATTACK INEFFECTIVE\n")

            if random.randint(1, 100) <= loss_chance:
                friendly_losses += 1
                await self.output("!!! AIRCRAFT LOST TO ENEMY FIRE !!!\n")

            self._turn += 1

        if targets_destroyed >= targets_total:
            await self.output(f"\nMISSION SUCCESS! All targets destroyed.\n")
            await self.output(f"Aircraft lost: {friendly_losses}\n")
            return {"result": GameResult.WIN}
        else:
            await self.output("\nMISSION FAILED - Out of sorties\n")
            return {"result": GameResult.LOSE}

    async def _play_tactical_warfare(self) -> dict[str, Any]:
        """Theaterwide tactical warfare - campaign."""
        await self.output(f"\n{self._game_name}\n")
        await self.output("=" * len(self._game_name) + "\n\n")
        await self.output("Command the theater campaign.\n")
        await self.output("Manage multiple fronts and strategic resources.\n\n")

        fronts = {"NORTH": 50, "CENTER": 50, "SOUTH": 50}  # Control percentage
        reserves = 100
        days = 0

        while all(v > 0 for v in fronts.values()) and any(v < 100 for v in fronts.values()):
            await self.output(f"\n--- DAY {days + 1} ---\n")
            await self.output(f"RESERVES: {reserves}\n")
            for front, control in fronts.items():
                bar = "█" * (control // 10) + "░" * (10 - control // 10)
                await self.output(f"{front}: [{bar}] {control}%\n")

            await self.output("\nALLOCATE RESERVES TO FRONT (N/C/S) or Q to quit: ")
            cmd = (await self._input()).strip().upper()

            if cmd in {"Q", "QUIT"}:
                return {"result": GameResult.QUIT}

            front_map = {"N": "NORTH", "C": "CENTER", "S": "SOUTH"}
            if cmd in front_map:
                front = front_map[cmd]
                await self.output(f"AMOUNT (0-{reserves}): ")
                try:
                    amount = int(await self._input())
                    amount = max(0, min(reserves, amount))
                    reserves -= amount
                    fronts[front] = min(100, fronts[front] + amount // 5)
                    await self.output(f"REINFORCED {front}\n")
                except:
                    pass

            # Enemy counterattacks
            for front in fronts:
                attack = random.randint(5, 15)
                fronts[front] = max(0, fronts[front] - attack)

            reserves = min(100, reserves + 20)
            days += 1

            if days > 30:
                break

        if all(v >= 100 for v in fronts.values()):
            await self.output("\nTOTAL VICTORY!\n")
            return {"result": GameResult.WIN}
        elif any(v <= 0 for v in fronts.values()):
            await self.output("\nFRONT COLLAPSED - DEFEAT\n")
            return {"result": GameResult.LOSE}
        else:
            await self.output("\nSTALEMATE\n")
            return {"result": GameResult.DRAW}

    async def _play_biotoxic_warfare(self) -> dict[str, Any]:
        """Biotoxic and chemical warfare - ethical scenarios."""
        await self.output(f"\n{self._game_name}\n")
        await self.output("=" * len(self._game_name) + "\n\n")
        await self.output("This simulation explores the consequences of NBC warfare.\n")
        await self.output("Your decisions have lasting implications.\n\n")

        await asyncio.sleep(1)

        scenarios = [
            {
                "situation": "Intelligence indicates the enemy is preparing a chemical attack.",
                "options": [
                    ("PREEMPTIVE STRIKE", "Strike first with conventional weapons", 20, -10),
                    ("DEFENSIVE POSTURE", "Prepare defenses and protective gear", 0, 0),
                    ("DIPLOMATIC CHANNEL", "Warn of consequences through back channels", 10, 5),
                ],
            },
            {
                "situation": "Enemy forces have used chemical weapons on your troops.",
                "options": [
                    ("RETALIATE IN KIND", "Chemical counterattack", -50, -30),
                    ("CONVENTIONAL RESPONSE", "Massive conventional strike", 10, -10),
                    ("SEEK CEASEFIRE", "Attempt immediate negotiations", 20, 20),
                ],
            },
            {
                "situation": "A biological agent has been released in a contested city.",
                "options": [
                    ("QUARANTINE", "Seal the city, prioritize containment", 5, 0),
                    ("EVACUATION", "Evacuate civilians despite spread risk", -10, 15),
                    ("MILITARY INTERVENTION", "Send troops to secure the area", 0, -5),
                ],
            },
        ]

        military_score = 0
        ethical_score = 50

        for i, scenario in enumerate(scenarios):
            await self.output(f"\n=== SCENARIO {i + 1} ===\n")
            await self.output(f"{scenario['situation']}\n\n")

            for j, (name, desc, mil, eth) in enumerate(scenario["options"]):
                await self.output(f"  {j + 1}. {name}\n     {desc}\n")

            await self.output("\nYOUR DECISION (or Q to quit): ")
            cmd = (await self._input()).strip()

            if cmd.upper() in {"Q", "QUIT"}:
                return {"result": GameResult.QUIT}

            try:
                choice = int(cmd) - 1
                if 0 <= choice < len(scenario["options"]):
                    name, desc, mil, eth = scenario["options"][choice]
                    military_score += mil
                    ethical_score += eth
                    await self.output(f"\nYOU CHOSE: {name}\n")

                    if eth < 0:
                        await self.output("INTERNATIONAL CONDEMNATION FOLLOWS.\n")
                    elif eth > 0:
                        await self.output("YOUR RESTRAINT IS NOTED.\n")
            except:
                pass

            ethical_score = max(0, min(100, ethical_score))

        await self.output(f"\n=== FINAL ASSESSMENT ===\n")
        await self.output(f"MILITARY OUTCOME: {'FAVORABLE' if military_score > 0 else 'UNFAVORABLE'}\n")
        await self.output(f"ETHICAL STANDING: {ethical_score}%\n")

        if ethical_score >= 50 and military_score >= 0:
            await self.output("\nBUT AT WHAT COST?\n")
            await self.output("THE USE OF SUCH WEAPONS HAS NO WINNER.\n")
        else:
            await self.output("\nTHE CONSEQUENCES WILL BE FELT FOR GENERATIONS.\n")

        # This game always leads to reflection, like GTW
        return {"result": GameResult.NONE, "trigger_learning": False}

    async def _play_generic(self) -> dict[str, Any]:
        """Generic simulation fallback."""
        await self.output(f"\n{self._game_name}\n")
        await self.output(self._game_config.get("description", "Military simulation") + "\n\n")
        await self.output("SIMULATION NOT FULLY IMPLEMENTED\n")
        await self.output("RETURNING TO GAME LIST...\n")
        return {"result": GameResult.QUIT}
