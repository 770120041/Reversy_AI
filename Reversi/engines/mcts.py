from engines import Engine
import Queue
import multiprocessing
from time import ctime, sleep
from MCTSCore import mcts_core


class MCTSEngine(Engine):
    def get_move(self, board, color, move_num=None, time_remaining=None, time_opponent=None):
        bob = 21  # Whatever sensible value you need
        queue = multiprocessing.Queue(1)  # Maximum size is 1
        proc = multiprocessing.Process(target=self.wrapper, args=(queue, bob))
        proc.start()

        # Wait for TIMEOUT seconds
        try:
            result = queue.get(True, self.cal_time(self, move_num, time_remaining))
        except Queue.Empty:
            # Deal with lack of data somehow
            result = None
        finally:
            proc.terminate()

        # Process data here, not in try block above, otherwise your process keeps running
        print result

    @staticmethod
    def cal_time(self, move_num, time_remaining):
        return time_remaining / (60 - move_num)


engine = MCTSEngine
