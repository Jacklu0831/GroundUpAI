# ---------------------------------------------
# | THIS FILE WAS AUTOGENERATED! DO NOT EDIT! |
# ---------------------------------------------
# edit notebooks/14_optimizer.ipynb and run generate_all.py

import sys
sys.path.insert(0, '/'.join(sys.path[0].split('/')[:-1] + ['scripts']))

from loss import *

class Optimizer():
    # vanilla
    def __init__(self, parameters, learning_rate):
        self.parameters = parameters
        self.learning_rate = learning_rate

    def __repr__(self):
        return f'(Optimizer) learning_rate: {self.learning_rate}'

    def step(self):
        for parameter in self.parameters:
            parameter.step(self.learning_rate)

    def zero_grad(self):
        for parameter in self.parameters:
            parameter.zero_grad()

class DynamicOpt():
    # for things like param scheduling or having multiple hyper params
    def __init__(self, parameters, **hyper_params):
        self.parameters = parameters
        self.hyper_params = dict(hyper_params)

    def __repr__(self):
        return f'(DynamicOpt) hyper_params: {list(self.hyper_params)}'

    def step(self):
        for parameter in self.parameters:
            parameter.step(self.hyper_params['learning_rate'])

    def zero_grad(self):
        for parameter in self.parameters:
            parameter.zero_grad()