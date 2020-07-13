#
#Created:       13/07/2020
#Last update:   13/07/2020
#Authors:       Victor Reyes
#
from __future__ import division
from pyparsing import (Literal, CaselessLiteral, Word, Combine, Group, Optional,
                       ZeroOrMore, Forward, nums, alphas, oneOf)
import ConfigParser
import random
from sets import Set
import math
import array
import numpy as np
import operator
import re
import copy
import os
import sys

class NumericStringParser(object):

    def pushFirst(self, strg, loc, toks):
        self.exprStack.append(toks[0])

    def pushUMinus(self, strg, loc, toks):
        if toks and toks[0] == '-':
            self.exprStack.append('unary -')

    def __init__(self):
        """
        expop   :: '^'
        multop  :: '*' | '/'
        addop   :: '+' | '-'
        integer :: ['+' | '-'] '0'..'9'+
        atom    :: PI | E | real | fn '(' expr ')' | '(' expr ')'
        factor  :: atom [ expop factor ]*
        term    :: factor [ multop factor ]*
        expr    :: term [ addop term ]*
        """
        point = Literal(".")
        e = CaselessLiteral("E")
        fnumber = Combine(Word("+-" + nums, nums) +
                          Optional(point + Optional(Word(nums))) +
                          Optional(e + Word("+-" + nums, nums)))
        ident = Word(alphas, alphas + nums + "_$")
        plus = Literal("+")
        minus = Literal("-")
        mult = Literal("*")
        div = Literal("/")
        lpar = Literal("(").suppress()
        rpar = Literal(")").suppress()
        addop = plus | minus
        multop = mult | div
        expop = Literal("^")
        pi = CaselessLiteral("PI")
        expr = Forward()
        atom = ((Optional(oneOf("- +")) +
                 (ident + lpar + expr + rpar | pi | e | fnumber).setParseAction(self.pushFirst))
                | Optional(oneOf("- +")) + Group(lpar + expr + rpar)
                ).setParseAction(self.pushUMinus)
        # by defining exponentiation as "atom [ ^ factor ]..." instead of
        # "atom [ ^ atom ]...", we get right-to-left exponents, instead of left-to-right
        # that is, 2^3^2 = 2^(3^2), not (2^3)^2.
        factor = Forward()
        factor << atom + \
            ZeroOrMore((expop + factor).setParseAction(self.pushFirst))
        term = factor + \
            ZeroOrMore((multop + factor).setParseAction(self.pushFirst))
        expr << term + \
            ZeroOrMore((addop + term).setParseAction(self.pushFirst))
        # addop_term = ( addop + term ).setParseAction( self.pushFirst )
        # general_term = term + ZeroOrMore( addop_term ) | OneOrMore( addop_term)
        # expr <<  general_term
        self.bnf = expr
        # map operator symbols to corresponding arithmetic operations
        epsilon = 1e-12
        self.opn = {"+": operator.add,
                    "-": operator.sub,
                    "*": operator.mul,
                    "/": operator.truediv,
                    "^": operator.pow}
        self.fn = {"sin": math.sin,
                   "cos": math.cos,
                   "tan": math.tan,
                   "exp": math.exp,
                   "abs": abs,
                   "trunc": lambda a: int(a),
                   "round": round,
                   "sgn": lambda a: abs(a) > epsilon and cmp(a, 0) or 0}

    def evaluateStack(self, s):
        op = s.pop()
        if op == 'unary -':
            return -self.evaluateStack(s)
        if op in "+-*/^":
            op2 = self.evaluateStack(s)
            op1 = self.evaluateStack(s)
            return self.opn[op](op1, op2)
        elif op == "PI":
            return math.pi  # 3.1415926535
        elif op == "E":
            return math.e  # 2.718281828
        elif op in self.fn:
            return self.fn[op](self.evaluateStack(s))
        elif op[0].isalpha():
            return 0
        else:
            return float(op)

    def eval(self, num_string, parseAll=True):
        self.exprStack = []
        results = self.bnf.parseString(num_string, parseAll)
        val = self.evaluateStack(self.exprStack[:])
        return val

class Instance_creator:
    def __init__(self,domain,nb_benchs,min_dom,max_dom,sett,nb_eq,nb_var):
        self.nb_var = nb_var
        self.nb_eq = nb_eq
        self.poolsize = poolsize
        self.P = P
        self.Q = Q
        self.nb_inst = nb_inst
        self.r1 = r1
        self.r2 = r2
        self.r3 = r3
        self.r4 = r4
        self.min_dom = min_dom
        self.max_dom = max_dom
        self.sett = sett
        self.type_bench = type_bench
        self.type_pool = type_pool
        self.Q1 = Q1
        self.Q2 = Q2
        #create pool
        pool = create_pool(self.nb_eq,self.poolsize,self.nb_inst,self.r4,self.type_pool)
        #create sets
        list_sets = create_pool_expressions(self.P,self.Q,pool)
        list_sets2 = create_pool_expressions(self.nb_eq,self.Q1,pool)
        list_sets3 = create_pool_expressions(self.nb_eq,self.Q2,pool)
        #create product
        list_expressions = create_expressions(list_sets,self.nb_eq,self.P)
        list_expressions2 = create_expressions(list_sets2,self.nb_eq,self.nb_eq)
        list_expressions3 = create_expressions(list_sets3,self.nb_eq,self.nb_eq)
        #Q1set,Q2set = create_two_expressions(list_sets,self.nb_eq,self.P)
        #create constraint
        if type_bench == 'sum':
            constraints = create_constraints(list_expressions,self.r1,self.r2,self.r3,self.type_bench)
        elif type_bench == 'two-sums':
             constraint1 = create_constraints(list_expressions2,self.r1,self.r2,self.r3,'sum')
             constraint2 = create_constraints(list_expressions3,self.r1,self.r2,self.r3,'sum')
             constraints = [list() for _ in xrange(len(constraint1))]
             for i in range(0,len(constraints)):
                constraints[i] = constraint1[i]+'*'+constraint2[i]
        #evaluate each constraint with a tuple (x0,x1....,xn)
        constraints,solution = evaluate_constraints(constraints,self.min_dom,self.max_dom)
        #create file
        create_file(constraints,solution,self.min_dom,self.max_dom,self.nb_inst,self.nb_var,self.sett)
