"""Gin Rummy card game."""

from typing import Any
import random
from collections import defaultdict

from ..base import CardGame, GameResult


class GinRummy(CardGame):
    """Gin Rummy against WOPR."""

    NAME = "GIN RUMMY"
    DESCRIPTION = "Classic two-player rummy game"
    INSTRUCTIONS = """
GIN RUMMY

Form melds (sets of 3-4 same rank, or runs of 3+ same suit).
Minimize deadwood (unmelded cards).

Commands:
  DRAW DECK    - Draw from deck
  DRAW DISCARD - Take the discard
  DISCARD n    - Discard card at position n
  KNOCK        - Knock (deadwood <= 10)
  GIN          - Declare gin (no deadwood)
  HAND         - Show your hand
  QUIT         - Leave game

Face cards = 10 points, Aces = 1, others = face value
"""

    def __init__(self, *args, target_score: int = 100, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._player_hand: list[tuple[str, str]] = []
        self._wopr_hand: list[tuple[str, str]] = []
        self._discard_pile: list[tuple[str, str]] = []
        self._player_score = 0
        self._wopr_score = 0
        self._target_score = target_score

    def _card_points(self, card: tuple[str, str]) -> int:
        """Get point value of a card."""
        rank = card[0]
        if rank in ["J", "Q", "K"]:
            return 10
        elif rank == "A":
            return 1
        else:
            return int(rank)

    def _rank_index(self, rank: str) -> int:
        """Get numeric index of a rank for run checking."""
        order = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        return order.index(rank)

    def _find_melds(self, hand: list[tuple[str, str]]) -> tuple[list[list[tuple[str, str]]], list[tuple[str, str]]]:
        """Find all valid melds in a hand. Returns (melds, deadwood)."""
        if not hand:
            return [], []

        # Group by rank and suit
        by_rank = defaultdict(list)
        by_suit = defaultdict(list)
        for card in hand:
            by_rank[card[0]].append(card)
            by_suit[card[1]].append(card)

        melds = []
        used = set()

        # Find sets (3-4 of same rank)
        for rank, cards in by_rank.items():
            if len(cards) >= 3:
                meld = cards[:min(4, len(cards))]
                melds.append(meld)
                for card in meld:
                    used.add(card)

        # Find runs (3+ consecutive same suit)
        for suit, cards in by_suit.items():
            available = [c for c in cards if c not in used]
            available.sort(key=lambda c: self._rank_index(c[0]))

            i = 0
            while i < len(available):
                run = [available[i]]
                j = i + 1
                while j < len(available):
                    if self._rank_index(available[j][0]) == self._rank_index(run[-1][0]) + 1:
                        run.append(available[j])
                        j += 1
                    else:
                        break

                if len(run) >= 3:
                    melds.append(run)
                    for card in run:
                        used.add(card)
                    i = j
                else:
                    i += 1

        deadwood = [c for c in hand if c not in used]
        return melds, deadwood

    def _deadwood_value(self, hand: list[tuple[str, str]]) -> int:
        """Calculate total deadwood points."""
        _, deadwood = self._find_melds(hand)
        return sum(self._card_points(c) for c in deadwood)

    def _render_hand(self, hand: list[tuple[str, str]], numbered: bool = True) -> str:
        """Render hand with position numbers using larger ASCII art."""
        sorted_hand = sorted(hand, key=lambda c: (c[1], self._rank_index(c[0])))
        return self._render_hand_art(sorted_hand, numbered=numbered)

    def _deal_hands(self) -> None:
        """Deal 10 cards to each player."""
        self._shuffle_deck()
        self._player_hand = [self._draw_card() for _ in range(10)]
        self._wopr_hand = [self._draw_card() for _ in range(10)]
        self._discard_pile = [self._draw_card()]

    def _wopr_turn(self) -> bool:
        """Execute WOPR's turn. Returns True if WOPR knocks/gins."""
        # Decide whether to take discard
        discard_top = self._discard_pile[-1] if self._discard_pile else None

        # Simple AI: take discard if it helps
        take_discard = False
        if discard_top:
            test_hand = self._wopr_hand + [discard_top]
            current_deadwood = self._deadwood_value(self._wopr_hand)
            # Estimate improvement
            _, new_deadwood = self._find_melds(test_hand)
            if len(new_deadwood) < len(self._find_melds(self._wopr_hand)[1]):
                take_discard = True

        if take_discard and self._discard_pile:
            self._wopr_hand.append(self._discard_pile.pop())
        else:
            card = self._draw_card()
            if card:
                self._wopr_hand.append(card)

        # Find worst card to discard
        _, deadwood = self._find_melds(self._wopr_hand)
        if deadwood:
            # Discard highest deadwood
            worst = max(deadwood, key=self._card_points)
        else:
            # Gin! But discard anyway for now
            worst = max(self._wopr_hand, key=self._card_points)

        self._wopr_hand.remove(worst)
        self._discard_pile.append(worst)

        # Check for knock/gin
        deadwood_value = self._deadwood_value(self._wopr_hand)
        if deadwood_value == 0:
            return True  # Gin
        elif deadwood_value <= 10:
            return random.random() < 0.3  # Sometimes knock

        return False

    async def play(self) -> dict[str, Any]:
        """Play Gin Rummy."""
        await self.show_instructions()

        while self._player_score < self._target_score and self._wopr_score < self._target_score:
            self._deal_hands()
            await self.output(f"\nSCORE - YOU: {self._player_score}  WOPR: {self._wopr_score}\n")
            await self.output(f"TARGET: {self._target_score}\n\n")

            game_over = False
            player_turn = True

            while not game_over and len(self._deck) > 2:
                if player_turn:
                    # Show state
                    await self.output(f"\nDISCARD: [{self._card_str(self._discard_pile[-1])}]\n")
                    await self.output(f"YOUR HAND ({self._deadwood_value(self._player_hand)} deadwood):\n")
                    await self.output(self._render_hand(self._player_hand) + "\n")

                    # Get command
                    await self.output("\nCOMMAND: ")
                    cmd = (await self._input()).strip().upper()

                    if cmd in {"QUIT", "Q"}:
                        return {"result": GameResult.QUIT}

                    elif cmd == "HAND":
                        melds, deadwood = self._find_melds(self._player_hand)
                        await self.output("MELDS:\n")
                        for meld in melds:
                            await self.output(f"  {self._render_hand(meld, False)}\n")
                        await self.output(f"DEADWOOD: {self._render_hand(deadwood, False)}\n")
                        continue

                    elif cmd == "DRAW DECK":
                        card = self._draw_card()
                        if card:
                            self._player_hand.append(card)
                            await self.output(f"DREW: [{self._card_str(card)}]\n")

                    elif cmd == "DRAW DISCARD":
                        if self._discard_pile:
                            card = self._discard_pile.pop()
                            self._player_hand.append(card)
                            await self.output(f"TOOK: [{self._card_str(card)}]\n")

                    elif cmd.startswith("DISCARD"):
                        try:
                            pos = int(cmd.split()[-1]) - 1
                            sorted_hand = sorted(self._player_hand, key=lambda c: (c[1], self._rank_index(c[0])))
                            if 0 <= pos < len(sorted_hand):
                                card = sorted_hand[pos]
                                self._player_hand.remove(card)
                                self._discard_pile.append(card)
                                await self.output(f"DISCARDED: [{self._card_str(card)}]\n")
                                player_turn = False
                        except:
                            await self.output("INVALID DISCARD\n")

                    elif cmd in {"KNOCK", "GIN"}:
                        deadwood = self._deadwood_value(self._player_hand)
                        if cmd == "GIN" and deadwood > 0:
                            await self.output("NOT GIN - YOU HAVE DEADWOOD\n")
                        elif deadwood > 10:
                            await self.output("DEADWOOD TOO HIGH TO KNOCK\n")
                        else:
                            game_over = True
                            wopr_deadwood = self._deadwood_value(self._wopr_hand)
                            await self.output(f"\nYOU {'GIN' if deadwood == 0 else 'KNOCK'} WITH {deadwood}\n")
                            await self.output(f"WOPR HAS {wopr_deadwood} DEADWOOD\n")

                            if deadwood == 0:
                                points = wopr_deadwood + 25
                                self._player_score += points
                                await self.output(f"GIN! YOU SCORE {points}\n")
                            elif wopr_deadwood < deadwood:
                                points = deadwood - wopr_deadwood + 25
                                self._wopr_score += points
                                await self.output(f"UNDERCUT! WOPR SCORES {points}\n")
                            else:
                                points = wopr_deadwood - deadwood
                                self._player_score += points
                                await self.output(f"YOU SCORE {points}\n")

                    else:
                        await self.output("INVALID COMMAND\n")

                else:
                    # WOPR's turn
                    await self.output("\nWOPR'S TURN...\n")
                    knocked = self._wopr_turn()

                    if knocked:
                        game_over = True
                        wopr_deadwood = self._deadwood_value(self._wopr_hand)
                        player_deadwood = self._deadwood_value(self._player_hand)

                        if wopr_deadwood == 0:
                            points = player_deadwood + 25
                            self._wopr_score += points
                            await self.output(f"WOPR GINS! SCORES {points}\n")
                        elif player_deadwood < wopr_deadwood:
                            points = wopr_deadwood - player_deadwood + 25
                            self._player_score += points
                            await self.output(f"YOU UNDERCUT! SCORE {points}\n")
                        else:
                            points = player_deadwood - wopr_deadwood
                            self._wopr_score += points
                            await self.output(f"WOPR KNOCKS AND SCORES {points}\n")
                    else:
                        await self.output(f"WOPR DISCARDS [{self._card_str(self._discard_pile[-1])}]\n")
                        player_turn = True

            if not game_over:
                await self.output("\nDECK EXHAUSTED - NO SCORE\n")

        # Game complete
        if self._player_score >= self._target_score:
            await self.output(f"\nYOU WIN! {self._player_score} to {self._wopr_score}\n")
            return {"result": GameResult.WIN}
        else:
            await self.output(f"\nWOPR WINS! {self._wopr_score} to {self._player_score}\n")
            return {"result": GameResult.LOSE}
