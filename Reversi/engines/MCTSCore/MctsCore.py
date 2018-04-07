import random
import copy
import MctsNode


class MctsCore(object):
    def __init__(self, board, color, move_num, fixed_potential):
        self.board = board
        self.color = color
        self.move_num = move_num
        self.fixed_potential = fixed_potential
        self.moves = self.board.get_legal_moves(self.color)
        pass

    def run(self):
        if self.pre_judge():
            self.cal()

    def pre_judge(self):
        if self.fixed_potential.match(self.board, self.color):
            self.moves = self.fixed_potential.getSolution()
            return False
        else:
            return True

    def cal(self):
        rootnode = MctsNode.MctsNode(self.board, self.color)
        while True:
            node = rootnode
            # Select
            while node.untriedMoves == [] and node.childNodes != []:  # node is fully expanded and non-terminal
                node = node.selectChild()
            # Expand
            if node.untriedMoves:  # if we can expand (i.e. state/node is non-terminal)
                move = random.choice(node.untriedMoves)
                node = node.AddChild(move)  # add child and descend tree
            # Simulation
            result = node.simulation()
            # Backpropagate
            while node is not None:  # backpropagate from the expanded node and work back to the root node
                node.update(result)
                node = node.parentNode

    def current_best_move(self):
        return random.choice(self.moves)
