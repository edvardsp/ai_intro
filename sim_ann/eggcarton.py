import random as rand
import math as m

import simann as sa

class Board(object):

    def __init__(self, M, N, K, eggs):
        self.M = M
        self.N = N
        self.K = K
        self.eggs = eggs

        self.board = [(x,y) for y in range(N) for x in range(M)
            if y * M + x < eggs]

    def __repr__(self):
        string = ""
        for y in range(self.N):
            for x in range(self.M):
                if (x,y) in self.board:
                    string += 'X '
                else:
                    string += '. '
            string += '\n'
        return string

    def getP(self):
        return self.board

    def setP(self, board):
        self.board = board

    def eval(self, board=None, final=False):
        if board is None:
            board = self.board

        STRAIGT_PENALTY = 0.9
        DIAG_PENALTY    = 0.1

        # Horizontal
        xs = {k: 0 for k in range(self.M)}
        # Vertical
        ys = {k: 0 for k in range(self.N)}
        # Diagonal
        ds1 = {k: 0 for k in range(self.M+self.N-1)}
        ds2 = {k: 0 for k in range(self.M+self.N-1)}
        
        # Compute each point
        for p in board:
            xs[p[0]] += 1
            ys[p[1]] += 1
            ds1[p[0]+p[1]] += 1
            ds2[(self.M+self.N-1)//2+p[0]-p[1]] += 1 

        # Calculate objective function value and return
        F = lambda ss: sum(max(v-self.K,0) for v in ss.values())
        cumsum =  sum(map(F, [xs, ys]))   * STRAIGT_PENALTY
        cumsum += sum(map(F, [ds1, ds2])) * DIAG_PENALTY

        if final:
            return cumsum
        else:
            return -cumsum

    def validSolution(self, board=None):
        score = self.eval()
        return score == 0

    def generate(self):
        newBoards = []

        # For each point
        for p in self.board:
            # Generate all neighboring points
            for newy in range(self.N):
                if newy == p[1]:
                    continue
                newp = (p[0], newy)
                if newp not in self.board:
                    newboard = self.board[:]
                    newboard[newboard.index(p)] = newp
                    newBoards.append(newboard)

        return newBoards


class EggCarton(sa.SimulatedAnnealing):
    
    def __init__(self, M, N, K):
        super(EggCarton, self).__init__()

        self.M = M
        self.N = N
        self.K = K

        maxEggs = max(M, N) * K
        self.environment = Board(M, N, K, maxEggs)

        self.Tmax = 1.0
        self.Tmin = 1e-2
        self.dT = 1e-5
        self.streakLimit = 1

        self.name = self.__repr__()

    def __repr__(self):
        return "EggCarton({}, {}, {})".format(self.M, self.N, self.K)

    def schedule(self, temp):
        return temp - self.dT