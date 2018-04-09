class MctsNode:
    def __init__(self, board, color):
        self.board = board
        self.color = color
        self.untriedMoves = board.get_legal_moves(color)
        self.childNodes = []
        self.parentNode = None

    def select_child(self):
        pass

    def add_child(self, move):
        pass

    def simulation(self):
        pass

    def update(self, result):
        pass
