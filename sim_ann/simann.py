import colorama as cr
import random as rand
import math as m

"""
Simaluted Annealing base class. Implements the algorithm.
""" 
class SimulatedAnnealing(object):

    def __init__(self):
        self.name = "SimulatedAnnealing Base Class"
        self.environment = None

        self.Tmax = 100
        self.Tmin = 1e-2
        self.streakLimit = 1000

    """
    Accept algorithm. Standard.
    """
    def accept(self, current, proposal, temp):
        if proposal < current:
            return True

        if temp == 0.0:
            return False

        prob = m.e ** (- (proposal - current) / temp)
        return rand.random() > prob

    """
    Base function of the algorithm. 
    Must be implemented by the inherited container class.
    """
    def schedule(self, temp):
        raise NotImplemented()

    """
    Print stats of the algorithm
    """
    def printStats(self, stats):
        string  = "\n   " + self.name + "\n\n"
        string += "          T = {0:.2f}\n"
        string += "      FPmax = {1:.3f}\n"
        string += "     Streak = {2}    \n"
        string += "  Exploring = {3}    \n"
        string += " Exploiting = {4}    \n"
        string += "  Iteration = {5}    \n"
        print(string.format(*stats))

    """
    Actual algorithm    
    """
    def run(self):
        # Clear the screen
        print(cr.ansi.clear_screen(), end="")

        # Initialize the algorithm
        T = self.Tmax
        P = self.environment.getP()
        FP = self.environment.objective()
        Pmax = P
        FPmax = FP

        # Search states
        streak = 0
        exploiting = 0
        exploring = 0
        iteration = 1

        # While T is acceptable and a valid solution 
        # found streak hasn't been broken
        while T > self.Tmin and streak < self.streakLimit:
            print(cr.Cursor.POS(), end="")

            # Generate neighborhood
            neighbors = self.environment.generate()

            # Reset local max
            PnMax  = None
            FPnMax = -float('inf')

            # Check each neighbor
            for neighbor in neighbors:
                FPn = self.environment.objective(neighbor)
                if FPn > FPnMax:
                    FPnMax = FPn
                    PnMax = neighbor
                if FPn > FPmax:
                    FPmax = FPn
                    Pmax = neighbor
                    streak = 0

            # If accept, choose best neighbor 
            if self.accept(FP, FPnMax, T):
                exploiting += 1
                P = PnMax
            # else choose random neighbor
            else:
                exploring += 1
                P = rand.choice(neighbors)

            # Evaluate next search state
            self.environment.setP(P)
            FP = self.environment.objective()

            # Schedule next temperature
            T = self.schedule(T)

            # Print stats
            self.printStats((T, FPmax, streak, exploring, exploiting, iteration))

            # Update iteration
            iteration += 1

            # If a valid solution is found, update streak
            if self.environment.validSolution(Pmax):
                streak += 1

        # Done with search
        # Clean the screen
        print(cr.ansi.clear_screen() + cr.Cursor.POS(), end="")
        # Set the best state we found in our search
        self.environment.setP(Pmax)
        # Calculate final score
        FPmax = self.environment.objective(final=True)
        # Print stats and best environment
        print("Finished in {} iterations".format(iteration))
        print(self.environment)
        print("Score:", FPmax)

        # Return score and state
        return FPmax, Pmax