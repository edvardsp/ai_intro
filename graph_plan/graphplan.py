from __future__ import print_function

import itertools as it


class Literal(object):

    def __init__(self, name, neg_name, _neg=False, _id=None):
        self.name = name
        self.neg_name = neg_name
        self._neg = _neg

        self._id = id(self) if _id is None else _id

    def __invert__(self):
        return Literal(self.name, self.neg_name, True, ~self._id)

    def __repr__(self):
        if self._neg:
            return "<{0},~{1}>".format(self.neg_name, ~self._id % 1000)
        else:
            return "<{0},{1}>".format(self.name, self._id % 1000)

    def __eq__(self, other):
        return self._id == other._id

    def __hash__(self):
        return self._id

    def is_neg(self, other):
        return self == ~other

    def get_name(self):
        return self.neg_name if self._neg else self.name


class Action(object):

    def __init__(self, name, precond, effect):
        self.name = name
        self.precond = precond
        self.effect = effect

        self._id = id(self)

    def __repr__(self):
        #string = "{0}\n  PRECOND: {1}\n  EFFECT: {2}\n"
        string = "{0}"
        return string.format(self.name, self.precond, self.effect)

    def __hash__(self):
        return self._id

    def is_valid(self, literals):
        return self.precond.issubset(literals)

    def is_mutex(self, other):
        for e in self.effect:
            # 1. Inconsistent effect
            if ~e in other.effect:
                return True

            # 2. Interference
            if ~e in other.precond:
                return True

        # 3. Competing needs
        for p in self.precond:
            if ~p in other.precond:
                return True

        return False


class GraphPlan(object):

    def __init__(self, literals, actions, init, goal):
        self.literals = literals
        self.actions = actions
        self.goal = goal

        self.level = 0
        self.no_good = dict()

        # Type dict(level: set(literal))
        self.S = {0: init}
        # Type dict(level: set(valid_actions))
        self.A = {0: set(a for a in actions if a.is_valid(init))}
        # Type dict(level: dict(literal: parent_actions))
        self.link = {0: {literal: set() for literal in init}}

        # Type dict(level: dict(action: set(mutex_literals)))
        self.mutex_S = {0: {}}
        # Type dict(level: dict(action: set(mutex_actions)))
        self.mutex_A = {0: self.mutex_A_add(0)}

    def mutex_S_add(self, level):
        if self.S.get(level) is None:
            raise TypeError("S[{}] does not exist".format(level))
        if level < 1:
            raise TypeError("mutex_S[{}] should not be made".format(level))

        mutexes = {literal: set() for literal in self.S[level]}
        for l1, l2 in it.combinations(self.S[level], 2):
            # Check if a negation
            if l1.is_neg(l2):
                mutexes[l1].add(l2)
                mutexes[l2].add(l1)
                continue

            # Check if all actions are mutexes
            l1_a, l2_a = self.link[level][l1], self.link[level][l2]
            for a1, a2 in it.product(l1_a, l2_a):
                if a1 not in self.mutex_A[level-1][a2]:
                    break
            else:
                mutexes[l1].add(l2)
                mutexes[l2].add(l1)

        return mutexes

    def mutex_A_add(self, level):
        if self.A.get(level) is None:
            raise TypeError("A[{}] does not exist".format(level))

        mutexes = {action: set() for action in self.A[level]}
        for a1, a2 in it.combinations(self.A[level], 2):
            if a1.is_mutex(a2):
                mutexes[a1].add(a2)
                mutexes[a2].add(a1)

        return mutexes

    def are_mutexes(self, level):
        if self.S.get(level) is None:
            raise TypeError("S[{}] does not exist".format(level))
        if self.mutex_S.get(level) is None:
            raise TypeError("mutex_S[{}] does not exist".format(level))

        if level < 1:
            return False

        for l1, l2 in it.combinations(self.goal, 2):
            if l1 in self.mutex_S[level][l2]:
                return True
            elif l2 in self.mutex_S[level][l1]:
                return True
        return False

    def goal_satisfied(self):
        if self.S.get(self.level) is None:
            raise TypeError("S[{}] does not exist".format(self.level))
        if self.mutex_S.get(self.level) is None:
            raise TypeError("mutex_S[{}] does not exist".format(self.level))

        literals_exists = self.goal.issubset(self.S[self.level])
        not_mutexes = not self.are_mutexes(self.level)

        return literals_exists and not_mutexes

    def extract_solution(self, lvl=None, literals=None):
        if lvl is None:
            lvl = self.level
        if literals is None:
            literals = self.goal
        if lvl == 0:
            return True

        action_pairs = (self.link[lvl][ltrl] for ltrl in literals)
        for ap in it.product(*action_pairs):
            for a1, a2 in it.combinations(ap, 2):
                if a1.is_mutex(a2):
                    continue

            self.solution[lvl] = ap
            new_literals = set()
            for a in ap:
                new_literals |= a.precond

            if self.extract_solution(lvl-1, new_literals):
                return True

        if lvl == self.level:
            self.solution = None

        return False

    def leveled(self):
        lvl = self.level
        if lvl < 1:
            return False

        s_lvl = self.S[lvl]
        s_lvlm1 = self.S[lvl-1]

        eq_len = len(s_lvl) == len(s_lvlm1)
        is_sub = s_lvl == s_lvlm1
        return eq_len and is_sub

    def expand(self):
        lvl = self.level
        lvlp1 = lvl + 1

        # Expand literals
        self.S[lvlp1] = set()
        self.link[lvlp1] = {}
        for action in self.A[lvl]:
            for e in action.effect:
                self.S[lvlp1].add(e)
                if self.link[lvlp1].get(e) is None:
                    self.link[lvlp1][e] = {action}
                else:
                    self.link[lvlp1][e].add(action)

        # Expand actions
        self.A[lvlp1] = set(a for a in self.actions if a.is_valid(self.S[lvlp1]))

        # Add mutexes
        self.mutex_S[lvlp1] = self.mutex_S_add(lvlp1)
        self.mutex_A[lvlp1] = self.mutex_A_add(lvlp1)

        # Increment to next level
        self.level += 1

    def solve(self):
        while True:
            if self.goal_satisfied():
                self.solution = {}
                self.extract_solution()
                if self.solution is not None:
                    return self.solution

            if self.leveled():
                return None

            self.expand()

        return None
