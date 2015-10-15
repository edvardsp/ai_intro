
class Board(object):

    def __init__(self):
        pass

    def __repr__(self):
        return ""

class Switchboard(object):

    def __init__(self, M, N, D, W, start, end):
        self.M = M
        self.N = N
        self.D = D
        self.W = W
        self.start = start
        self.end = end

    def __repr__(self):
        return "Switchboard(M={}, N={}, D={}, W={}, start={}, end={})".format(
            self.M, self.N, self.D, self.W, self.start, self.end)

    def simulated_annealing(self):
        b = Board()

        print(board)