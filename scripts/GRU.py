# ---------------------------------------------
# | THIS FILE WAS AUTOGENERATED! DO NOT EDIT! |
# ---------------------------------------------
# edit notebooks/27_GRU.ipynb and run generate_all.py

import sys
from os.path import join

sys.path.insert(0, '/'.join(sys.path[0].split('/')[:-1] + ['scripts']))
from LSTM import *

class GRUCell(nn.Module):
    def __init__(self, i_dim, h_dim):
        super().__init__()
        self.i_dim, self.h_dim = i_dim, h_dim
        self.Wz = nn.Parameter(init_2d_weight((i_dim, h_dim)))
        self.Wr = nn.Parameter(init_2d_weight((i_dim, h_dim)))
        self.Wh = nn.Parameter(init_2d_weight((i_dim, h_dim)))
        self.Uz = nn.Parameter(init_2d_weight((h_dim, h_dim)))
        self.Ur = nn.Parameter(init_2d_weight((h_dim, h_dim)))
        self.Uh = nn.Parameter(init_2d_weight((h_dim, h_dim)))
        self.bz = nn.Parameter(torch.zeros(h_dim))
        self.br = nn.Parameter(torch.zeros(h_dim))

    def forward(self, x, h):
        z =   (x @ self.Wz + h @ self.Uz).sigmoid()
        r =   (x @ self.Wr + h @ self.Ur).sigmoid()
        h_t = (x @ self.Wh + r * h @ self.Uh).tanh()
        h = weighted_sum(h, h_t, z)
        return h

class GRULayer(nn.Module):
    def __init__(self, i_dim, h_dim):
        super().__init__()
        self.cell = GRUCell(i_dim, h_dim)

    def forward(self, inps, h):
        outputs = []
        for inp in inps.unbind(1):
            h = self.cell(inp, h)
            outputs.append(h)
        return torch.stack(outputs, 1), h