# ---------------------------------------------
# | THIS FILE WAS AUTOGENERATED! DO NOT EDIT! |
# ---------------------------------------------
# edit notebooks/07_model.ipynb and run generate_all.py

import sys
sys.path.insert(0, '/'.join(sys.path[0].split('/')[:-1] + ['scripts']))

from augmentation import *

class Sequential():
    def __init__(self, *args):
        assert args, 'empty model'
        self.layers = args[0] if isinstance(args[0], list) else list(args)
        self.training = True

    def __call__(self, data):
        for layer in self.layers:
            data = layer(data)
        return data

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

    def __repr__(self, t=''):
        header = '(Model)\n' if t == '' else ''
        return header + ('\n').join(layer.__repr__(t) for layer in self.layers)