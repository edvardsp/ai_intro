#!/usr/bin/python

from __future__ import print_function

from pprint import pprint

from graphplan import *


def problem1():
    # Literals
    AvailSprk = Literal("AvailSprk", "NotAvailSprk")

    ShortLawn = Literal("ShortLawn", "LongLawn")
    DryLawn = Literal("DryLawn", "WetLawn")
    DryFlwrs = Literal("DryFlwrs", "WetFlwrs")

    literals = {AvailSprk, ShortLawn, DryLawn, DryFlwrs}
    literals ^= set(map(lambda n: ~n, literals))

    # Actions
    MowLawn = Action("MowLawn", {DryLawn, ~ShortLawn}, {DryLawn, ShortLawn})
    SprkLawn = Action("SprkLawn", {AvailSprk, DryLawn}, {~AvailSprk, ~DryLawn})
    SprkFlwrs = Action("SprkFlwrs", {AvailSprk, DryFlwrs}, {~AvailSprk, ~DryFlwrs})
    WcanFlwrs = Action("WcanFlwrs", {DryFlwrs}, {~DryFlwrs})

    def Pers_aux(litrl):
        name = "Pers_" + (litrl.name if not litrl._neg else litrl.neg_name)
        return Action(name, {litrl}, {litrl})

    actions = {MowLawn, SprkLawn, SprkFlwrs, WcanFlwrs}
    actions ^= set(map(Pers_aux, literals))

    # Initial and goal conditions
    init = {AvailSprk, ~ShortLawn, DryFlwrs, DryLawn}
    goal = {ShortLawn, ~DryLawn, ~DryFlwrs}

    # Solve the problem
    problem = GraphPlan(literals, actions, init, goal)
    solution = problem.solve()

    if solution is not None:
        pprint(solution)
    else:
        print('Found no solution')


def problem2():
    # Literals
    HaveCake = Literal("HaveCake", "NotHaveCake")
    EatenCake = Literal("EatenCake", "NotEatenCake")

    literals = {HaveCake, EatenCake}
    literals = literals ^ set(map(lambda n: ~n, literals))

    # Actions
    EatCake = Action("EatCake", {HaveCake}, {~HaveCake, EatenCake})
    BakeCake = Action("BakeCake", {~HaveCake}, {HaveCake})

    def Pers_aux(litrl):
        name = "Pers_" + (litrl.name if not litrl._neg else litrl.neg_name)
        return Action(name, {litrl}, {litrl})

    persistent = set(map(Pers_aux, literals))
    actions = {EatCake, BakeCake} ^ persistent

    # Initial and goal conditions
    init = {HaveCake, ~EatenCake}
    goal = {HaveCake, EatenCake}

    # Solve the problem
    problem = GraphPlan(literals, actions, init, goal)
    solution = problem.solve()

    if solution is not None:
        pprint(solution)
    else:
        print('Found no solution')

if __name__ == '__main__':
    problem1()
    problem2()
