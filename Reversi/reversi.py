from __future__ import print_function

import argparse
import copy
import random
import signal
import sys
import timeit
import traceback

from board import Board, move_string

player = {-1: "Black", 1: "White"}


def game(black_engine, white_engine, game_time=30.0, verbose=False):
    """ Run a single game. Raise RuntimeError in the event of time expiration.
    Raise LookupError in the case of a bad move. The tournament engine must
    handle these exceptions. """

    # Initialize variables
    board = Board()
    total_time = {-1: game_time * 60, 1: game_time * 60}  # in seconds
    engine = {-1: black_engine, 1: white_engine}

    if verbose:
        print("INITIAL BOARD\n\n--\n")
        board.display(total_time)

    # Do rounds
    for move_num in range(60):
        moves = []
        for color in [-1, 1]:
            start_time = timeit.default_timer()
            move = get_move(board, engine[color], color, move_num, total_time)
            end_time = timeit.default_timer()
            # Update user total_time
            time = round(end_time - start_time, 1)
            total_time[color] -= time

            if total_time[color] < 0:
                raise RuntimeError(color)

            # Make a move, otherwise pass
            if move is not None:
                board.execute_move(move, color)
                moves.append(move)

                if verbose:
                    print(("--\n\nRound {}: {} plays in {}\n"
                           ).format(str(move_num + 1), player[color], move_string(move)))
                    board.display(total_time)

        if not moves:
            break  # No more legal moves. Game is over.

    print("\n--------------------\nFINAL BOARD\n--\n")
    board.display(total_time)

    board.total_time = total_time
    return board


def get_move(board, engine, color, move_num, time, **kwargs):
    """ Get the move for the given engine and color. Check validity of the
    move. """
    legal_moves = board.get_legal_moves(color)

    if not legal_moves:
        return None
    elif len(legal_moves) == 1:
        return legal_moves[0]
    else:
        try:
            move = engine.get_move(copy.deepcopy(board), color, move_num, time[color], time[-color])
        except Exception, e:
            print(traceback.format_exc())
            raise SystemError(color)

        if move not in legal_moves:
            print("legal list", [move_string(m) for m in legal_moves])
            print("illegal", move_string(move), "=", move)
            raise LookupError(color)

        return move


def winner(board):
    """ Determine the winner of a given board. Return the points of the two
    players. """
    black_count = board.count(-1)
    white_count = board.count(1)
    if black_count > white_count:
        return -1, black_count, white_count
    elif white_count > black_count:
        return 1, black_count, white_count
    else:
        return 0, black_count, white_count


def signal_handler(signal, frame):
    """ Capture SIGINT command. """
    print('\n\n- You quit the game!')
    sys.exit()


def main(engines, user_names, scores, game_time, verbose):
    try:

        print("\n====================\nNEW GAME\nBlack: {}\nWhite: {}".format(user_names[0], user_names[1]))
        board = game(engines[0], engines[1], game_time, verbose)
        stats = winner(board)
        if stats[0] == -1:  # black wins
            scores[0] += stats[1]
            print("- {} ({}) wins the game! (Current score: {})".format(user_names[0], player[-1], scores[0]))
        elif stats[0] == 1:  # white wins
            scores[1] += stats[2]
            print("- {} ({}) wins the game! (Current score: {})".format(user_names[1], player[1], scores[1]))
        else:
            print("- Tied!")

    except RuntimeError, e:
        err_usr_id = int((e[0] + 1) / 2)  # 0 or 1
        other_id = int((1 - e[0]) / 2)  # 1 or 0
        scores[other_id] += 64
        print("\n- {} ({}) ran out of time!\n".format(user_names[err_usr_id], player[e[0]]))
        print("{} ({}) wins the game! (Current score: {})".format(user_names[other_id], player[e[0] * -1],
                                                                  scores[other_id]))
    except LookupError, e:
        err_usr_id = int((e[0] + 1) / 2)  # 0 or 1
        other_id = int((1 - e[0]) / 2)  # 1 or 0
        scores[other_id] += 64
        print("\n- {} ({}) made an illegal move!\n".format(user_names[err_usr_id], player[e[0]]))
        print("{} ({}) wins the game! (Current score: {})".format(user_names[other_id], player[e[0] * -1],
                                                                  scores[other_id]))
    except SystemError, e:
        err_usr_id = int((e[0] + 1) / 2)  # 0 or 1
        other_id = int((1 - e[0]) / 2)  # 1 or 0
        scores[other_id] += 64
        print("\n- {} ({}) ended prematurely because of an error!\n".format(user_names[err_usr_id], player[e[0]]))
        print("{} ({}) wins the game! (Current score: {})".format(user_names[other_id], player[e[0] * -1],
                                                                  scores[other_id]))
    finally:
        return scores


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    # Automatically generate help and usage messages.
    # Issue errors when users gives the program invalid arguments.
    parser = argparse.ArgumentParser(description="Play the Reversi/Othello game using different engines.")
    parser.add_argument("-a", "--engine_a", action="store", type=str, default="greedy",
                        help="first engine (human, eona, greedy, nonull, random)")
    parser.add_argument("-b", "--engine_b", action="store", type=str, default="random",
                        help="second engine (human, eona, greedy, nonull, random)")
    parser.add_argument("-t", "--time", action="store", type=int, default=30, help="time limit (in minutes)")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="display the board at each turn")
    args = parser.parse_args()

    ename1 = args.engine_a  # engine name 1
    ename2 = args.engine_b  # engine name 2
    enames = [ename1, ename2]
    print("{} vs. {}".format(ename1, ename2))

    try:
        engines_1 = __import__('engines.' + ename1)
        engines_2 = __import__('engines.' + ename2)
        engine1 = engines_1.__dict__[ename1].__dict__['engine']()
        engine2 = engines_2.__dict__[ename2].__dict__['engine']()
        engines = [engine1, engine2]

        v = (args.verbose or ename1 == "human" or ename2 == "human")

        # Game begin
        ss = [0] * 2  # scores
        n = 0
        while n < 3 or ss[0] == ss[1]:
            i, j = random.sample([0, 1], 2)
            ss[i], ss[j] = main([engines[i], engines[j]], [enames[i], enames[j]], [ss[i], ss[j]], game_time=args.time,
                                verbose=v)
            n += 1

        print('\n========== FINAL REPORT ==========\n{} - {}: {} - {}'.format(enames[0], enames[1], ss[0], ss[1]))
        if ss[0] > ss[1]:
            print('The winner is', enames[0], '!')
        else:
            print('The winner is', enames[1], '!')

    except ImportError, e:
        print('Unknown engine -- {}'.format(e[0].split()[-1]))
        sys.exit()
