# ---------------------------------------------
# | THIS FILE WAS AUTOGENERATED! DO NOT EDIT! |
# ---------------------------------------------
# edit notebooks/03_model.ipynb and run generate_all.py

import sys
from os.path import join
import math

sys.path.insert(0, '/'.join(sys.path[0].split('/')[:-1] + ['scripts']))
from data_bunch import *

class Sequential():
    def __init__(self, *args):
        self.layers = list(args)
        self.training = True

    def __call__(self, data):
        for layer in self.layers:
            data = layer(data)
        return data

    def __repr__(self):
        return '(Sequential)\n\t' + '\n\t'.join(f'(Layer{i}) {layer}' for i, layer in enumerate(self.layers, 1))

    def train(self):
        self.training = True

    def eval_(self):
        self.training = False

    def backward(self):
        for layer in reversed(self.layers):
            layer.backward()

    def parameters(self):
        for layer in self.layers:
            for parameter in layer.parameters():
                yield parameter