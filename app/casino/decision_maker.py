def dealer_decision(dealer_hand, dealer_type=None):
    if dealer_type == "STAND":
        if dealer_hand.get_total() < 17:
            return True
        else:
            return False
    else:
        if dealer_hand.get_total() < 17:
            return True
        elif dealer_hand.get_total() == 17 and 11 in [
            c.value for c in dealer_hand.cards
        ]:
            return True
        else:
            return False


def decision_basic_hit(player_hand, dealer_up_value):
    hard_hits = {
        12: [2, 3, 7, 8, 9, 10, 11],
        13: [7, 8, 9, 10, 11],
        14: [7, 8, 9, 10, 11],
        15: [7, 8, 9, 10, 11],
        16: [7, 8, 9, 10, 11],
    }

    soft_hits = {
        13: range(2, 12),
        14: range(2, 12),
        15: range(2, 12),
        16: range(2, 12),
        17: range(2, 12),
        18: [9, 10, 11],
    }

    if 11 in [c.value for c in player_hand.cards]:
        return (
            True
            if dealer_up_value in soft_hits.get(player_hand.get_total(), [])
            else False
        )
    else:
        if player_hand.get_total() <= 11:
            return True
        elif player_hand.get_total() >= 17:
            return False
        else:
            return (
                True
                if dealer_up_value in hard_hits.get(player_hand.get_total(), [])
                else False
            )


def decision_double(player_hand, dealer_up_value):
    soft_doubles = {
        13: [5, 6],
        14: [5, 6],
        15: [4, 5, 6],
        16: [4, 5, 6],
        17: [3, 4, 5, 6],
        18: [2, 3, 4, 5, 6],
        19: [6],
    }

    hard_doubles = {
        9: [3, 4, 5, 6],
        10: range(2, 10),
        11: range(2, 12),  # always
    }

    if 11 in [c.value for c in player_hand.cards]:
        return (
            True
            if dealer_up_value in soft_doubles.get(player_hand.get_total(), [])
            else False
        )
    else:
        return (
            True
            if dealer_up_value in hard_doubles.get(player_hand.get_total(), [])
            else False
        )


def decision_split(player_value, dealer_up_value, das_input):
    splits = {
        2: [4, 5, 6, 7],  # 2,3 if DAS
        3: [4, 5, 6, 7],  # 2,3 if DAS
        4: [],  # 5,6 if DAS
        5: [],  # never
        6: [3, 4, 5, 6],  # 2 if DAS
        7: [2, 3, 4, 5, 6, 7],
        8: range(2, 12),  # always
        9: [2, 3, 4, 5, 6, 8, 9],
        10: [],  # never
        11: range(2, 12),  # always
    }

    # add a few splits for when casino allows DAS (Double After Split)
    if das_input:
        splits[2].extend([2, 3])
        splits[3].extend([2, 3])
        splits[4].extend([5, 6])
        splits[6].append(2)

    return True if dealer_up_value in splits[player_value] else False


def player_decision(player_hand, split_hand, dealer_hand):
    if len(player_hand.cards) == 2:
        c1 = player_hand.cards[0]
        c2 = player_hand.cards[1]

        if player_hand.can_split(split_hand):
            if decision_split(
                max(c1.face.value, c2.face.value), dealer_hand.cards[1].value, False
            ):
                return "SPLIT"

        elif decision_double(player_hand, dealer_hand.cards[1].value):
            return "DOUBLE"

    return (
        "HIT"
        if decision_basic_hit(player_hand, dealer_hand.cards[1].value)
        else "STAND"
    )
