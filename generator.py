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
    def __init__(self,min_dom,max_dom,sett,nb_eq,nb_var,min_coef,max_coef):
        self.nb_eq = nb_eq
        self.nb_var = nb_var
        self.nb_benchs = nb_benchs
        self.min_dom = min_dom
        self.max_dom = max_dom
        self.sett = sett
        self.min_coef = min_coef
        self.max_coef = max_coef
        self.sett = sett
        #create constraints
        constraints = create_constraints(self.nb_eq,self.nb_var,self.min_coef,self.max_coef)
        #evaluate each constraint with a tuple (x0,x1....,xn)
        constraints,solution = evaluate_constraints(constraints,self.min_dom,self.max_dom)
        #create file
        create_file(constraint,solution,self.min_dom,self.max_dom,self.nb_inst,self.nb_var)

def constraints(nb_eq,nb_var,min_dom,max_dom):
    constraints = [list() for _ in xrange(nb_eq)]

    return list_constraints

class Params:
    def __init__(self, configParser):
        self.configParser=configParser
        self.set_parameters("default")


    def set_parameters(self, name):
        self.set = name

        if configParser.has_option(name,  'nb_eq'):
            self.nb_eq = int(configParser.get(name, 'nb_eq'))

        if configParser.has_option(name,  'nb_var'):
            self.nb_var = int(configParser.get(name, 'nb_var'))

        if configParser.has_option(name,  'dom'):
            self.lbdom,self.ubdom = configParser.get(name, 'dom').split()
            self.lbdom = int(self.lbdom)
            self.ubdom = int(self.ubdom)

        if configParser.has_option(name,  'random_seed'):
            self.random_seed = int(configParser.get(name, 'random_seed'))

        if configParser.has_option(name,  'coef'):
            self.lbcoef,self.ubcoef = configParser.get(name, 'coef').split()
            self.lbcoef = int(self.lbcoef)
            self.ubcoef = int(self.ubcoef)

        if configParser.has_option(name, 'nb_benchs'):
            self.nb_benchs = int(configParser.get(name, 'nb_benchs'))

if __name__ == '__main__':

    configParser = ConfigParser.RawConfigParser()
    configParser.read("config.txt")

    p = Params(configParser)
    random.seed(p.random_seed)

    for sett in configParser.get('default', 'sets').split():
        p.set_parameters('default')
        p.set_parameters(sett)

        #number of constraints per equation
        for i in range(1, p.nb_benchs+1):
            Instance_creator(p.lbdom,p.ubdom,p.set,p.nb_eq,p.nb_var,p.lbcoef,p.ubcoef)
        if p.nb_inst == 1:
            print str(p.nb_benchs)+' instance has been created!'
        else:
            print str(p.nb_benchs)+' instances have been created!'
