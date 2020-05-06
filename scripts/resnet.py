# ---------------------------------------------
# | THIS FILE WAS AUTOGENERATED! DO NOT EDIT! |
# ---------------------------------------------
# edit notebooks/25_resnet.ipynb and run generate_all.py

import sys
sys.path.insert(0, '/'.join(sys.path[0].split('/')[:-1] + ['scripts']))

from stateful_optim import *

class ResLayer(Module):
    def __init__(self, i, o, s, bottleneck):
        '''Get ResLayer (almost a ResBlock but not including the final activation).
            i: channel in
            o: channel out
            s: stride size
            bottleneck: boolean of whether the resblock is basic or bottleneck
        '''
        super().__init__()
        self.i, self.o, self.s, self.bottleneck = i, o, s, bottleneck
        self.x_layer = Identity()
        self.Fx_layer = get_bottleneck(i, o) if bottleneck else get_basic_block(self.i, self.o, self.s)

    def fwd(self, inp):
        self.fx = self.Fx_layer(inp)
        self.x = self.x_layer(inp)
        self.out = self.fx + self.x
        return self.out

    def bwd(self, out, inp):
        self.fx.g = out.g
        self.x.g = out.g
        self.Fx_layer.backward()
        self.x_layer.backward()

    def parameters(self):
        for sub_model in [self.Fx_layer, self.x_layer]:
            for param in sub_model.parameters():
                yield param

class ResBlock(SubModel):
    def __init__(self, i, o, s, bottleneck):
        '''ResBlock (ResLayer + Activation).
            i: channel in
            o: channel out
            s: stride size
            bottleneck: boolean of whether the resblock is basic or bottleneck
        '''
        super().__init__()
        self.i, self.o, self.s, self.bottleneck = i, o, s, bottleneck
        self.sub_model = Sequential(ResLayer(i, o, s, bottleneck),
                                    ReLU())

    def __repr__(self, t=''):
        return f"{t+'    '}{'Bottleneck' if self.bottleneck else 'BasicBlock'}({self.i}, {self.o}, {self.s})"