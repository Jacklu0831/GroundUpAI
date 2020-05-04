# ---------------------------------------------
# | THIS FILE WAS AUTOGENERATED! DO NOT EDIT! |
# ---------------------------------------------
# edit notebooks/08_linear.ipynb and run generate_all.py

import sys
sys.path.insert(0, '/'.join(sys.path[0].split('/')[:-1] + ['scripts']))

from initialization import *

class Module():
    def __init__(self):
        self._parameters = {}

    def __setattr__(self, k, v):
        if isinstance(v, Parameter):
            self._parameters[k] = v
        super().__setattr__(k, v)

    def __call__(self, *args):
        self.args = args
        self.out = self.fwd(*args)
        return self.out

    def parameters(self):
        for param in self._parameters.values():
            yield param

    def forward(self):
        raise NotImplementedError('Module.forward')

    def backward(self):
        self.bwd(self.out, *self.args)

class Linear(Module):
    def __init__(self, in_dim, num_hidden, end=False, require_grad=True):
        super().__init__()
        self.w = Parameter(init_weight(in_dim, num_hidden, end), require_grad)
        self.b = Parameter(init_bias(num_hidden), require_grad)

    def fwd(self, inp):
        return inp @ self.w.data + self.b.data

    def bwd(self, out, inp):
        inp.g = out.g @ self.w.data.t()
        self.w.update(inp.t() @ out.g)
        self.b.update(out.g.sum(0))

    def __repr__(self, t=''):
        return f"{t+'    '}Linear({self.w.data.shape[0]}, {self.w.data.shape[1]})"

class ReLU(Module):
    def fwd(self, inp):
        return inp.clamp_min(0.) - 0.5

    def bwd(self, out, inp):
        inp.g = (inp > 0).float() * out.g

    def __repr__(self, t=''):
        return f"{t+'    '}ReLU()"

class CrossEntropy(Module):
    def fwd(self, inp, tar):
        return cross_entropy(inp, tar)

    def bwd(self, loss, inp, tar):
        inp_soft = softmax(inp)
        inp_soft[range(tar.shape[0]), tar] -= 1
        inp.g = inp_soft / tar.shape[0]

    def __repr__(self):
        return '(CrossEntropy)'

def get_lin_model(data_bunch, num_hidden=50):
    in_dim = data_bunch.train_ds.x_data.shape[1]
    out_dim = int(max(data_bunch.train_ds.y_data) + 1)
    return Sequential(Linear(in_dim, 50),
                      ReLU(),
                      Linear(num_hidden, out_dim, end=True))