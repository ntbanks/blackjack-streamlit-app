import streamlit as st
import theme
from pathlib import Path

from casino.cards import Deck, Hand, Card, Suit, Face
from casino.decision_maker import dealer_decision, player_decision

CHIPS_PER_BET = 2
STARTING_CHIPS = 200


st.set_page_config(layout="wide", page_title="Learn BlackJack!")

dir_path = Path(__file__).resolve().parent
full_path = dir_path.joinpath(Path('assets/css/main.css'))
theme.local_css(full_path)


ss = st.session_state
if "wins" not in ss:
    ss.wins = 0
if "ties" not in ss:
    ss.ties = 0
if "losses" not in ss:
    ss.losses = 0
if "active" not in ss:
    ss.active = "menu"
if "deck" not in ss:
    deck = Deck()
    deck.shuffle()
    ss["deck"] = deck
if "player_hand" not in ss:
    ss.player_hand = Hand()
if "dealer_hand" not in ss:
    ss.dealer_hand = Hand()
if "hints" not in ss:
    ss.hints = True
if "dealer_type" not in ss:
    ss.dealer_type = "Hit"
if "chips" not in ss:
    ss.chips = None
if "split_hand" not in ss:
    ss.split_hand = None


def handle_split():
    split_hand = Hand()
    split_hand.add_card(ss.player_hand.cards.pop())
    if ss.player_hand.cards[0].face.char == "A":
        ss.player_hand.cards[0].value = 11
        split_hand.cards[0].value = 11

    ss.player_hand.add_card(ss.deck.get_top_card())
    split_hand.add_card(ss.deck.get_top_card())

    return split_hand


def player_decision_input(decision, hand):
    if decision == "hit":
        hand.add_card(ss.deck.get_top_card())
    elif decision == "stand":
        hand.status = "STAND"
    elif decision == "split":
        if ss.chips is not None:
            ss.chips -= CHIPS_PER_BET
        ss.split_hand = handle_split()
    elif decision == "double":
        if ss.chips is not None:
            ss.chips -= CHIPS_PER_BET
        hand.status = "DOUBLE"
        hand.double = True
        hand.add_card(ss.deck.get_top_card())


def first_hand(hints, bets):
    ss.player_hand.add_card(ss.deck.get_top_card())
    ss.dealer_hand.add_card(ss.deck.get_top_card(showing=False))
    ss.player_hand.add_card(ss.deck.get_top_card())
    ss.dealer_hand.add_card(ss.deck.get_top_card())

    ss.active = "player"
    ss.hints = True if hints == "Yes" else False
    if bets == "Yes":
        if ss.chips is None:
            ss.chips = STARTING_CHIPS

        ss.chips -= CHIPS_PER_BET


def new_hand():
    ss.dealer_hand = Hand()
    ss.player_hand = Hand()
    ss.split_hand = None
    first_hand("Yes" if ss.hints else "", "Yes" if ss.chips else "No")


def set_args(hand):
    if ss.hints and len(hand.cards) >= 2 and len(ss.dealer_hand.cards) >= 2:
        comp_hint = player_decision(hand, ss.split_hand, ss.dealer_hand)
    else:
        comp_hint = "None"

    sp_args = {
        "use_container_width": True,
        "type": "primary" if comp_hint == "SPLIT" else "secondary",
        "disabled": False if hand.can_split(ss.split_hand) else True,
    }
    d_args = {
        "use_container_width": True,
        "type": "primary" if comp_hint == "DOUBLE" else "secondary",
        "disabled": True if len(hand.cards) > 2 else False,
    }
    h_args = {
        "use_container_width": True,
        "type": "primary" if comp_hint == "HIT" else "secondary",
    }
    s_args = {
        "use_container_width": True,
        "type": "primary" if comp_hint == "STAND" else "secondary",
    }
    return sp_args, d_args, h_args, s_args


def get_hand_result(hand):
    if hand is None:
        return None

    if hand.double:
        mult = 2
    else:
        mult = 1

    if hand.status == "BUST":
        return -1 * mult

    elif hand.status == "BLACKJACK":
        if ss.dealer_hand.status == "BLACKJACK":
            return 0
        else:
            return 1.5

    elif ss.dealer_hand.status == "BUST":
        return 1 * mult

    elif ss.dealer_hand.status == "BLACKJACK":
        return -1

    elif hand.get_total() == ss.dealer_hand.get_total():
        return 0
    elif hand.get_total() > ss.dealer_hand.get_total():
        return 1 * mult
    elif hand.get_total() < ss.dealer_hand.get_total():
        return -1 * mult


def get_result_string(result):
    if result < 0:
        return f"<h3 style='text-align: center; color: rgba(255,0,0,.9);'>DEALER WINS {'(2x)' if abs(result) == 2 else ''}</h3>"
    elif result == 0:
        return f"<h3 style='text-align: center; color: rgba(255,255,255,.9);'>TIE</h3>"
    else:
        return f"<h3 style='text-align: center; color: rgba(0,255,0,.9);'>PLAYER WINS {'(2x)' if abs(result) == 2 else ''}</h3>"


def get_results(player_col, split_col, bets_col):
    p_hand_res = {
        "hand": ss.player_hand,
        "col": player_col,
        "result": get_hand_result(ss.player_hand),
    }
    hand_results = [p_hand_res]
    if ss.split_hand:
        hand_results.append(
            {
                "hand": ss.split_hand,
                "col": split_col,
                "result": get_hand_result(ss.split_hand),
            }
        )

    chips_bet_total = 0
    chips_back_total = 0
    for hand_res in hand_results:
        chips_bet = CHIPS_PER_BET
        chips_back = 0
        if hand_res["hand"].double:
            chips_bet += CHIPS_PER_BET
        if hand_res["result"] >= 0:
            chips_back = chips_bet + (CHIPS_PER_BET * hand_res["result"])
        hand_res["col"].markdown(
            get_result_string(hand_res["result"]), unsafe_allow_html=True
        )

        chips_bet_total += chips_bet
        chips_back_total += chips_back

    chips_back_total = int(chips_back_total)

    if chips_back_total == chips_bet_total:
        ss.ties += 1
    elif chips_back_total > chips_bet_total:
        ss.wins += 1
    else:
        ss.losses += 1

    ss.chips += chips_back_total

    bets_col.markdown(
        f"<h3 style='text-align:center;'>Bet: {chips_bet_total}<br>Back to player: {chips_back_total}</h3>",
        unsafe_allow_html=True,
    )
    bets_col.button(
        "New Hand", type="primary", on_click=new_hand, use_container_width=True
    )


if ss.active == "dealer":
    if ss.player_hand.status in ["BUST", "BLACKJACK"]:
        if ss.split_hand is not None:
            if ss.split_hand in ["BUST", "BLACKJACK"]:
                ss.active = "results"
                st.experimental_rerun()
        else:
            ss.active = "results"
            st.experimental_rerun()

    if ss.dealer_hand.status is None:
        if dealer_decision(ss.dealer_hand, ss.dealer_type):
            ss.dealer_hand.add_card(ss.deck.get_top_card())
            st.experimental_rerun()
        else:
            ss.dealer_hand.status = "STAND"
            ss.active = "results"
            st.experimental_rerun()
    else:
        ss.active = "results"


if ss.active == "player":
    if ss.dealer_hand.status == "BLACKJACK" or ss.player_hand.status is not None:
        if ss.split_hand is None:
            ss.active = "dealer"
        else:
            ss.active = "split"
        st.experimental_rerun()


if ss.active == "split":
    if ss.split_hand.status is not None:
        if ss.split_hand.status in ["BUST", "BLACKJACK"] and ss.player_hand.status in [
            "BUST",
            "BLACKJACK",
        ]:
            ss.active = "results"
        else:
            ss.active = "dealer"
        st.experimental_rerun()


st.title("Play BlackJack!")

_, menu, _ = st.columns([4, 3, 4])

_, dealer, _, score, _ = st.columns([4, 4, 1, 2, 1])
if ss.split_hand is None:
    _, player, _ = st.columns([4, 4, 4])
    _, sp_input, d_input, h_input, s_input, _ = st.columns([4, 1, 1, 1, 1, 4])
    _, results_col, _ = st.columns([4, 4, 4])
    split_results_col = None
    split_col = None
else:
    _, player, split_col, _ = st.columns([2, 4, 4, 2])
    if ss.player_hand.status is None:
        _, sp_input, d_input, h_input, s_input, _ = st.columns([2, 1, 1, 1, 1, 6])
    else:
        _, sp_input, d_input, h_input, s_input, _ = st.columns([6, 1, 1, 1, 1, 2])
    _, results_col, split_results_col, _ = st.columns([2, 4, 4, 2])

_, bets_col, _ = st.columns([4, 4, 4])


if ss.active == "menu":
    menu.header("Table Options and Rules")
    ss.dealer_type = menu.radio("Dealer behavior on soft 17?", ("Hit", "Stand"))
    bets = menu.radio("Do you want to track bets?", ("Yes", "No"))
    hints = menu.radio(
        "Do you want hints? Buttons will be colored on hover.", ("Yes", "No")
    )
    deal = menu.button(
        "Start Game",
        type="primary",
        on_click=first_hand,
        kwargs={"hints": hints, "bets": bets},
    )


else:
    if ss.active == "player":
        hand = ss.player_hand
    elif ss.active == "split":
        hand = ss.split_hand
    else:
        hand = None

    if hand:
        sp_args, d_args, h_args, s_args = set_args(hand)
        split = sp_input.button(
            "Split",
            on_click=player_decision_input,
            kwargs={"decision": "split", "hand": hand},
            **sp_args,
        )
        double = d_input.button(
            "Double",
            on_click=player_decision_input,
            kwargs={"decision": "double", "hand": hand},
            **d_args,
        )
        hit = h_input.button(
            "Hit",
            on_click=player_decision_input,
            kwargs={"decision": "hit", "hand": hand},
            **h_args,
        )
        stand = s_input.button(
            "Stand",
            on_click=player_decision_input,
            kwargs={"decision": "stand", "hand": hand},
            **s_args,
        )

    if ss.active == "results":
        get_results(results_col, split_results_col, bets_col)

    theme.draw_main_table(ss, player, dealer, score, STARTING_CHIPS, split_col)
