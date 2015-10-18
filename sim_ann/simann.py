import colorama as cr
import random as rand
import math as m


class SimulatedAnnealing(object):

    def __init__(self):
        self.Tmax = 100
        self.environment = None

    def accept(self, current, proposal, temp):
        if proposal < current:
            return True

        if temp == 0.0:
            return False

        prob = m.e ** (- (proposal - current) / temp)
        return rand.random() > prob

    def schedule(self, temp):
        raise NotImplemented()

    def printStats(self, *stats):
        raise NotImplemented()

    def run(self):
        print(cr.ansi.clear_screen(), end="")

        iteration = 1

        # Initialize the algorithm
        T = self.Tmax

        P = self.environment.moves
        FP = self.environment.eval()
        Pmax = P
        FPmax = FP

        streak = 0
        exploiting = 0
        exploring = 0

        while T > self.Tmin and streak < 1000 :
            print(cr.Cursor.POS(), end="")

            # Generate neighborhood
            neighbors = self.environment.generate()

            PnMax  = None
            FPnMax = -float('inf')

            # Check each neighbor
            for neighbor in neighbors:
                FPn = self.environment.eval(neighbor)
                if FPn > FPnMax:
                    FPnMax = FPn
                    PnMax = neighbor
                if FPn > FPmax:
                    FPmax = FPn
                    Pmax = neighbor
                    streak = 0

            # Accept best neighbor or random
            if not self.accept(FP, FPnMax, T):
                exploring += 1
                P = rand.choice(neighbors)
            else:
                exploiting += 1
                P = PnMax
            self.environment.setMoves(P)
            FP = self.environment.eval()

            # Schedule next temperature
            T = self.schedule(T)

            self.printStats((T, FPmax, streak, exploring, exploiting, iteration))

            iteration += 1
            if self.environment.validSolution(Pmax):
                streak += 1

        print(cr.ansi.clear_screen() + cr.Cursor.POS(), end="")
        self.environment.setMoves(Pmax)
        FPmax = self.environment.eval(final=True)
        print("Finished in {} iterations".format(iteration))
        print(self.environment)
        print("Score:", FPmax)

        return FPmax, Pmax