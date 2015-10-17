import colorama as cr
import math as m
import random as rand

UP    = "↑"
LEFT  = "←"
DOWN  = "↓"
RIGHT = "→"

MOVES = {UP, LEFT, DOWN, RIGHT}

OTHER = {UP:   {LEFT, DOWN, RIGHT}, LEFT:  {UP, DOWN, RIGHT},
         DOWN: {UP,   LEFT, RIGHT}, RIGHT: {UP, LEFT, DOWN}}
OPPOSITE = {UP: DOWN, LEFT: RIGHT, DOWN: UP, RIGHT: LEFT}

class Board(object):

    def __init__(self, M, N, D, W, start, end):
        self.M = M
        self.N = N
        self.MxN = M * N
        self.D = D
        self.W = W
        self.start = start
        self.end = end

        self.moves = {(x,y): rand.choice(tuple(MOVES)) for x in range(M) for y in range(N)}

    def setMoves(self, moves):
        self.moves = moves

    def __repr__(self):
        s = cr.Fore.BLUE + cr.Style.BRIGHT
        for y in range(self.N):
            for x in range(self.M):
                if (x,y) == self.start:
                    s += cr.Fore.GREEN + self.moves[(x,y)] + cr.Fore.BLUE

                elif (x,y) == self.end:
                    s += cr.Fore.GREEN + 'E' + cr.Fore.BLUE

                else:
                    s += self.moves[(x,y)]

                s += " "

            if y == self.N - 1:
                s += "\n"
            else:
                s += "\n\n"

        s += cr.Fore.RESET + cr.Style.NORMAL
        return s

    def moveCoord(self, coord, move):
        rule = {UP:   (0, -1), LEFT:  (-1, 0),
                DOWN: (0,  1), RIGHT: ( 1, 0)}
        return tuple(map(sum, zip(coord, rule[move])))

    def validCoord(self, coord):
        return 0 <= coord[0] < self.M and 0 <= coord[1] < self.N

    def manhattanDist(self, p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    def eval(self, moves=None, final=False):
        if moves is None:
            moves = self.moves

        # Optimistic optimal value
        OPT_VALUE = (self.MxN-1) * self.D + min(self.M, self.N) * self.W

        PENALIZE_OUTOFBOUNDS = 100
        PENALIZE_NOTVISITED = 80
        PENALIZE_NOFINISH = 60

        value = self.W
        visited = set()
        currCoord = self.start
        currDir = moves[currCoord]
        streak = 0

        # Break when hitting a peg we have already visited
        while currCoord not in visited and currCoord != self.end:
            # Add current peg to visited
            visited.add(currCoord)

            # Move currCord in current direction
            # and check for validness
            # If not valid, then out of bounds, break
            newCoord = self.moveCoord(currCoord, currDir)
            if not self.validCoord(newCoord):
                value += PENALIZE_OUTOFBOUNDS
                break

            # Check if a new winding is made
            # Reward long streaks
            streak += 1
            newDir = moves[newCoord]
            if newCoord != self.end and newDir != currDir:
                value += self.W 
                if not final:
                    value += (max(self.M, self.N) - streak) * 2
                    streak = 0

            # Update current state
            currCoord = newCoord
            currDir = newDir

        # Add wire length, excluding end peg
        value += len(visited) * self.D

        # Penalize if not hit end peg
        if currCoord != self.end:
            dist = self.manhattanDist(currCoord, self.end)
            value += PENALIZE_NOFINISH * dist
        # else add to visited set
        else:
            visited.add(self.end)

        # Penalize unvisited pegs
        numNotvisited = (self.MxN - len(visited))
        if final and numNotvisited != 0:
            return float('inf')
        value += numNotvisited * PENALIZE_NOTVISITED

        if final:
            return value
        else:
            return (OPT_VALUE - value) / OPT_VALUE

    def validSolution(self, moves=None):
        if moves is None:
            moves = self.moves

        upperLimit = (self.MxN-1) * (self.D + self.W)
        return self.eval(moves, True) < upperLimit

    def generate(self):
        out = []

        for y in range(self.N):
            for x in range(self.M):
                coord = (x,y)
                if coord == self.end:
                    continue

                possibleMoves = OTHER[self.moves[coord]]
                for newMove in possibleMoves:
                    if self.validCoord(self.moveCoord(coord, newMove)):
                        newOut = self.moves.copy()
                        newOut[coord] = newMove
                        out.append(newOut)

        return out


class Switchboard(object):

    def __init__(self, M, N, D, W, start, end):
        self.M = M
        self.N = N
        self.D = D
        self.W = W
        self.start = start
        self.end = end
        self.board = Board(M, N, D, W, start, end)

        self.Tmax = 30.0
        self.Tmin = 3e-2
        self.dT = 0.9995

        cr.init(autoreset=True)

    def __repr__(self):
        string = "Switchboard(M={}, N={}, D={}, W={}, start={}, end={})"
        return string.format(self.M, self.N, self.D, self.W, self.start, self.end)

    def accept(self, current, proposal, temp):
        if proposal < current:
            return True

        if temp == 0.0:
            return False

        prob = m.e ** (- (proposal - current) / temp)
        return rand.random() > prob

    def simulated_annealing(self):
        print(cr.ansi.clear_screen(), end="")

        iteration = 1

        # Initialize the algorithm
        T = self.Tmax

        P = self.board.moves
        FP = self.board.eval()
        Pmax = P
        FPmax = FP

        streak = 0
        exploiting = 0
        exploring = 0

        while T > self.Tmin and streak < 1000 :
            print(cr.Cursor.POS(), end="")
            print(self.board)
            neighbors = self.board.generate()

            PnMax  = None
            FPnMax = -float('inf')

            for neighbor in neighbors:
                FPn = self.board.eval(neighbor)
                if FPn > FPnMax:
                    FPnMax = FPn
                    PnMax = neighbor
                if FPn > FPmax:
                    FPmax = FPn
                    Pmax = neighbor
                    streak = 0

            if not self.accept(FP, FPnMax, T):
                exploring += 1
                P = rand.choice(neighbors)
            else:
                exploiting += 1
                P = PnMax
            self.board.setMoves(P)
            FP = self.board.eval()

            T *= self.dT

            print('         T = {0:.2f}   '.format(T))
            print('     FPmax = {0:.3f}    '.format(FPmax))
            print('    Streak = {}    '.format(streak))
            print(' Exploring = {0:.1f}  '.format(exploring * 100.0 / iteration))
            print('Exploiting = {0:.1f}  '.format(exploiting * 100.0 / iteration))
            print(' Iteration = {}'.format(iteration))

            iteration += 1
            if self.board.validSolution(Pmax):
                streak += 1

        print(cr.ansi.clear_screen() + cr.Cursor.POS(), end="")
        self.board.setMoves(Pmax)
        FPmax = self.board.eval(final=True)
        print("Finished in {} iterations".format(iteration))
        print(self.board)
        print(FPmax)

        return FPmax, Pmax