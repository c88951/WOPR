"""Simplified Bridge card game."""

from typing import Any
import random

from ..base import CardGame, GameResult


class Bridge(CardGame):
    """Simplified Contract Bridge against WOPR."""

    NAME = "BRIDGE"
    DESCRIPTION = "Simplified contract bridge"
    INSTRUCTIONS = """
BRIDGE (SIMPLIFIED)

You and WOPR-Partner vs WOPR-East and WOPR-West.
Each hand: bid for tricks, then play.

Bidding: BID <number> <suit> (e.g., BID 3 HEARTS) or PASS
Suits: CLUBS, DIAMONDS, HEARTS, SPADES, NO TRUMP

Playing: PLAY <number> to play card at position

Scoring simplified:
  Making contract: tricks × 30
  Overtricks: tricks × 10
  Undertricks: -50 each

Commands: BID, PASS, PLAY, HAND, QUIT
"""

    SUITS_ORDER = ["♣", "♦", "♥", "♠", "NT"]
    SUIT_NAMES = {"CLUBS": "♣", "DIAMONDS": "♦", "HEARTS": "♥", "SPADES": "♠",
                  "NO TRUMP": "NT", "NOTRUMP": "NT", "NT": "NT"}

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._hands: dict[int, list[tuple[str, str]]] = {}  # 0=player, 1=partner, 2=east, 3=west
        self._scores = [0, 0]  # [NS, EW]
        self._contract = None  # (level, suit, declarer)
        self._tricks_won = [0, 0]  # [NS, EW]

    def _card_value(self, card: tuple[str, str]) -> int:
        """Get numeric value for ordering."""
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        return ranks.index(card[0])

    def _deal_hands(self) -> None:
        """Deal 13 cards to each player."""
        self._shuffle_deck()
        for i in range(4):
            self._hands[i] = [self._draw_card() for _ in range(13)]
            self._hands[i].sort(key=lambda c: (["♣", "♦", "♥", "♠"].index(c[1]), self._card_value(c)))

    def _count_points(self, hand: list[tuple[str, str]]) -> int:
        """Count high card points."""
        points = 0
        for card in hand:
            if card[0] == "A":
                points += 4
            elif card[0] == "K":
                points += 3
            elif card[0] == "Q":
                points += 2
            elif card[0] == "J":
                points += 1
        return points

    def _wopr_bid(self, player: int, current_bid: tuple[int, str] | None) -> tuple[int, str] | None:
        """WOPR makes a bid."""
        points = self._count_points(self._hands[player])

        if points < 12:
            return None  # Pass

        # Simple bidding based on points
        if points >= 20:
            level = 4
        elif points >= 16:
            level = 3
        elif points >= 12:
            level = 2
        else:
            level = 1

        # Find longest suit
        suits = {"♣": 0, "♦": 0, "♥": 0, "♠": 0}
        for card in self._hands[player]:
            suits[card[1]] += 1

        best_suit = max(suits.keys(), key=lambda s: (suits[s], self.SUITS_ORDER.index(s)))

        if current_bid:
            cur_level, cur_suit = current_bid
            cur_suit_idx = self.SUITS_ORDER.index(cur_suit)
            best_suit_idx = self.SUITS_ORDER.index(best_suit)

            if level > cur_level:
                return (level, best_suit)
            elif level == cur_level and best_suit_idx > cur_suit_idx:
                return (level, best_suit)
            elif level + 1 <= 7:
                return (level + 1, best_suit)
            return None

        return (level, best_suit)

    def _render_hand(self, hand: list[tuple[str, str]]) -> str:
        """Render hand with position numbers using larger ASCII art."""
        return self._render_hand_art(hand, numbered=True)

    async def _bidding_phase(self) -> tuple[int, str, int] | None:
        """Run bidding phase. Returns (level, suit, declarer) or None if passed out."""
        await self.output("\n=== BIDDING ===\n")
        await self.output(f"YOUR HAND ({self._count_points(self._hands[0])} HCP):\n")
        await self.output(self._render_hand(self._hands[0]) + "\n\n")

        current_bid = None
        declarer = None
        passes = 0
        bidder = 0  # Start with player

        names = ["YOU", "PARTNER", "EAST", "WEST"]

        while passes < 4:
            if bidder == 0:
                # Player bids
                await self.output(f"CURRENT BID: {current_bid[0]} {current_bid[1] if current_bid else 'NONE'}\n")
                await self.output("YOUR BID (e.g., '2 HEARTS' or 'PASS'): ")
                cmd = (await self._input()).strip().upper()

                if cmd in {"QUIT", "Q"}:
                    raise StopIteration()

                if cmd == "PASS":
                    passes += 1
                    await self.output("YOU PASS\n")
                elif cmd.startswith("BID"):
                    cmd = cmd.replace("BID", "").strip()
                    parts = cmd.split()
                    if len(parts) >= 2:
                        try:
                            level = int(parts[0])
                            suit_name = " ".join(parts[1:])
                            suit = self.SUIT_NAMES.get(suit_name)

                            if suit and 1 <= level <= 7:
                                # Validate bid is higher
                                valid = True
                                if current_bid:
                                    cur_level, cur_suit = current_bid
                                    if level < cur_level:
                                        valid = False
                                    elif level == cur_level:
                                        if self.SUITS_ORDER.index(suit) <= self.SUITS_ORDER.index(cur_suit):
                                            valid = False

                                if valid:
                                    current_bid = (level, suit)
                                    declarer = 0
                                    passes = 0
                                    await self.output(f"YOU BID {level} {suit}\n")
                                else:
                                    await self.output("BID MUST BE HIGHER\n")
                                    continue
                            else:
                                await self.output("INVALID BID\n")
                                continue
                        except:
                            await self.output("INVALID FORMAT\n")
                            continue
                else:
                    await self.output("BID or PASS\n")
                    continue

            else:
                # WOPR bids
                bid = self._wopr_bid(bidder, current_bid)
                if bid:
                    current_bid = bid
                    declarer = bidder
                    passes = 0
                    await self.output(f"{names[bidder]} BIDS {bid[0]} {bid[1]}\n")
                else:
                    passes += 1
                    await self.output(f"{names[bidder]} PASSES\n")

            bidder = (bidder + 1) % 4

            if passes >= 3 and current_bid:
                break

        if not current_bid:
            return None

        return (current_bid[0], current_bid[1], declarer)

    async def _play_hand(self, contract: tuple[int, str, int]) -> tuple[int, int]:
        """Play the hand. Returns (NS tricks, EW tricks)."""
        level, trump, declarer = contract
        tricks = [0, 0]  # NS, EW
        leader = (declarer + 1) % 4  # Left of declarer leads

        await self.output(f"\nCONTRACT: {level} {trump} BY {'YOU' if declarer == 0 else 'WOPR'}\n")

        for trick_num in range(13):
            await self.output(f"\n--- TRICK {trick_num + 1} ---\n")
            trick = []
            lead_suit = None

            for i in range(4):
                current = (leader + i) % 4
                hand = self._hands[current]

                if current == 0:
                    await self.output(f"YOUR HAND: {self._render_hand(hand)}\n")
                    if trick:
                        trick_str = " ".join(f"[{self._card_str(c)}]" for _, c in trick)
                        await self.output(f"TRICK: {trick_str}\n")

                    while True:
                        await self.output("PLAY (card number): ")
                        cmd = (await self._input()).strip()

                        if cmd.upper() in {"QUIT", "Q"}:
                            raise StopIteration()

                        try:
                            pos = int(cmd) - 1
                            if 0 <= pos < len(hand):
                                card = hand[pos]
                                # Check if must follow suit
                                if lead_suit:
                                    same_suit = [c for c in hand if c[1] == lead_suit]
                                    if same_suit and card[1] != lead_suit:
                                        await self.output("MUST FOLLOW SUIT\n")
                                        continue

                                hand.remove(card)
                                trick.append((current, card))
                                if not lead_suit:
                                    lead_suit = card[1]
                                await self.output(f"YOU PLAY [{self._card_str(card)}]\n")
                                break
                        except:
                            pass
                        await self.output("INVALID\n")

                else:
                    # WOPR plays
                    valid = [c for c in hand if c[1] == lead_suit] if lead_suit else hand
                    if not valid:
                        valid = hand

                    # Simple: play highest if winning, lowest otherwise
                    card = max(valid, key=self._card_value) if len(trick) == 3 else min(valid, key=self._card_value)
                    hand.remove(card)
                    trick.append((current, card))
                    if not lead_suit:
                        lead_suit = card[1]

                    name = ["YOU", "PARTNER", "EAST", "WEST"][current]
                    await self.output(f"{name} PLAYS [{self._card_str(card)}]\n")

            # Determine winner
            winning_card = trick[0]
            for player, card in trick[1:]:
                if card[1] == trump and winning_card[1][1] != trump:
                    winning_card = (player, card)
                elif card[1] == winning_card[1][1] and self._card_value(card) > self._card_value(winning_card[1]):
                    winning_card = (player, card)

            winner = winning_card[0]
            team = 0 if winner in [0, 1] else 1
            tricks[team] += 1

            name = ["YOU", "PARTNER", "EAST", "WEST"][winner]
            await self.output(f"{name} WINS TRICK (NS: {tricks[0]}, EW: {tricks[1]})\n")
            leader = winner

        return tuple(tricks)

    async def play(self) -> dict[str, Any]:
        """Play Bridge."""
        await self.show_instructions()

        try:
            for hand_num in range(4):  # Play 4 hands
                await self.output(f"\n{'='*40}\nHAND {hand_num + 1}\n")
                await self.output(f"SCORE: NS={self._scores[0]} EW={self._scores[1]}\n")

                self._deal_hands()
                contract = await self._bidding_phase()

                if not contract:
                    await self.output("PASSED OUT - NO SCORE\n")
                    continue

                level, suit, declarer = contract
                ns_tricks, ew_tricks = await self._play_hand(contract)

                # Score
                declaring_team = 0 if declarer in [0, 1] else 1
                tricks_needed = level + 6
                tricks_made = ns_tricks if declaring_team == 0 else ew_tricks

                if tricks_made >= tricks_needed:
                    score = level * 30 + (tricks_made - tricks_needed) * 10
                    self._scores[declaring_team] += score
                    await self.output(f"CONTRACT MADE! +{score}\n")
                else:
                    penalty = (tricks_needed - tricks_made) * 50
                    self._scores[1 - declaring_team] += penalty
                    await self.output(f"CONTRACT DOWN {tricks_needed - tricks_made}. -{penalty}\n")

        except StopIteration:
            pass

        await self.output(f"\nFINAL: NS={self._scores[0]} EW={self._scores[1]}\n")

        if self._scores[0] > self._scores[1]:
            await self.output("YOU WIN!\n")
            return {"result": GameResult.WIN}
        elif self._scores[0] < self._scores[1]:
            await self.output("WOPR WINS\n")
            return {"result": GameResult.LOSE}
        else:
            await self.output("TIE\n")
            return {"result": GameResult.DRAW}
