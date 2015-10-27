#!/usr/bin/python3

import copy as cp
import itertools as it

from pprint import pprint

class CSP:

    def __init__(self):
        # self.variables is a list of the variable names in the CSP
        self.variables = []

        # self.domains[i] is a list of legal values for variable i
        self.domains = {}

        # self.constraints[i][j] is a list of legal value pairs for
        # the variable pair (i, j)
        self.constraints = {}

        # Variables to record the number of backtracks and failed backtracks
        self.num_backtrack = 0
        self.num_backtrack_failed = 0

    def add_variable(self, name, domain):
        """
        Add a new variable to the CSP. 'name' is the variable name
        and 'domain' is a list of the legal values for the variable.
        """
        self.variables.append(name)
        self.domains[name] = list(domain)
        self.constraints[name] = {}

    def get_all_possible_pairs(self, a, b):
        """
        Get a list of all possible pairs (as tuples) of the values in
        the lists 'a' and 'b', where the first component comes from list
        'a' and the second component comes from list 'b'.
        """
        return it.product(a, b)

    def get_all_arcs(self):
        """
        Get a list of all arcs/constraints that have been defined in
        the CSP. The arcs/constraints are represented as tuples (i, j),
        indicating a constraint between variable 'i' and 'j'.
        """
        return [(i,j) for i in self.constraints for j in self.constraints[i]]

    def get_all_neighboring_arcs(self, var):
        """
        Get a list of all arcs/constraints going to/from variable
        'var'. The arcs/constraints are represented as in get_all_arcs().
        """
        return [(i,var) for i in self.constraints[var]]

    def add_constraint_one_way(self, i, j, filter_function):
        """
        Add a new constraint between variables 'i' and 'j'. The legal
        values are specified by supplying a function 'filter_function',
        that returns True for legal value pairs and False for illegal
        value pairs. This function only adds the constraint one way,
        from i -> j. You must ensure that the function also gets called
        to add the constraint the other way, j -> i, as all constraints
        are supposed to be two-way connections!
        """
        if not j in self.constraints[i]:
            # First, get a list of all possible pairs of values between variables i and j
            self.constraints[i][j] = self.get_all_possible_pairs(self.domains[i], self.domains[j])

        # Next, filter this list of value pairs through the function
        # 'filter_function', so that only the legal value pairs remain
        self.constraints[i][j] = tuple(filter(lambda value_pair: filter_function(*value_pair), self.constraints[i][j]))

    def add_all_different_constraint(self, variables):
        """
        Add an Alldiff constraint between all of the variables in the
        list 'variables'.
        """
        for (i, j) in self.get_all_possible_pairs(variables, variables):
            if i != j:
                self.add_constraint_one_way(i, j, lambda x, y: x != y)

    def backtracking_search(self):
        """
        This functions starts the CSP solver and returns the found
        solution.
        """
        # Make a so-called "deep copy" of the dictionary containing the
        # domains of the CSP variables. The deep copy is required to
        # ensure that any changes made to 'assignment' does not have any
        # side effects elsewhere.
        assignment = cp.deepcopy(self.domains)

        # Run AC-3 on all constraints in the CSP, to weed out all of the
        # values that are not arc-consistent to begin with
        self.inference(assignment, self.get_all_arcs())

        # Call backtrack with the partial assignment 'assignment'
        solution = self.backtrack(assignment)
        print('Num backtrack =', self.num_backtrack)
        print('Num backtrack failed =', self.num_backtrack_failed)
        return solution

    def backtrack(self, assignment):
        """
        The function 'Backtrack' from the pseudocode in the
        textbook.

        The function is called recursively, with a partial assignment of
        values 'assignment'. 'assignment' is a dictionary that contains
        a list of all legal values for the variables that have *not* yet
        been decided, and a list of only a single value for the
        variables that *have* been decided.

        When all of the variables in 'assignment' have lists of length
        one, i.e. when all variables have been assigned a value, the
        function should return 'assignment'. Otherwise, the search
        should continue. When the function 'inference' is called to run
        the AC-3 algorithm, the lists of legal values in 'assignment'
        should get reduced as AC-3 discovers illegal values.

        IMPORTANT: For every iteration of the for-loop in the
        pseudocode, you need to make a deep copy of 'assignment' into a
        new variable before changing it. Every iteration of the for-loop
        should have a clean slate and not see any traces of the old
        assignments and inferences that took place in previous
        iterations of the loop.
        """
        # Increment the number of backtrack calls
        self.num_backtrack += 1

        # Get the next box to check on
        var = self.select_unassigned_variable(assignment)
        # If there is no box to check, result found
        if var is None:
            return assignment

        # For all possible values in the box
        for value in assignment[var]:
            # Create a copy of the assignment
            assigCopy = cp.deepcopy(assignment)
            # Assign the value to the box
            assigCopy[var] = [value]

            # Generate all arcs from the box
            neighbors = self.get_all_neighboring_arcs(var)
            # If the board is consistent
            if self.inference(assigCopy, neighbors):
                # Recursive call with the assignment copy
                result = self.backtrack(assigCopy)
                # If the result is valid, return result
                if result is not None:
                    return result

        # If no values generated a valid board, then backtrack
        self.num_backtrack_failed += 1
        return None

    def select_unassigned_variable(self, assignment):
        """
        The function 'Select-Unassigned-Variable' from the pseudocode
        in the textbook. Should return the name of one of the variables
        in 'assignment' that have not yet been decided, i.e. whose list
        of legal values has a length greater than one.
        """
        # Possible candidates with domains larger than 1
        candidates = tuple(filter(lambda kv: len(kv[1]) > 1, assignment.items()))
        # If there are no candidates, return None
        if len(candidates) == 0:
            return None
        # Find the candidate with minimum domain and return variable
        min_cand = min(candidates, key=lambda kv: len(kv[1]))
        return min_cand[0]

    def inference(self, assignment, queue):
        """
        The function 'AC-3' from the pseudocode in the textbook.
        'assignment' is the current partial assignment, that contains
        the lists of legal values for each undecided variable. 'queue'
        is the initial queue of arcs that should be visited.
        """
        # While the queue is not empty
        while len(queue) != 0:
            # Pop the first item in the queue
            i, j = queue.pop(0)

            # Update the arc
            # If the arc is valid, update the queue
            if self.revise(assignment, i, j):
                # Check the domain
                Di = assignment[i]
                # If the domain is empty, the arc does not
                # create a valid board
                if len(Di) == 0:
                    # The board is not consistent
                    return False

                # If the domain is not empty,
                # add all intermediate arcs to the queue
                for k, _ in self.get_all_neighboring_arcs(i):
                    if k != i and k != j:
                        queue.append((k, i))

        # If all arcs create a valid board, then it is consistent
        return True

    def revise(self, assignment, i, j):
        """
        The function 'Revise' from the pseudocode in the textbook.
        'assignment' is the current partial assignment, that contains
        the lists of legal values for each undecided variable. 'i' and
        'j' specifies the arc that should be visited. If a value is
        found in variable i's domain that doesn't satisfy the constraint
        between i and j, the value should be deleted from i's list of
        legal values in 'assignment'.
        """
        # Variable to check if some domains have been altered
        revised = False
        # Domains for i and j
        Di, Dj = assignment[i], assignment[j]
        # Set of possible solutions for arc i and j
        Cij_set = set(self.constraints[i][j])

        # For all values in the domain i
        for x in Di:
            # Create the set of all possible values for j
            Cj_set = {(x,y) for y in Dj if x != y}
            # The set which is the union of Cij and Cj
            valid_set = Cij_set & Cj_set

            # If it is empty then there does not
            # exist a value pair which satisfies the arc
            if len(valid_set) == 0:
                # Remove the value x from the domain i
                Di.remove(x)
                revised = True

        # Return if some domains have been altered
        return revised

def create_map_coloring_csp():
    """
    Instantiate a CSP representing the map coloring problem from the
    textbook. This can be useful for testing your CSP solver as you
    develop your code.
    """
    csp = CSP()
    states = [ 'WA', 'NT', 'Q', 'NSW', 'V', 'SA', 'T' ]
    edges = { 'SA': [ 'WA', 'NT', 'Q', 'NSW', 'V' ], 'NT': [ 'WA', 'Q' ], 'NSW': [ 'Q', 'V' ] }
    colors = [ 'red', 'green', 'blue' ]

    for state in states:
        csp.add_variable(state, colors)

    for state, other_states in edges.items():
        for other_state in other_states:
            csp.add_constraint_one_way(state, other_state, lambda i, j: i != j)
            csp.add_constraint_one_way(other_state, state, lambda i, j: i != j)

    return csp

def create_sudoku_csp(filename):
    """
    Instantiate a CSP representing the Sudoku board found in the text
    file named 'filename' in the current directory.
    """
    csp = CSP()
    board = tuple(map(lambda x: x.strip(), open(filename, 'r')))

    for row in range(9):
        for col in range(9):
            if board[row][col] == '0':
                csp.add_variable('%d-%d' % (row, col), map(str, range(1, 10)))
            else:
                csp.add_variable('%d-%d' % (row, col), [board[row][col]])

    for row in range(9):
        csp.add_all_different_constraint(['%d-%d' % (row, col) for col in range(9)])

    for col in range(9):
        csp.add_all_different_constraint(['%d-%d' % (row, col) for row in range(9)])

    for box_row in range(3):
        for box_col in range(3):
            cells = []
            for row in range(box_row * 3, (box_row + 1) * 3):
                for col in range(box_col * 3, (box_col + 1) * 3):
                    cells.append('%d-%d' % (row, col))
            csp.add_all_different_constraint(cells)

    return csp

def print_sudoku_solution(solution):
    """
    Convert the representation of a Sudoku solution as returned from
    the method CSP.backtracking_search(), into a human readable
    representation.
    """
    holdr = "{} {} {} | {} {} {} | {} {} {}"
    delim = "\n------+-------+------\n"

    aux_board = "\n".join(holdr for _ in range(3))
    board = delim.join(aux_board for _ in range(3))

    pairs = ("%d-%d" % (row,col) for row in range(9) for col in range(9))
    output = (
        solution[pair][0] 
        if len(solution[pair]) == 1 
        else '.'
        for pair in pairs
    )

    print(board.format(*output))

# Possible sudoku boards
Boards = ['easy.txt', 'hard.txt', 'medium.txt', 'veryhard.txt']
Hard_boards = ['almostlockedset.txt', 'suedecoq.txt', 'escargot.txt', 'artoinkala.txt']

def main():
    # For all boards
    for board in Boards: 
        print('Board ::', board)

        # Create the CSP for the sudoku board
        csp = create_sudoku_csp('boards/' + board)
        # Find the solution if any
        solution = csp.backtracking_search()
        # And print it
        print_sudoku_solution(solution)

        input('Next\n')

    # Createh the CSP for the map coloring problem
    csp = create_map_coloring_csp()
    # Find the solution if any
    solution = csp.backtracking_search()
    # And print it
    pprint(solution)

if __name__ == '__main__':
    main()