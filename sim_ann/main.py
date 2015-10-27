import random as rand
import colorama as cr

import eggcarton as egg
import switchboard as switch

eggPuzzles = [egg.EggCarton(5, 5, 2), egg.EggCarton(6, 6, 2),
              egg.EggCarton(8, 8, 1), egg.EggCarton(10, 10, 3)]

switchPuzzles = [switch.Switchboard(4, 4, 3, 2, (3, 1), (0, 3)),
                 switch.Switchboard(6, 5, 3, 2, (5, 0), (0, 4)),
                 switch.Switchboard(8, 8, 3, 2, (7, 1), (0, 7))]


def main():
    rand.seed()
    cr.init(autoreset=True)

    # Part 1
    print("The Egg Carton Puzzles", end="\n\n")

    for puzzle in eggPuzzles:
        print("New puzzle {}!".format(puzzle))

        FP, P = puzzle.run()

        input("Next\n")

    # Part 2
    print("The Switchboard Puzzles", end="\n\n")

    for puzzle in switchPuzzles:
        print("New puzzle: {}".format(puzzle))

        FP, P = puzzle.run()

        input("Next\n")

if __name__ == '__main__':
    main()
