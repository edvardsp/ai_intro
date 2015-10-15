import random as rand
import math as m
from pprint import pprint

class Point(object):

	def __init__(self, x, y):
		self.x = x
		self.y = y

	def __eq__(self, other):
		return self.x == other.x and self.y == other.y

	def __repr__(self):
		return "<{},{}>".format(self.x, self.y)

class SimAnnBase(object):

	def __init__(self):
		pass

class EggCarton(SimAnnBase):
	
	def __init__(self, M, N, K):
		self.M = M
		self.N = N
		self.K = K
		self.Tmax = 1.0
		self.dT = 1e-5
		self.Ftarget = 0

	def __repr__(self):
		return "EggCarton({}, {}, {})".format(self.M, self.N, self.K)

	def initBoard(self, n):
		if n > self.M * self.N:
			raise ValueError("Too many eggs")

		left = n
		board = []
		for y in range(int(m.ceil(n / self.N))):
			for x in range(min(left, self.M)):
				p = Point(x, y)
				board.append(p)
			left = max(left - self.M, 0)

		

		return board

	def evalBoard(self, board):
		# Horizontal
		xs = {k: 0 for k in range(self.M)}
		# Vertical
		ys = {k: 0 for k in range(self.N)}
		# Diagonal
		ds1 = {k: 0 for k in range(self.M+self.N-1)}
		ds2 = {k: 0 for k in range(self.M+self.N-1)}
		
		# Compute each point
		for p in board:
			xs[p.x] += 1
			ys[p.y] += 1
			ds1[p.x+p.y] += 1
			ds2[(self.M+self.N-1)//2+p.x-p.y] += 1 

		# Calculate objective function value and return
		F = lambda ss: sum(max(v-self.K,0) for v in ss.values())
		straigt_penalty = 0.9
		diag_penalty    = 0.1

		cumsum =  sum(map(F, [xs, ys]))   * straigt_penalty
		cumsum += sum(map(F, [ds1, ds2])) * diag_penalty

		return self.Ftarget - cumsum

	def genNeighbors(self, board):
		newBoards = []
		# For each point
		for p in board:
			# Generate all neighboring points
			for newy in range(self.N):
				if newy == p.y:
					continue

				newp = Point(p.x, newy)
				if newp not in board:
					newboard = board[:]
					newboard[newboard.index(p)] = newp
					newBoards.append(newboard)

		return newBoards

	def printBoard(self, board):
		for y in range(self.N):
			for x in range(self.M):
				if Point(x,y) in board:
					print('X ', end='')
				else:
					print('. ', end='')
			print()

	def simulated_annealing(self, numEggs):
		# Create initial board
		P = self.initBoard(numEggs)
		T = self.Tmax

		iteration = 0
		FP = self.evalBoard(P)

		while FP != self.Ftarget and T > self.dT:
			neighbors = self.genNeighbors(P)
			Pmax = None
			FPmax = -float('inf')

			for neighbor in neighbors:
				FPn = self.evalBoard(neighbor)
				if FPn > FPmax:
					FPmax = FPn
					Pmax = neighbor

			q = max(0, float(FPmax - FP))
			p = min(1.0, m.e**(-q / T))
			x = rand.random()

			if x > p:
				P = Pmax
			else:
				P = rand.choice(neighbors)
			FP = self.evalBoard(P)

			T -= self.dT

			iteration += 1

		print("Finished in {} iterations".format(iteration))

		return FP, P


def main():
	rand.seed()

	# The Egg Carton Puzzle
	puzzles = [EggCarton(5, 5, 2), EggCarton(6, 6, 2),
			   EggCarton(8, 8, 1), EggCarton(10, 10, 3)]

	for puzzle in puzzles:
		print("New puzzle {}!".format(puzzle))

		numEggs = puzzle.M * puzzle.K 
		P = None
		while numEggs == puzzle.M * puzzle.K:
			print("Testing for {} eggs".format(numEggs))

			lastP = P
			FP, P = puzzle.simulated_annealing(numEggs)
			if FP != puzzle.Ftarget:
				print("Max eggs is {}\n".format(numEggs-1))
				break
			puzzle.printBoard(P)
			numEggs += 1

			print()

		input("Next\n")

	# The switchboard Puzzle

if __name__ == '__main__':
	main()