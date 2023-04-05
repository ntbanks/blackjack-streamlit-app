import random
import copy

SUITS = {"S": "♠", "D": "♦", "H": "♥", "C": "♣"}
FACES = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]


class Suit:
    def __init__(self, suit):
        char = SUITS.get(suit, None)
        if char:
            self.char = char
            self.suit = suit
            self.color = "red" if suit in ["H", "D"] else "black"
        else:
            raise ValueError(
                f"Suit.__init__ will only accept one of {list(SUITS.keys())}"
            )

    def __str__(self):
        return self.char

    def __repr__(self):
        return f"Suit(char: {self.char})"


class Face:
    def __init__(self, char):
        self.char = char
        try:
            self.value = int(char)
        except ValueError:
            if char == "A":
                self.value = 11
            elif char in ["J", "Q", "K"]:
                self.value = 10
            else:
                raise ValueError(f"Face.__init__ will only accept one of {FACES}")

    def __str__(self):
        return self.char

    def __repr__(self):
        return f"Face(char: {self.char}, value: {self.value})"


class Card:
    def __init__(self, suit, face, showing=True):
        self.suit = suit
        self.face = face
        self.value = face.value
        self.showing = showing

    def demote_ace(self):
        if self.face.char == "A" and self.value == 11:
            self.value = 1

    def get_html(self, angle, ctr):
        margin = "margin-left:-90px;" if ctr == 0 else ""
        css_class = "card_showing" if self.showing else "card_hidden"

        div = f"<div class='card {css_class}' style='{margin}transform: rotate({angle}deg);'>"
        if self.showing:
            div += f"<div class='card_letter' style='color: {self.suit.color};'>{self.face.char}</div>"
            div += f"<div class='card_suit' style='color: {self.suit.color};'>{self.suit.char}</div>"
        div += "</div>"

        return div

    def __str__(self):
        return f"{self.face}{self.suit}"

    def __repr__(self):
        return f"Card(face: {self.face}, suit: {self.suit}, value: {self.value})"


class Deck:
    def __init__(self, num_decks=6):
        self._cards = []
        for _ in range(num_decks):
            self._cards.extend(self.make_new_deck())

        self.shuffle()

    def make_new_deck(self):
        suits = [Suit(k) for k in SUITS.keys()]
        faces = [Face(f) for f in FACES]

        cards = []
        for s in suits:
            for f in faces:
                cards.append(Card(s, f))

        return cards

    def shuffle(self, seed=None):
        return random.Random(seed).shuffle(self._cards)

    def peek_top_n_cards(self, n=1):
        peek = copy.copy(self._cards[-n:])
        peek.reverse()
        return peek

    def get_top_card(self, showing=True):
        c = self._cards.pop()
        c.showing = showing
        return c

    def __str__(self):
        return f"Deck(len: {len(self._cards)})"

    def __repr__(self):
        first_ten = ["{}".format(c) for c in self.peek_top_n_cards(10)]
        return f"Deck(len: {len(self._cards)}, first_ten: {first_ten})"


class Hand:
    def __init__(self):
        self.cards = []
        self.status = None
        self.bet = 2
        self.double = False

    def get_total(self):
        return sum([c.value for c in self.cards])

    def can_split(self, split_hand):
        if split_hand is not None:
            return False
        if (
            len(self.cards) == 2
            and self.cards[0].face.value == self.cards[1].face.value
        ):
            return True
        return False

    def add_card(self, card):
        if self.get_total() <= 21:
            if card.face.char == "A":
                for c in self.cards:
                    c.demote_ace()

            self.cards.append(card)
            total = self.get_total()

            if self.get_total() > 21:
                values = [c.value for c in self.cards]
                if 11 in values:
                    self.cards[values.index(11)].demote_ace()
                else:
                    self.status = "BUST"
                    return

            if self.get_total() == 21:
                if len(self.cards) == 2:
                    self.status = "BLACKJACK"
                    return
                elif self.status is None:
                    self.status = "STAND"
                    return

    def list_cards(self):
        return ["{}".format(c) for c in self.cards]

    def print_total(self):
        if self.status is not None:
            return f"Total: {self.get_total()}"

        values = [c.value for c in self.cards]
        values_showing = [c.value for c in self.cards if c.showing]

        output_prefix = "Total: " if len(values) == len(values_showing) else "Showing: "
        soft_total = f"{sum(values_showing) - 10}/" if 11 in values_showing else ""

        return f"{output_prefix}{soft_total}{sum(values_showing)}"

    def html_status_string(self):
        if self.status == "BUST":
            return "<span class='bust-text'>BUST</span>"
        elif self.status == "21":
            return "<span class='bust-text'>21!</span>"
        else:
            return ""

    def get_card_area(self, status="ACTIVE"):
        html_string = "<div class='card_area_small'>"

        if len(self.cards) > 0:
            html_string += (
                f"<div class='hand_title'>{status} | {self.print_total()}</div><center>"
            )

            max_angle = len(self.cards) * 10
            shift = -max_angle / 2

            for ctr, c in enumerate(self.cards):
                angle = shift + (ctr * 10)
                html_string += c.get_html(angle, ctr)

            html_string += "</center>"
            html_string += self.html_status_string()

        html_string += "</div>"
        return html_string

    def __str__(self):
        return f"{self.status} ({self.get_total()})| {self.list_cards()}"

    def __repr__(self):
        return f"Hand(status: {self.status}, total: {self.get_total()}, cards: {self.list_cards()})"
