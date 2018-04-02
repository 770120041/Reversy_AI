from engines import Engine


class MCTSEngine(Engine):
    def get_move(self, board, color, move_num=None, time_remaining=None, time_opponent=None):
        moves = board.get_legal_moves(color)


engine = MCTSEngine
