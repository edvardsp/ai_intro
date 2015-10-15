import random as rand
import eggcarton as egg

eggPuzzles = [egg.EggCarton(5, 5, 2), egg.EggCarton(6, 6, 2),
		      egg.EggCarton(8, 8, 1), egg.EggCarton(10, 10, 3)]


def main():
	rand.seed()

	# The Egg Carton Puzzle

	for puzzle in eggPuzzles:
		print("New puzzle {}!".format(puzzle))

		numEggs = puzzle.M * puzzle.K 
		print("Testing for {} eggs".format(numEggs))

		FP, P = puzzle.simulated_annealing(numEggs)
		if FP != puzzle.Ftarget:
			print("Failed to find a solution!")

		puzzle.printBoard(P)

		input("Next\n")

	# The switchboard Puzzle

	

if __name__ == '__main__':
	main()