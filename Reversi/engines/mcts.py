from engines import Engine
from MCTSCore import *
import multiprocessing


class MCTSEngine(Engine):
    def __init__(self):
        self.fixed_potential = MctsPotentials.MctsPotentials()

    def get_move(self, board, color, move_num=None, time_remaining=None, time_opponent=None):
        core = MctsCore.MctsCore(board, color, move_num, self.fixed_potential)
        p = multiprocessing.Process(target=core.run)
        p.start()
        p.join(self.cal_time(move_num, time_remaining))
        if p.is_alive():
            p.terminate()
            p.join()
        return core.current_best_move()

    @staticmethod
    def cal_time(move_num, time_remaining):
        return time_remaining / (30 - move_num)


engine = MCTSEngine
