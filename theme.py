import streamlit as st


def local_css(file_name):
    with open(file_name) as f:
        st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)


def draw_main_table(ss, player, dealer, score, STARTING_CHIPS, split=None):
    score.subheader("Session Stats")
    hands = ss.ties + ss.losses + ss.wins
    if hands == 0:
        score.write("0-0-0 (0.00)")
    else:
        score.write(
            f"{ss.wins}-{ss.losses}-{ss.ties} (W-L-T)"
        )
    if ss.chips is not None:
        diff = ss.chips - STARTING_CHIPS
        score.write(f"{ss.chips} ({'+' if diff >= 0 else '-'}{abs(diff)}) chips left")        
        if hands == 0:
            diff_per_hand = 0
        else:
            diff_per_hand = round(abs(diff) / hands, 2)
        score.write(
            f"{diff_per_hand} chips {'gained' if diff >= 0 else 'lost'} per hand"
        )
    dealer.subheader("Dealer")
    dealer.markdown(
        ss.dealer_hand.get_card_area(ss.dealer_hand.status), unsafe_allow_html=True
    )
    player.subheader("Player")
    player.markdown(
        ss.player_hand.get_card_area(ss.player_hand.status), unsafe_allow_html=True
    )
    if split is not None:
        split.subheader("Player Split")
        split.markdown(
            ss.split_hand.get_card_area(ss.split_hand.status), unsafe_allow_html=True
        )
