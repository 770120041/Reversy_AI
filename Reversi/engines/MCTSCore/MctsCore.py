import random
import time


class MctsCore(object):
    def __init__(self, board, color):
        self.board = board
        self.color = color
        self.count = 0
        pass

    def cal(self):
        while self.count < 4:
            time.sleep(1)
            self.count += 1

    def current_best_move(self):
        print self.count
        return random.choice(self.board.get_legal_moves(self.color))
