# ---------------------------------------------
# | THIS FILE WAS AUTOGENERATED! DO NOT EDIT! |
# ---------------------------------------------
# edit notebooks/13_sub_model.ipynb and run generate_all.py

import sys
sys.path.insert(0, '/'.join(sys.path[0].split('/')[:-1] + ['scripts']))

from other_layers import *

class SubModel(Module):
    def __init__(self):
        super().__init__()

    def parameters(self):
        for param in self.sub_model.parameters():
            yield param

    def fwd(self, inp):
        return self.sub_model(inp)

    def bwd(self, out, inp):
        self.sub_model.backward()

    def __repr__(self, t):
        return self.sub_model.__repr__(t+'    ')