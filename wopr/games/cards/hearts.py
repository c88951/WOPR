"""Hearts card game."""

from typing import Any
import random
from collections import defaultdict

from ..base import CardGame, GameResult


class Hearts(CardGame):
    """Hearts - four player game with WOPR controlling 3 opponents."""

    NAME = "HEARTS"
    DESCRIPTION = "Avoid hearts and the Queen of Spades"
    INSTRUCTIONS = """
HEARTS

Avoid taking hearts (1 point each) and Queen of Spades (13 points).
Or "shoot the moon" - take all hearts and the Queen for 0 points
while opponents get 26 each!

Pass 3 cards to another player each hand (except every 4th hand).
2 of Clubs leads the first trick. Must follow suit if possible.
Hearts can't be led until "broken" (played when unable to follow).

First to 100 points loses. Lowest score wins.

Commands:
  PLAY n  - Play card at position n
  HAND    - Show your hand
  SCORE   - Show scores
  QUIT    - Leave game
"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._hands: dict[int, list[tuple[str, str]]] = {}  # 0=player, 1-3=WOPR
        self._scores = [0, 0, 0, 0]
        self._trick: list[tuple[int, tuple[str, str]]] = []
        self._hearts_broken = False
        self._hand_number = 0

    def _card_value(self, card: tuple[str, str]) -> int:
        """Get numeric value for ordering."""
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        return ranks.index(card[0])

    def _suit_order(self, suit: str) -> int:
        """Get suit order for sorting."""
        return ["♣", "♦", "♠", "♥"].index(suit)

    def _sort_hand(self, hand: list[tuple[str, str]]) -> list[tuple[str, str]]:
        """Sort hand by suit then rank."""
        return sorted(hand, key=lambda c: (self._suit_order(c[1]), self._card_value(c)))

    def _deal_hands(self) -> None:
        """Deal 13 cards to each player."""
        self._shuffle_deck()
        for i in range(4):
            self._hands[i] = [self._draw_card() for _ in range(13)]
            self._hands[i] = self._sort_hand(self._hands[i])
        self._hearts_broken = False

    def _card_points(self, card: tuple[str, str]) -> int:
        """Get point value of a card."""
        if card[1] == "♥":
            return 1
        if card == ("Q", "♠"):
            return 13
        return 0

    def _trick_points(self, trick: list[tuple[int, tuple[str, str]]]) -> int:
        """Calculate points in a trick."""
        return sum(self._card_points(card) for _, card in trick)

    def _trick_winner(self, trick: list[tuple[int, tuple[str, str]]]) -> int:
        """Determine who won the trick."""
        lead_suit = trick[0][1][1]
        winner = trick[0]
        for player, card in trick[1:]:
            if card[1] == lead_suit and self._card_value(card) > self._card_value(winner[1]):
                winner = (player, card)
        return winner[0]

    def _valid_plays(self, player: int, lead_suit: str | None) -> list[tuple[str, str]]:
        """Get valid cards to play."""
        hand = self._hands[player]

        # First trick - 2 of clubs must lead
        if not self._trick and not lead_suit:
            if ("2", "♣") in hand:
                return [("2", "♣")]

        # Must follow suit if possible
        if lead_suit:
            same_suit = [c for c in hand if c[1] == lead_suit]
            if same_suit:
                return same_suit

        # First trick - can't play hearts or Q of spades
        if len(self._trick) < 4 and not lead_suit:
            non_points = [c for c in hand if self._card_points(c) == 0]
            if non_points:
                return non_points

        # Leading - can't lead hearts until broken
        if not lead_suit and not self._hearts_broken:
            non_hearts = [c for c in hand if c[1] != "♥"]
            if non_hearts:
                return non_hearts

        return hand  # Any card

    def _wopr_play(self, player: int, lead_suit: str | None) -> tuple[str, str]:
        """WOPR selects a card to play."""
        valid = self._valid_plays(player, lead_suit)

        # Simple strategy: avoid taking points
        if lead_suit:
            # Try to play low card of suit
            same_suit = [c for c in valid if c[1] == lead_suit]
            if same_suit:
                return min(same_suit, key=self._card_value)
            # Dump high point cards
            point_cards = [c for c in valid if self._card_points(c) > 0]
            if point_cards:
                return max(point_cards, key=self._card_points)
            # Play highest non-point card
            return max(valid, key=self._card_value)
        else:
            # Leading - play lowest non-heart
            non_hearts = [c for c in valid if c[1] != "♥"]
            if non_hearts:
                return min(non_hearts, key=self._card_value)
            return min(valid, key=self._card_value)

    def _render_hand(self, hand: list[tuple[str, str]]) -> str:
        """Render hand with position numbers."""
        parts = []
        for i, card in enumerate(self._sort_hand(hand)):
            parts.append(f"{i + 1}:[{self._card_str(card)}]")
        return " ".join(parts)

    async def _play_hand(self) -> list[int]:
        """Play one hand. Returns points taken by each player."""
        self._deal_hands()
        points = [0, 0, 0, 0]
        leader = 0

        # Find who has 2 of clubs
        for i in range(4):
            if ("2", "♣") in self._hands[i]:
                leader = i
                break

        for trick_num in range(13):
            self._trick = []
            lead_suit = None

            await self.output(f"\n=== TRICK {trick_num + 1} ===\n")

            for i in range(4):
                current = (leader + i) % 4

                if current == 0:
                    # Player's turn
                    await self.output(f"\nYOUR HAND:\n{self._render_hand(self._hands[0])}\n")
                    if self._trick:
                        trick_str = " ".join(f"[{self._card_str(c)}]" for _, c in self._trick)
                        await self.output(f"CURRENT TRICK: {trick_str}\n")

                    valid = self._valid_plays(0, lead_suit)
                    sorted_hand = self._sort_hand(self._hands[0])

                    while True:
                        await self.output("PLAY (card number): ")
                        cmd = (await self._input()).strip().upper()

                        if cmd in {"QUIT", "Q"}:
                            raise StopIteration()

                        if cmd == "HAND":
                            await self.output(f"{self._render_hand(self._hands[0])}\n")
                            continue

                        if cmd == "SCORE":
                            await self.output(f"SCORES: YOU={self._scores[0]} ")
                            await self.output(f"WOPR-A={self._scores[1]} ")
                            await self.output(f"WOPR-B={self._scores[2]} ")
                            await self.output(f"WOPR-C={self._scores[3]}\n")
                            continue

                        try:
                            pos = int(cmd.split()[-1]) - 1
                            if 0 <= pos < len(sorted_hand):
                                card = sorted_hand[pos]
                                if card in valid:
                                    self._hands[0].remove(card)
                                    self._trick.append((0, card))
                                    if not lead_suit:
                                        lead_suit = card[1]
                                    if card[1] == "♥":
                                        self._hearts_broken = True
                                    await self.output(f"YOU PLAY: [{self._card_str(card)}]\n")
                                    break
                                else:
                                    await self.output("INVALID PLAY\n")
                            else:
                                await self.output("INVALID CARD NUMBER\n")
                        except:
                            await self.output("ENTER CARD NUMBER\n")

                else:
                    # WOPR's turn
                    card = self._wopr_play(current, lead_suit)
                    self._hands[current].remove(card)
                    self._trick.append((current, card))
                    if not lead_suit:
                        lead_suit = card[1]
                    if card[1] == "♥":
                        self._hearts_broken = True
                    name = ["YOU", "WOPR-A", "WOPR-B", "WOPR-C"][current]
                    await self.output(f"{name} PLAYS: [{self._card_str(card)}]\n")

            # Determine winner
            winner = self._trick_winner(self._trick)
            trick_pts = self._trick_points(self._trick)
            points[winner] += trick_pts

            name = ["YOU", "WOPR-A", "WOPR-B", "WOPR-C"][winner]
            await self.output(f"\n{name} TAKES TRICK ({trick_pts} points)\n")
            leader = winner

        return points

    async def play(self) -> dict[str, Any]:
        """Play Hearts."""
        await self.show_instructions()

        try:
            while max(self._scores) < 100:
                await self.output(f"\n{'='*40}\n")
                await self.output(f"HAND {self._hand_number + 1}\n")
                await self.output(f"SCORES: YOU={self._scores[0]} WOPR-A={self._scores[1]} ")
                await self.output(f"WOPR-B={self._scores[2]} WOPR-C={self._scores[3]}\n")

                points = await self._play_hand()

                # Check for shoot the moon
                for i in range(4):
                    if points[i] == 26:
                        await self.output(f"\n{'['*3} SHOT THE MOON! {']'*3}\n")
                        for j in range(4):
                            if j != i:
                                self._scores[j] += 26
                        points = [0, 0, 0, 0]
                        break

                for i in range(4):
                    self._scores[i] += points[i]

                self._hand_number += 1

                await self.output(f"\nHAND COMPLETE. POINTS THIS HAND:\n")
                await self.output(f"YOU: {points[0]}  WOPR-A: {points[1]}  ")
                await self.output(f"WOPR-B: {points[2]}  WOPR-C: {points[3]}\n")

        except StopIteration:
            pass

        # Determine winner
        await self.output(f"\nFINAL SCORES:\n")
        await self.output(f"YOU: {self._scores[0]}  WOPR-A: {self._scores[1]}  ")
        await self.output(f"WOPR-B: {self._scores[2]}  WOPR-C: {self._scores[3]}\n")

        if self._scores[0] == min(self._scores):
            await self.output("YOU WIN!\n")
            return {"result": GameResult.WIN}
        else:
            await self.output("WOPR WINS\n")
            return {"result": GameResult.LOSE}
