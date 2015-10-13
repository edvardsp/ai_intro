import time
from colorama import init, Fore, Back, Cursor


# Tested on python-3.4
# Colorama used for color handling in terminal
# Colorama library installed through pip as such
#   $ sudo pip install colorama
# or if multiple pip (for 2.x or 3.x)
#   $ sudo apt-get install python3-pip
#   $ sudo pip3 install colorama


# Which color for which node.
# Used with the colorama library.
color = {'A' : Fore.CYAN,
         'B' : Fore.YELLOW,
         '.' : Back.WHITE,
         '#' : Back.BLACK,
         'w' : Back.BLUE,
         'm' : Back.BLACK,
         'f' : Back.GREEN,
         'g' : Back.YELLOW,
         'r' : Back.WHITE}

# Cost of each node.
cost = {'A' : 1,
        'B' : 1,
        '.' : 1,
        '#' : float('Inf'),
        'w' : 100,
        'm' : 50,
        'f' : 10,
        'g' : 5,
        'r' : 1}

# Base class which defines common variables and 
# functions for each of the three search algorithms,
# A*, BFS and Dijkstra.
# 
# Nodes are defined as a 2-tuple, (x, y), which holds
# the x and y coordinate. 
class SearchBase(object):
    def __init__(self):
        self.clear()

    # Reset all variables used in the algorithm
    def clear(self):
        # Holds all nodes on the board and corresponding char
        self.nodes = dict()
        # Node to start on
        self.start = None
        # Node to reach
        self.goal = None
        # Set of all visited nodes
        self.closed_set = set()
        # Set of all nodes to visit
        self.open_set = set()
        # Dict of G-scores of all nodes
        self.g = dict()
        # Dict of F-scores of all nodes
        self.f = dict()
        # Dict to keep track of pathing
        self.came_from = dict()

    # Parse the txt file of the board into nodes
    def parseBoard(self, file):
        # Clear any old data from last board
        self.clear()

        # Retrieve data from board.txt file
        with open(file, 'r') as f:
            data = [line[:-1] for line in f]

        # Loop over each char
        for y, line in enumerate(data):
            for x, char in enumerate(line):
                # Create a node and store it
                node = (x, y)
                self.nodes[node] = char
                # Set the inital F- and G-score to Inf
                self.g[node] = self.f[node] = float('Inf')

                # Save start and goal node
                if char == 'A':
                    self.start = node
                elif char == 'B':
                    self.goal = node 

        # Store size of the board for printing
        self.x_size = len(data[0]) 
        self.y_size = len(data)

    # Calculates the heuristic score of a node, which in 
    # this case is calculated as the manhattan distance
    def heuristic(self, node):
        value = abs(node[0] - self.goal[0]) + abs(node[1] - self.goal[1]) 
        return value

    # Return the node from open_set with the lowest F-score
    def findLowestFNode(self):
        low_f = float('Inf')
        low_node = None
        for node in self.open_set:
            score = self.f[node]
            if score < low_f:
                low_f = score
                low_node = node
        return low_node

    # Return the node from open_set with the lowest G-score
    def findLowestGNode(self):
        low_g = float('Inf')
        low_node = None
        for node in self.open_set:
            score = self.g[node]
            if score < low_g:
                low_g = score
                low_node = node
        return low_node

    # Generate a list of neighboring nodes around a given node.
    # Neighbors are only to the sides, not diagonal.
    def generateNeighbors(self, node):
        neighbors = []
        for x, y in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            n = (node[0] + x, node[1] + y)
            if n in self.nodes:
                neighbors.append(n)
        return neighbors

    # Returns the cost of the given node
    def distCost(self, node):
        return cost[self.nodes[node]]

    # Prints the board.
    # Param show_sets prints the nodes in open_set
    # and closed_set if True. 
    # Param path prints the nodes in the list
    # with special chars.
    def printBoard(self, show_sets=True, path=[]):
        # For each node
        board = Cursor.POS(1, 1)
        for y in range(self.y_size):
            for x in range(self.x_size):

                n = (x, y)
                if n in self.nodes:
                    char = self.nodes[n]
                else:
                    char = '#'
                c = color[char]


                # Show Start and Goal node specially
                if n == self.start or n == self.goal:
                    board += c + char
                # If node in path, print special char
                elif n in path:
                    board += c + Fore.RED + '@'
                # If node in open_set, print special char
                elif show_sets and n in self.open_set:
                    board += c + Fore.CYAN + '*'
                # If node in closed_set, print special char
                elif show_sets and n in self.closed_set:
                    board += c + Fore.MAGENTA + 'x'
                # print only background color
                else:
                    board += c + ' '
            board += '\n'
        print(board)

    # Convenience function for printing final path
    def printPath(self, path):
        self.printBoard(True, path)
        print("Final path cost is {}".format(self.g[self.goal]))

    # Function to generate list of nodes in found path
    def reconstructPath(self, curr):
        path = [curr]
        while curr in self.came_from:
            curr = self.came_from[curr]
            path.append(curr)
        return path


# A* search algorithm, based on base class SearchBase
class Astar(SearchBase):

    # Actual algorithm, returns path of solution
    def findPath(self, showprog=False):
        # Init of sets and score dicts
        self.open_set.add(self.start)

        self.g[self.start] = 0;
        self.f[self.start] = self.g[self.start] + self.heuristic(self.start)

        # Shows iteration number 
        itr = 1

        # Main loop, loop while nodes to visit
        while self.open_set != set():
            # Current node is the node in open_set
            # with lowest F-score
            curr = self.findLowestFNode()

            # Break and return path if goal is found
            if curr == self.goal:
                return self.reconstructPath(curr)

            # Move current from open to closed set
            self.open_set.remove(curr)
            self.closed_set.add(curr)            

            # Check all neighbors to current
            for neighbor in self.generateNeighbors(curr):
                # If already visited, skip
                if neighbor in self.closed_set:
                    continue

                # Check initial G-score of neighboor
                tmp_g = self.g[curr] + self.distCost(neighbor)

                # If not visitable, add to closed set
                if tmp_g == float('Inf'):
                    self.closed_set.add(neighbor)
                    continue

                # If neighbor not in open set or lower G-score
                if neighbor not in self.open_set or tmp_g < self.g[neighbor]:
                    # Store new path, and G- and F-score
                    self.came_from[neighbor] = curr
                    self.g[neighbor] = tmp_g
                    self.f[neighbor] = self.g[neighbor] + self.heuristic(neighbor)

                    # If not in open set, add
                    if neighbor not in self.open_set:
                        self.open_set.add(neighbor)

            # Show progression if stated
            if showprog:
                self.printBoard()
                print("Iteration {}".format(itr))
                itr += 1
                time.sleep(0.05)
        
        # If no more nodes to visit and no goal found, return empty path
        return []


# BFS search algorithm, based on base class SearchBase.
# Only difference from A* is open_set is now a FIFO list,
# rather than a priority queue.
class BreadthFirstSearch(SearchBase):

    # Actual algorithm, returns path of solution
    def findPath(self, showprog=False):
        # Init of FIFO and score dicts
        self.open_set = [self.start]

        self.g[self.start] = 0;
        self.f[self.start] = self.g[self.start] + self.heuristic(self.start)

        # Shows iteration number 
        itr = 1
        
        # Main loop, loop while nodes to visit
        while self.open_set != list():
            # Current node is the first node in the list
            curr = self.open_set.pop(0)

            # Break and return path if goal is found
            if curr == self.goal:
                return self.reconstructPath(curr)

            # Add current to the closed set
            self.closed_set.add(curr)            

            # Check all neighbors to current
            for neighbor in self.generateNeighbors(curr):
                # If already visited, skip
                if neighbor in self.closed_set:
                    continue

                # Check initial G-score of neighbor
                tmp_g = self.g[curr] + self.distCost(neighbor)

                # If not visitable, add to closed set
                if tmp_g == float('Inf'):
                    self.closed_set.add(neighbor)
                    continue

                # If neighbor not in open set or lower G-score
                if neighbor not in self.open_set or tmp_g < self.g[neighbor]:
                    # Store new path, and G- and F-score
                    self.came_from[neighbor] = curr
                    self.g[neighbor] = tmp_g
                    self.f[neighbor] = self.g[neighbor] + self.heuristic(neighbor)

                    # If not in open set, add
                    if neighbor not in self.open_set:
                        self.open_set.append(neighbor)

            # Show progression if stated
            if showprog:
                self.printBoard()
                print("Iteration {}".format(itr))
                itr += 1
                time.sleep(0.05)
            
        # If no more nodes to visit and no goal found, return empty path
        return []


# Dijkstra search algorithm, based on base class SearchBase.
# Only difference from A* is open_set is now a priority queue
# on G-score, rather than on F-score.
class Dijkstra(SearchBase):

    # Actual algorithm, returns path of solution
    def findPath(self, showprog=False):
        # Init of sets and score dicts
        self.open_set.add(self.start)

        self.g[self.start] = 0;
        self.f[self.start] = self.g[self.start] + self.heuristic(self.start)

        # Shows iteration number 
        itr = 1

        # Main loop, loop while nodes to visit
        while self.open_set != set():
            # Current node is the node in open_set
            # with lowest F-score
            curr = self.findLowestGNode()

            # Break and return path if goal is found
            if curr == self.goal:
                return self.reconstructPath(curr)

            # Move current from open to closed set
            self.open_set.remove(curr)
            self.closed_set.add(curr)            

            # Check all neighbors to current
            for neighbor in self.generateNeighbors(curr):
                # If already visited, skip
                if neighbor in self.closed_set:
                    continue

                # Check initial G-score of neighbor
                tmp_g = self.g[curr] + self.distCost(neighbor)

                # If not visitable, add to closed set
                if tmp_g == float('Inf'):
                    self.closed_set.add(neighbor)
                    continue

                # If neighbor not in open set or lower G-score
                if neighbor not in self.open_set or tmp_g < self.g[neighbor]:
                    # Store new path, and G- and F-score
                    self.came_from[neighbor] = curr
                    self.g[neighbor] = tmp_g
                    self.f[neighbor] = self.g[neighbor] + self.heuristic(neighbor)

                    # If not in open set, add
                    if neighbor not in self.open_set:
                        self.open_set.add(neighbor)

            # Show progression if stated
            if showprog:
                self.printBoard()
                print("Iteration {}".format(itr))
                itr += 1
                time.sleep(0.05)
            
        # If no more nodes to visit and goal not found, return empty path
        return []


# Computes the given algorithm on all given boards
def do_task(boards, algo, show_prog):
    for board in boards:
        print(chr(27) + "[2J")

        # Parse Board
        algo.parseBoard(board)
        # Compute path
        tot_path = algo.findPath(showprog=show_prog)
        # Print result
        print("\nBoard '{}'".format(board.partition('/')[-1]))
        algo.printPath(tot_path)

        input('Press <Enter> for next board\n')

if __name__ == '__main__':
    # Colorama init
    init(autoreset=True)

    # Different boards
    boards_1 = ['boards/board-1-1.txt', 'boards/board-1-2.txt',
                'boards/board-1-3.txt', 'boards/board-1-4.txt']
    boards_2 = ['boards/board-2-1.txt', 'boards/board-2-2.txt',
                'boards/board-2-3.txt', 'boards/board-2-4.txt']
    boards_extra = ['boards/board-ex.txt', 'boards/board-ex-2.txt']

    # Different algorithms
    astar = Astar()
    bfs = BreadthFirstSearch()
    dijkstra = Dijkstra()

    # Simple terminal UI
    while True:
        print(chr(27) + "[2J")
        algo_inp = input('[a]star, [b]fs, or [d]ijkstra? ')
        if algo_inp == 'a':
            algo = astar
        elif algo_inp == 'b':
            algo = bfs
        elif algo_inp == 'd':
            algo = dijkstra
        else:
            print("Not a valid algorithm")
            continue

        show_prog = input('Show progression? [t/F] ') == 't'

        do_task(boards_1, algo, show_prog)
        do_task(boards_2, algo, show_prog)
        # Some extra boards
        #do_task(boards_extra, algo, show_prog)
