from engines import Engine
from MCTSCore import MctsCore
import multiprocessing


class MCTSEngine(Engine):
    def get_move(self, board, color, move_num=None, time_remaining=None, time_opponent=None):
        core = MctsCore.MctsCore(board, color)
        p = multiprocessing.Process(target=core.cal)
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
