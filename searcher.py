import copy
import time
from functools import reduce
import random

# all pawns, all kings, safe pawns, attack pawns, central kings, triangle, dog, king corner
opening = [3, 0, 1.5, 2, 0, 1, 1, 1]
kings = [3, 7, 2, 3, 3, 2, 2, 2]
ending = [4, 8, 2, 3, 2, 2, 2, 2]
safe_positions = [1, 2, 3, 4, 5, 13, 21, 29, 30, 31, 32, 28, 20, 12]
attack_positions = [14, 22, 18, 10, 15, 23, 19, 11]


def get_checkers(state, player):
    return reduce(lambda all, p: all + (([p] if p.player == player else [])),
                  list(filter(lambda p: p.captured == False, state.board.pieces)), [])


def get_kings(state, player):
    return reduce(lambda all, p: all + (([p] if p.player == player and p.king else [])),
                  list(filter(lambda p: p.captured == False, state.board.pieces)), [])


def heuristic(state):
    player1 = get_checkers(state, 1)
    player2 = get_checkers(state, 2)
    player1_kings = get_kings(state, 1)
    player2_kings = get_kings(state, 2)

    if (len(player1) - len(player1_kings) >= 3 and len(player2) - len(player1_kings) >= 3 and len(
            player1_kings) == 0 and len(player2_kings) == 0):
        coef = opening
    elif len(player1) >= 3 and len(player2) >= 3 and len(player1_kings) >= 1 and len(player2_kings) >= 2:
        coef = kings
    else:
        coef = ending
    evaluation = count_val(coef, player1, player2)
    return evaluation


def count_val(coef, red, black):
    evaluation = 0
    tr_red = list(filter(lambda ch: ch.position == 1 or ch.position == 6 or ch.position == 2, red))
    tr_black = list(filter(lambda ch: ch.position == 31 or ch.position == 37 or ch.position == 32, black))
    dog_red_counter = 0
    dog_black_counter = 0
    if len(tr_red) == 3:
        evaluation += coef[5]
    if len(tr_black) == 3:
        evaluation -= coef[5]

    for p in red:
        if p.king:
            evaluation += coef[1]
            if (p.position not in safe_positions):
                evaluation += coef[4]
            if p.position == 1:
                dog_red_counter += 1
            if p.position == 28:
                dog_black_counter += 1
            if p.position == 29:
                evaluation += coef[7]
        if not p.king:
            evaluation += coef[0]
            if (p.position in safe_positions):
                evaluation += coef[2]
            if p.position in attack_positions:
                evaluation += coef[3]
            if p.position == 1:
                dog_red_counter += 1
            if p.position == 28:
                dog_black_counter += 1
    for p in black:
        if p.king:
            evaluation -= coef[1]
            if (p.position not in safe_positions):
                evaluation -= coef[4]
            if p.position == 5:
                dog_red_counter -= 1
            if p.position == 32:
                dog_black_counter -= 1
            if p.position == 4:
                evaluation -= coef[7]
        if not p.king:
            evaluation -= coef[0]
            if (p.position in safe_positions):
                evaluation -= coef[2]
            if p.position in attack_positions:
                evaluation -= coef[3]
            if p.position == 5:
                dog_red_counter -= 1
            if p.position == 32:
                dog_black_counter -= 1
    if dog_red_counter == 2:
        evaluation += coef[6]
    if dog_black_counter == 2:
        evaluation -= coef[6]
    return evaluation


def find_move(state, time_left):
    start = time.time()
    player = state.whose_turn()
    moves = state.get_possible_moves()
    l = len(moves)
    if l == 1:
        return moves[0]
    if player == 1:
        heuristic = -1000000
    if player == 2:
        heuristic = 1000000
    move = random.choice(moves)
    alpha = -1000000
    beta = 1000000
    moves_left = 0
    for m in moves:
        state_copy = copy.deepcopy(state)
        state_copy.move(m)
        if time.time() - start >= time_left:
            return move
        time_left = time_left - (time.time() - start)
        val = minimax_search(state_copy, time_left / (l - moves_left), alpha, beta)
        moves_left += 1
        if player == 1:
            if val > heuristic:
                move = m
                heuristic = val
        if player == 2:
            if val < heuristic:
                move = m
                heuristic = val
    return move


def minimax_search(state, time_left, alpha, beta):
    start = time.time()
    player = state.whose_turn()
    moves = state.get_possible_moves()
    l = len(moves)
    cop = copy.deepcopy(state)
    if l == 0:
        return -999999
    cop.move(random.choice(moves))
    more = (cop.whose_turn() == state.whose_turn())
    if more:
        h = (-1) ** player * 1000000
    else:
        h = (-1) ** (player + 1) * 1000000
    moves_left = l
    for m in moves:
        state_copy = copy.deepcopy(state)
        state_copy.move(m)
        if time.time() - start >= time_left:
            return heuristic(state_copy)
        time_left = time_left - (time.time() - start)
        val = minimax_search(state_copy, time_left / moves_left, alpha, beta)
        moves_left -= 1
        if not more:
            if player == 1:
                if h > val:
                    h = val
            if player == 2:
                if h < val:
                    h = val
        if more:
            if player == 1:
                if h < val:
                    h = val
            if player == 2:
                if h > val:
                    h = val
        if player == 1:
            alpha = max(alpha, h)
        else:
            beta = min(beta, h)
        if beta < alpha:
            break
    return h
