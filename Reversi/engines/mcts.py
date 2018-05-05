from __future__ import absolute_import
from engines import Engine
from copy import deepcopy
import random
import timeit
import math


class MCTSNode:
    EXPLORATION = 0
    EXPLOITATION = 1

    MAX_GENERATION = 4

    def __init__(self, board, turn, father, generation, index, cause_move):
        self.board = board
        self.turn = turn
        self.father = father
        self.generation = generation
        self.id = index
        self.cause_move = cause_move
        self.all_moves = self.board.get_legal_moves(self.turn)
        self.all_moves_num = len(self.all_moves)
        self.child_nodes = [None] * self.all_moves_num
        self.child_num = 0
        self.stats = {-1: 0, 1: 0}

    def is_leaf(self):
        return (self.child_num is 0) or (self.generation is MCTSNode.MAX_GENERATION-1)

    def has_tried_all(self):
        return self.child_num is self.all_moves_num and self.all_moves_num is not 0

    def find_child_node_by_board(self, board):
        for child_node in self.child_nodes:
            flag = True
            for x in range(8):
                for y in range(8):
                    if child_node.board[x][y] is not board[x][y]:
                        flag = False
                        break
                if not flag:
                    break
            if flag:
                return child_node
        return None

    def get_best_child_index(self, mode):
        constant = 1 / math.sqrt(2.0)
        best_child_index = -1
        max_score = -1
        for index in range(self.child_num):
            child_node = self.child_nodes[index]
            score = 1 - child_node.get_quality_value() * 1.0 / child_node.get_visit_times()
            if mode is MCTSNode.EXPLORATION:
                right = 2.0 * math.log(self.get_visit_times()) / child_node.get_visit_times()
                score = score + constant * math.sqrt(right)
            if score > max_score:
                best_child_index = index
                max_score = score
        return best_child_index

    def select_best_child(self, mode):
        best_child_index = self.get_best_child_index(mode)
        if best_child_index is -1:
            return None
        else:
            return self.child_nodes[best_child_index]

    def add_child(self):
        if self.child_num is self.all_moves_num:
            if self.child_num is 0:
                return self
            else:
                return self.select_best_child(MCTSNode.EXPLORATION)
        new_board = deepcopy(self.board)
        new_move = self.all_moves[self.child_num]
        new_board.execute_move(new_move, self.turn)
        new_node = MCTSNode(new_board, -self.turn, self, self.generation + 1, self.id + '.' + str(self.child_num), new_move)
        self.child_nodes[self.child_num] = new_node
        self.child_num += 1
        return new_node

    def simulation(self):
        result = {-1: 0, 1: 0}
        simulation_times = 1
        for time in range(simulation_times):
            board = deepcopy(self.board)
            is_end = False
            while not is_end:
                is_end = True
                for turn in [self.turn, -self.turn]:
                    move = self.get_quick_move(board, turn)
                    if move is not None:
                        board.execute_move(move, turn)
                        is_end = False
            chess_num = {-1: 0, 0: 0, 1: 0}
            for y in range(8):
                for x in range(8):
                    chess_num[board[x][y]] += 1
            if chess_num[-1] >= chess_num[1]:
                result[-1] += 1
            if chess_num[-1] <= chess_num[1]:
                result[1] += 1
        self.refresh(result)
        return result

    def get_father(self):
        return self.father

    def refresh(self, result):
        self.stats[-1] += result[-1]
        self.stats[1] += result[1]

    def get_visit_times(self):
        return self.stats[-1] + self.stats[1]

    def get_quality_value(self):
        return self.stats[self.turn]

    def get_quick_move(self, board, turn):
        moves = board.get_legal_moves(turn)
        if moves:
            return random.choice(moves)
        else:
            return None
        # moves = board.get_legal_moves(turn)
        # if moves:
        #     return max(moves, key=lambda move: self.get_quick_cost(board, turn, move))
        # else:
        #     return None

    @staticmethod
    def get_quick_cost(board, turn, move):
        new_board = deepcopy(board)
        new_board.execute_move(move, turn)

        # Count the # of pieces of each color on the board
        num_pieces_op = len(new_board.get_squares(turn * -1))
        num_pieces_me = len(new_board.get_squares(turn))

        # Return the difference in number of pieces
        return num_pieces_me - num_pieces_op

    def print_node(self):
        print('address(' + str(hex(id(self))) + ') ' +
              'id(' + self.id + ') ' +
              'move(' + chr(self.cause_move[0]+65) + str(self.cause_move[1] + 1) + ') '
              'stats(' + str(self.stats[-1]) + ',' + str(self.stats[1]) + ') ')


class MCTSCore:
    def __init__(self):
        self.board = None
        self.color = None
        self.time_remained = None
        self.start_time = None
        self.root = None
        self.move = None

    def run(self, board, color, time, timer):
        self.board = board
        self.color = color
        self.time_remained = time
        self.start_time = timer

        self.root = self.get_root()
        while round(timeit.default_timer() - self.start_time, 2) < self.time_remained:
            node = self.root
            try:
                # selection
                while not node.is_leaf() and node.has_tried_all():
                    node = node.select_best_child(MCTSNode.EXPLORATION)
                # expansion
                node = node.add_child()
                # simulation
                result = node.simulation()
                # back propagation
                while node is not self.root:
                    node = node.get_father()
                    node.refresh(result)
            except AttributeError:
                print('There is a Error: begin')
                self.print_tree()
                print('There is a Error: end')

    def current_best_move(self):
        best_child_index = self.root.get_best_child_index(MCTSNode.EXPLOITATION)
        if best_child_index is -1:
            self.root = None
            return None
        else:
            selected_move = self.root.all_moves[best_child_index]
            self.root = self.root.child_nodes[best_child_index]
            return selected_move

    def print_tree(self):
        queue = [self.root]
        while queue:
            if queue[0] is not None:
                queue[0].print_node()
                for node in queue[0].child_nodes:
                    queue.append(node)
            queue.pop(0)

    def get_root(self):
        if self.root is None:
            return MCTSNode(deepcopy(self.board), self.color, None, 0, '0', [0, 0])
        else:
            branch_node = self.root.find_child_node_by_board(self.board)
            if branch_node is None:
                return MCTSNode(deepcopy(self.board), self.color, None, 0, '0', [0, 0])
            else:
                return branch_node


class MCTSEngine(Engine):
    def __init__(self):
        self.core = MCTSCore()

    def get_move(self, board, color, move_num=None, time_remaining=None, time_opponent=None):
        timer = timeit.default_timer()
        self.core.run(board, color, self.cal_time(move_num, time_remaining), timer)
        self.core.print_tree()
        return self.core.current_best_move()

    @staticmethod
    def cal_time(move_num, time_remaining):
        # return 5
        if move_num is 0:
            return 0.1
        else:
            return time_remaining / (30 - move_num) - 1


engine = MCTSEngine
