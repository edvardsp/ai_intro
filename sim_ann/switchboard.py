import colorama as cr
import random as rand

import simann as sa

# Moves used
UP = "↑"
LEFT = "←"
DOWN = "↓"
RIGHT = "→"

# Set of possible moves
MOVES = {UP, LEFT, DOWN, RIGHT}

# Dict of trailing wire, used in representation
MOVE_CHAR = {UP:    '',
             LEFT:  cr.Cursor.BACK(2) + '-',
             DOWN:  '',
             RIGHT: '-'}

# Returns set of moves excluding given move
OTHER = {UP:   MOVES ^ UP,   LEFT:  MOVES ^ LEFT,
         DOWN: MOVES ^ DOWN, RIGHT: MOVES ^ RIGHT}


class Board(object):

    """
    Solution representation.
    Represented as a list of coordinates of the eggs.
    """

    def __init__(self, M, N, D, W, start, end):
        self.M = M
        self.N = N
        self.MxN = M * N
        self.D = D
        self.W = W
        self.start = start
        self.end = end

        self.possible = {(x, y) for x in range(M) for y in range(N)}
        self.moves = {coord: rand.choice(tuple(MOVES))
                      for coord in self.possible}

    def __repr__(self):
        s = (" " * (self.M*2+2) + "\n") * (self.N+2)
        s += cr.Fore.BLUE + cr.Style.BRIGHT

        coord = self.start
        visited = {coord}

        while coord != self.end:
            move = self.moves[coord]
            pos = (2*coord[0]+2, coord[1]+2)
            s += cr.Cursor.POS(*pos)

            if coord == self.start:
                s += cr.Fore.GREEN + move + cr.Fore.BLUE
            elif coord == self.start:
                s += cr.Fore.GREEN + 'E' + cr.Fore.BLUE
                break
            else:
                s += move
            s += MOVE_CHAR[move]

            coord = self.moveCoord(coord, move)
            if not self.validCoord(coord) or coord in visited:
                break
            visited.add(coord)

        pos = (2*self.end[0]+2, self.end[1]+2)
        s += cr.Cursor.POS(*pos) + cr.Fore.GREEN + 'E' + cr.Fore.BLUE
        s += cr.Fore.RESET + cr.Style.NORMAL
        s += cr.Cursor.POS(1, self.N+2)
        return s

    def getP(self):
        """
        Function used by the simann bibliography.
        Sets new current state.
        """
        return self.moves

    def setP(self, P):
        """
        Function used by the simann bibliography.
        Gets the current state.
        """
        self.moves = P

    def moveCoord(self, coord, move):
        """
        Move a given coordinate one unit with the given move
        """
        rule = {UP: (0, -1), LEFT: (-1, 0),
                DOWN: (0, 1), RIGHT: (1, 0)}
        return tuple(map(sum, zip(coord, rule[move])))

    def validCoord(self, coord):
        """
        Validate if the given coord is valid
        """
        return 0 <= coord[0] < self.M and 0 <= coord[1] < self.N

    def manhattanDist(self, p1, p2):
        """
        Return the manhattan distance between two coordinates
        """
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    def objective(self, moves=None, final=False):
        """
        Function used by the simann bibliography.
        Returns the objective value of the given board.
        If no board is given, return the objective value of the
        current board.
        Final gives the final score of the solution when
        simann algorithm has finished.
        """
        if moves is None:
            moves = self.moves

        # Optimistic optimal value
        OPT_VALUE = (self.MxN-1) * self.D + max(self.M, self.N) * self.W

        # Different penalize costs
        PENALIZE_OUTOFBOUNDS = 100
        PENALIZE_NOTVISITED = 100
        PENALIZE_NOFINISH = 100
        PENALIZE_CROSSING = 60

        # Initialize
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

        # Penalize crossing wires
        if currCoord in visited:
            value += PENALIZE_CROSSING

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
        notVisited = self.possible ^ visited
        if final and len(notVisited) != 0:
            return float('inf')
        for coord in notVisited:
            if coord in [(x, y) for x in [0, self.M-1] for y in [0, self.N-1]]:
                value += PENALIZE_NOTVISITED * 10
            else:
                value += PENALIZE_NOTVISITED

        if final:
            return value
        else:
            return (OPT_VALUE - value) / OPT_VALUE

    def validSolution(self, moves=None):
        """
        Function used by the simann bibliography.
        Checks if the given solution is a valid one.
        """
        if moves is None:
            moves = self.moves

        upperLimit = (self.MxN-1) * (self.D + self.W)
        return self.objective(moves, True) < upperLimit

    def generate(self):
        """
        Function used by the simann bibliography.
        Generates a neighborhood of states of the current
        state on the board.
        """
        out = []

        for y in range(self.N):
            for x in range(self.M):
                coord = (x, y)
                if coord == self.end:
                    continue

                possibleMoves = OTHER[self.moves[coord]]
                for newMove in possibleMoves:
                    if self.validCoord(self.moveCoord(coord, newMove)):
                        newOut = self.moves.copy()
                        newOut[coord] = newMove
                        out.append(newOut)

        return out


class Switchboard(sa.SimulatedAnnealing):

    """
    Switchboard puzzle container
    """

    def __init__(self, M, N, D, W, start, end):
        super(Switchboard, self).__init__()

        self.M = M
        self.N = N
        self.D = D
        self.W = W
        self.start = start
        self.end = end
        self.environment = Board(M, N, D, W, start, end)

        self.Tmax = 20.0
        self.Tmin = 2e-2
        self.streakLimit = 1000

        self.name = self.__repr__()

    def __repr__(self):
        string = "Switchboard(M={}, N={}, D={}, W={}, start={}, end={})"
        return string.format(self.M, self.N, self.D,
                             self.W, self.start, self.end)

    def schedule(self, temp):
        """
        Function used by the simann bibliography.
        Gives the new temperature when given one.
        """
        if temp > 10.0:
            return temp - 3e-2
        elif temp > 1.0:
            return temp - 1e-3
        else:
            return temp - 5e-4
