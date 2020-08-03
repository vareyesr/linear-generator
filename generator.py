#
#Created:       13/07/2020
#Last update:   17/07/2020
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

class Instance_creator:
    def __init__(self,min_dom,max_dom,initial_domain_lb,initial_domain_ub,sett,nb_eq,nb_var,min_coef,max_coef,sparsing_factor,bench_id,uniform_dom):
        self.nb_eq = nb_eq
        self.nb_var = nb_var
        self.min_dom = min_dom
        self.max_dom = max_dom
        self.sett = sett
        self.min_coef = min_coef
        self.max_coef = max_coef
        self.sparsing_factor = sparsing_factor
        self.bench_id = bench_id
        self.initial_domain_lb = initial_domain_lb
        self.initial_domain_ub = initial_domain_ub
        self.uniform_dom = uniform_dom
        #create constraints
        constraints = create_constraints(self.nb_eq,self.nb_var,self.min_coef,self.max_coef,self.sparsing_factor)
        #evaluate each constraint with a tuple (x0,x1....,xn)
        constraints,solution = evaluate_constraints(constraints,self.min_dom,self.max_dom)
        #create file
        create_file(constraints,solution,self.min_dom,self.max_dom,self.initial_domain_lb,self.initial_domain_ub,self.sett,self.bench_id,self.uniform_dom)

def create_constraints(nb_eq,nb_var,min_coef,max_coef,sparsing_factor):
    list_constraints = [list() for _ in xrange(nb_eq)]
    for i in range(0,len(list_constraints)):
        constraint = []
        for j in range(0,int(nb_var)):
            constraint.append(round(random.uniform(int(min_coef),int(max_coef)),2))
        list_constraints[i] = constraint
    for i in range(0,len(list_constraints)):
        for j in range(0,len(list_constraints[i])):
            num_prob = random.uniform(0,1)
            if num_prob > sparsing_factor:
                list_constraints[i][j] = 0
    return list_constraints

def evaluate_constraints(constraints,min_dom,max_dom):
    solution = np.zeros(len(constraints[0]))
    #a random solution is generated
    for i in range(0, len(constraints[0])):
        solution[i] = random.uniform(min_dom,max_dom)
    for i in range(0,len(constraints)):
        current_value = 0.0
        for j in range(0,len(constraints[i])):
            current_value = current_value + constraints[i][j]*solution[j]
        constraints[i].append(current_value)
    return constraints, solution

def create_file(constraint,solution,min_dom,max_dom,initial_domain_lb,initial_domain_ub,sett,bench_id,uniform_dom):
    list_domains = [1] ## TODO: set it as input
    for k in list_domains:
        if not os.path.exists('benchs'):
            os.makedirs('benchs')
        if not os.path.exists('benchs/'+sett):
            os.makedirs('benchs/'+sett)
        completeName = os.path.join('benchs/'+sett, 'problem'+ "%03d" % (bench_id)+"_"+(str(k))+".txt")
        f = open(completeName,"w+")
        f.write(str(len(constraint))+'\n')
        f.write(str(len(solution))+'\n')
        for i in range(0,len(constraint)):
            for j in range(0,len(constraint[i])):
                f.write(str(constraint[i][j])+' ')
            f.write('\n')

        if (uniform_dom == 'False'):
            for i in range(0,len(solution)):
                alpha = round(random.uniform(initial_domain_lb,0),2)
                f.write(str(alpha)+' '+str(alpha+k*(initial_domain_ub-initial_domain_lb))+'\n')
        else:
            for i in range(0,len(solution)):
                f.write(str(initial_domain_lb)+' '+str(initial_domain_ub)+'\n')

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

        if configParser.has_option(name,  'uniform_dom'):
            self.uniform_dom = str(configParser.get(name, 'uniform_dom'))

        if configParser.has_option(name,  'sparsing_factor'):
            self.sparsing_factor = float(configParser.get(name, 'sparsing_factor'))

        if configParser.has_option(name,  'domain_solution'):
            self.lbdom,self.ubdom = configParser.get(name, 'domain_solution').split()
            self.lbdom = int(self.lbdom)
            self.ubdom = int(self.ubdom)

        if configParser.has_option(name,  'domain'):
            self.initial_domain_lb,self.initial_domain_ub = configParser.get(name, 'domain').split()
            self.initial_domain_lb = int(self.initial_domain_lb)
            self.initial_domain_ub = int(self.initial_domain_ub)

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
            Instance_creator(p.lbdom,p.ubdom,p.initial_domain_lb,p.initial_domain_ub,p.set,p.nb_eq,p.nb_var,p.lbcoef,p.ubcoef,p.sparsing_factor,i,p.uniform_dom)
        if p.nb_benchs == 1:
            print str(p.nb_benchs)+' instance has been created!'
        else:
            print str(p.nb_benchs)+' instances have been created!'
