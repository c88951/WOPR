"""Blackjack card game."""

from typing import Any
import random

from ..base import CardGame, GameResult


class Blackjack(CardGame):
    """Blackjack (21) against WOPR as dealer."""

    NAME = "BLACK JACK"
    DESCRIPTION = "Try to beat the dealer without going over 21"
    INSTRUCTIONS = """
BLACK JACK

Get as close to 21 as possible without going over.
Face cards = 10, Aces = 1 or 11

Commands:
  H or HIT    - Draw another card
  S or STAND  - Keep your current hand
  D or DOUBLE - Double bet and take one card
  Q or QUIT   - Leave the table

Dealer stands on 17.
"""

    def __init__(self, *args, starting_chips: int = 100, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._chips = starting_chips
        self._player_hand: list[tuple[str, str]] = []
        self._dealer_hand: list[tuple[str, str]] = []
        self._bet = 0

    def _card_value(self, card: tuple[str, str]) -> int:
        """Get the value of a card."""
        rank = card[0]
        if rank in ["J", "Q", "K"]:
            return 10
        elif rank == "A":
            return 11  # Will adjust for soft hands
        else:
            return int(rank)

    def _hand_value(self, hand: list[tuple[str, str]]) -> int:
        """Calculate the best value of a hand."""
        value = sum(self._card_value(card) for card in hand)
        aces = sum(1 for card in hand if card[0] == "A")

        # Adjust for aces
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1

        return value

    def _render_hand(self, hand: list[tuple[str, str]], hide_first: bool = False) -> str:
        """Render a hand of cards."""
        if hide_first and hand:
            cards = ["[??]"] + [f"[{self._card_str(c)}]" for c in hand[1:]]
        else:
            cards = [f"[{self._card_str(c)}]" for c in hand]
        return " ".join(cards)

    def _deal_initial(self) -> None:
        """Deal initial hands."""
        self._shuffle_deck()
        self._player_hand = [self._draw_card(), self._draw_card()]
        self._dealer_hand = [self._draw_card(), self._draw_card()]

    async def _show_table(self, reveal_dealer: bool = False) -> None:
        """Display the current table state."""
        await self.output("\n" + "=" * 40 + "\n")
        await self.output(f"CHIPS: {self._chips}    BET: {self._bet}\n")
        await self.output("-" * 40 + "\n")

        # Dealer's hand
        await self.output("DEALER: ")
        await self.output(self._render_hand(self._dealer_hand, hide_first=not reveal_dealer))
        if reveal_dealer:
            await self.output(f"  ({self._hand_value(self._dealer_hand)})")
        await self.output("\n\n")

        # Player's hand
        await self.output("YOU:    ")
        await self.output(self._render_hand(self._player_hand))
        await self.output(f"  ({self._hand_value(self._player_hand)})\n")
        await self.output("=" * 40 + "\n")

    async def _player_turn(self) -> bool:
        """Handle player's turn. Returns True if player busts."""
        while True:
            value = self._hand_value(self._player_hand)

            if value > 21:
                return True  # Bust
            if value == 21:
                return False  # Stand at 21

            await self.output("\n(H)IT, (S)TAND, (D)OUBLE, (Q)UIT: ")
            cmd = (await self._input()).strip().upper()

            if cmd in {"H", "HIT"}:
                card = self._draw_card()
                self._player_hand.append(card)
                await self.output(f"DREW: [{self._card_str(card)}]\n")
                await self._show_table()

            elif cmd in {"S", "STAND"}:
                return False

            elif cmd in {"D", "DOUBLE"}:
                if len(self._player_hand) == 2 and self._chips >= self._bet:
                    self._chips -= self._bet
                    self._bet *= 2
                    card = self._draw_card()
                    self._player_hand.append(card)
                    await self.output(f"DOUBLED! DREW: [{self._card_str(card)}]\n")
                    await self._show_table()
                    return self._hand_value(self._player_hand) > 21
                else:
                    await self.output("CANNOT DOUBLE\n")

            elif cmd in {"Q", "QUIT"}:
                raise StopIteration()

            else:
                await self.output("INVALID COMMAND\n")

    async def _dealer_turn(self) -> None:
        """Handle dealer's turn."""
        await self.output("\nDEALER'S TURN...\n")
        await self._show_table(reveal_dealer=True)

        while self._hand_value(self._dealer_hand) < 17:
            card = self._draw_card()
            self._dealer_hand.append(card)
            await self.output(f"DEALER DRAWS: [{self._card_str(card)}]\n")
            await self._show_table(reveal_dealer=True)

    async def play(self) -> dict[str, Any]:
        """Play Blackjack."""
        await self.show_instructions()
        await self.output(f"\nYOU HAVE {self._chips} CHIPS\n")

        try:
            while self._chips > 0:
                # Get bet
                await self.output(f"\nCHIPS: {self._chips}\n")
                await self.output("BET (or Q to quit): ")
                bet_str = await self._input()

                if bet_str.strip().upper() in {"Q", "QUIT"}:
                    break

                try:
                    self._bet = int(bet_str)
                    if self._bet <= 0 or self._bet > self._chips:
                        await self.output("INVALID BET\n")
                        continue
                except ValueError:
                    await self.output("ENTER A NUMBER\n")
                    continue

                self._chips -= self._bet

                # Deal
                self._deal_initial()
                await self._show_table()

                # Check for blackjack
                player_value = self._hand_value(self._player_hand)
                dealer_value = self._hand_value(self._dealer_hand)

                if player_value == 21:
                    await self.output("BLACKJACK!\n")
                    if dealer_value == 21:
                        await self.output("DEALER ALSO HAS BLACKJACK - PUSH\n")
                        self._chips += self._bet
                    else:
                        await self.output("YOU WIN 3:2!\n")
                        self._chips += int(self._bet * 2.5)
                    continue

                # Player's turn
                bust = await self._player_turn()

                if bust:
                    await self.output("BUST! YOU LOSE\n")
                    continue

                # Dealer's turn
                await self._dealer_turn()
                dealer_value = self._hand_value(self._dealer_hand)
                player_value = self._hand_value(self._player_hand)

                # Determine winner
                if dealer_value > 21:
                    await self.output("DEALER BUSTS! YOU WIN!\n")
                    self._chips += self._bet * 2
                elif player_value > dealer_value:
                    await self.output("YOU WIN!\n")
                    self._chips += self._bet * 2
                elif dealer_value > player_value:
                    await self.output("DEALER WINS\n")
                else:
                    await self.output("PUSH - TIE\n")
                    self._chips += self._bet

        except StopIteration:
            pass

        # Game over
        if self._chips <= 0:
            await self.output("\nYOU'RE BROKE!\n")
            return {"result": GameResult.LOSE, "chips": 0}
        else:
            await self.output(f"\nYOU LEAVE WITH {self._chips} CHIPS\n")
            return {"result": GameResult.QUIT, "chips": self._chips}
