"""Five-card draw poker game."""

from typing import Any
import random
from collections import Counter

from ..base import CardGame, GameResult


class Poker(CardGame):
    """Five-card draw poker against WOPR."""

    NAME = "POKER"
    DESCRIPTION = "Five-card draw poker"
    INSTRUCTIONS = """
POKER - FIVE CARD DRAW

You play against WOPR. Each player is dealt 5 cards.
You may discard up to 3 cards and draw new ones.

Hand rankings (highest to lowest):
  Royal Flush, Straight Flush, Four of a Kind,
  Full House, Flush, Straight, Three of a Kind,
  Two Pair, One Pair, High Card

Commands:
  DISCARD 1,2,3  - Discard cards by position
  KEEP           - Keep all cards
  FOLD           - Forfeit the hand
  QUIT           - Leave the game
"""

    HAND_RANKS = [
        "HIGH CARD",
        "ONE PAIR",
        "TWO PAIR",
        "THREE OF A KIND",
        "STRAIGHT",
        "FLUSH",
        "FULL HOUSE",
        "FOUR OF A KIND",
        "STRAIGHT FLUSH",
        "ROYAL FLUSH",
    ]

    def __init__(self, *args, starting_chips: int = 100, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._chips = starting_chips
        self._player_hand: list[tuple[str, str]] = []
        self._wopr_hand: list[tuple[str, str]] = []
        self._pot = 0
        self._ante = 5

    def _rank_value(self, rank: str) -> int:
        """Get numeric value of a rank."""
        if rank == "A":
            return 14
        elif rank == "K":
            return 13
        elif rank == "Q":
            return 12
        elif rank == "J":
            return 11
        else:
            return int(rank)

    def _evaluate_hand(self, hand: list[tuple[str, str]]) -> tuple[int, list[int]]:
        """Evaluate a poker hand. Returns (rank_index, tiebreaker_values)."""
        ranks = sorted([self._rank_value(c[0]) for c in hand], reverse=True)
        suits = [c[1] for c in hand]
        rank_counts = Counter(ranks)
        most_common = rank_counts.most_common()

        is_flush = len(set(suits)) == 1
        is_straight = (max(ranks) - min(ranks) == 4 and len(set(ranks)) == 5) or \
                      ranks == [14, 5, 4, 3, 2]  # Wheel

        if is_straight and ranks == [14, 5, 4, 3, 2]:
            ranks = [5, 4, 3, 2, 1]  # Ace-low straight

        if is_straight and is_flush:
            if ranks == [14, 13, 12, 11, 10]:
                return (9, ranks)  # Royal flush
            return (8, ranks)  # Straight flush

        if most_common[0][1] == 4:
            return (7, ranks)  # Four of a kind

        if most_common[0][1] == 3 and most_common[1][1] == 2:
            return (6, ranks)  # Full house

        if is_flush:
            return (5, ranks)  # Flush

        if is_straight:
            return (4, ranks)  # Straight

        if most_common[0][1] == 3:
            return (3, ranks)  # Three of a kind

        if most_common[0][1] == 2 and most_common[1][1] == 2:
            return (2, ranks)  # Two pair

        if most_common[0][1] == 2:
            return (1, ranks)  # One pair

        return (0, ranks)  # High card

    def _render_hand(self, hand: list[tuple[str, str]], numbered: bool = False) -> str:
        """Render a hand with optional position numbers."""
        cards = []
        for i, card in enumerate(hand):
            card_str = f"[{self._card_str(card)}]"
            if numbered:
                cards.append(f"{i + 1}:{card_str}")
            else:
                cards.append(card_str)
        return " ".join(cards)

    def _deal_hands(self) -> None:
        """Deal fresh hands to both players."""
        self._shuffle_deck()
        self._player_hand = [self._draw_card() for _ in range(5)]
        self._wopr_hand = [self._draw_card() for _ in range(5)]

    def _wopr_discard(self) -> None:
        """WOPR decides which cards to discard."""
        rank_idx, _ = self._evaluate_hand(self._wopr_hand)

        # Simple AI: keep pairs and high cards
        if rank_idx >= 3:  # Three of a kind or better
            return  # Keep all

        ranks = [self._rank_value(c[0]) for c in self._wopr_hand]
        rank_counts = Counter(ranks)

        # Keep pairs
        keep_ranks = {r for r, count in rank_counts.items() if count >= 2}
        if not keep_ranks:
            # Keep highest two cards
            sorted_ranks = sorted(set(ranks), reverse=True)[:2]
            keep_ranks = set(sorted_ranks)

        # Discard and draw
        new_hand = []
        for card in self._wopr_hand:
            if self._rank_value(card[0]) in keep_ranks:
                new_hand.append(card)
            else:
                new_card = self._draw_card()
                if new_card:
                    new_hand.append(new_card)

        self._wopr_hand = new_hand

    async def play(self) -> dict[str, Any]:
        """Play poker."""
        await self.show_instructions()

        while self._chips > self._ante:
            # Ante up
            self._pot = self._ante * 2
            self._chips -= self._ante
            await self.output(f"\nCHIPS: {self._chips}  ANTE: {self._ante}  POT: {self._pot}\n")

            # Deal
            self._deal_hands()
            await self.output("\nYOUR HAND:\n")
            await self.output(self._render_hand(self._player_hand, numbered=True) + "\n")

            # Player discard phase
            await self.output("\nDISCARD positions (e.g., 1,3,5) or KEEP all: ")
            cmd = (await self._input()).strip().upper()

            if cmd in {"FOLD", "F"}:
                await self.output("YOU FOLD. WOPR WINS POT.\n")
                continue

            if cmd in {"QUIT", "Q"}:
                break

            if cmd not in {"KEEP", "K", ""}:
                try:
                    positions = [int(p.strip()) - 1 for p in cmd.replace("DISCARD", "").split(",")]
                    positions = [p for p in positions if 0 <= p < 5]

                    for pos in sorted(positions, reverse=True):
                        new_card = self._draw_card()
                        if new_card:
                            self._player_hand[pos] = new_card

                    await self.output(f"DREW {len(positions)} NEW CARDS\n")
                except:
                    await self.output("KEEPING ALL CARDS\n")

            await self.output("\nYOUR HAND:\n")
            await self.output(self._render_hand(self._player_hand) + "\n")

            # WOPR discard
            old_wopr = len(self._wopr_hand)
            self._wopr_discard()
            discarded = old_wopr - len(self._wopr_hand) + (5 - len(self._wopr_hand))
            if discarded > 0:
                await self.output(f"WOPR DISCARDS {discarded} CARDS\n")
            else:
                await self.output("WOPR KEEPS ALL CARDS\n")

            # Showdown
            await self.output("\n*** SHOWDOWN ***\n\n")
            await self.output(f"YOUR HAND:  {self._render_hand(self._player_hand)}\n")
            await self.output(f"WOPR HAND:  {self._render_hand(self._wopr_hand)}\n\n")

            player_rank = self._evaluate_hand(self._player_hand)
            wopr_rank = self._evaluate_hand(self._wopr_hand)

            await self.output(f"YOU:  {self.HAND_RANKS[player_rank[0]]}\n")
            await self.output(f"WOPR: {self.HAND_RANKS[wopr_rank[0]]}\n\n")

            if player_rank > wopr_rank:
                await self.output("YOU WIN!\n")
                self._chips += self._pot
            elif wopr_rank > player_rank:
                await self.output("WOPR WINS\n")
            else:
                await self.output("TIE - SPLIT POT\n")
                self._chips += self._pot // 2

        if self._chips <= self._ante:
            await self.output("\nNOT ENOUGH CHIPS TO CONTINUE\n")
            return {"result": GameResult.LOSE, "chips": self._chips}

        await self.output(f"\nYOU LEAVE WITH {self._chips} CHIPS\n")
        return {"result": GameResult.QUIT, "chips": self._chips}
