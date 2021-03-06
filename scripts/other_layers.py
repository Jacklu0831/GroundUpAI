# ---------------------------------------------
# | THIS FILE WAS AUTOGENERATED! DO NOT EDIT! |
# ---------------------------------------------
# edit notebooks/12_other_layers.ipynb and run generate_all.py

import sys
sys.path.insert(0, '/'.join(sys.path[0].split('/')[:-1] + ['scripts']))

from batch_norm import *

class Identity(Module):
    def __init__(self):
        '''Identity layer (for skip connections in ResNet).'''
        super().__init__()

    def fwd(self, inp): return inp

    def bwd(self, out, inp):
        # make sure not assign the gradient else model will not learn anything
        inp.g += out.g

    def __repr__(self, t=''): return f"{t+'    '}Identity()"