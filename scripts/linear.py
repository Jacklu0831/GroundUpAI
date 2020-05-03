# ---------------------------------------------
# | THIS FILE WAS AUTOGENERATED! DO NOT EDIT! |
# ---------------------------------------------
# edit notebooks/04_linear.ipynb and run generate_all.py

import sys
from os.path import join
import math

sys.path.insert(0, '/'.join(sys.path[0].split('/')[:-1] + ['scripts']))
from model import *

def init_weight_he(d1, d2):
    return torch.randn(d1, d2) * (2./d1) ** 0.5

def init_weight_norm(d1, d2):
    return torch.randn(d1, d2) * (2./d1) ** 0.5

def init_weight(d1, d2, end=False):
    return init_weight_norm(d1, d2) if end else init_weight_he(d1, d2)

def init_bias_zero(d):
    return torch.zeros(d)

def init_bias_uni(d):
    return torch.randn(d)

def init_bias(d, zero=True):
    return init_bias_zero(d) if zero else init_bias_uni(d)

def softmax(inp):
    # prone to overflow (floating aint precise)
    return inp.exp() / inp.exp().sum(-1, keepdim=True)

def log_sum_exp(inp):
    e = inp.max(-1)[0]
    return e + (inp - e[:, None]).exp().sum(-1).log()

def log_softmax(inp):
    # LogSumExp trick to avoid floating point error
    return inp - log_sum_exp(inp).unsqueeze(-1)

def nll_loss(pre, tar):
    # use multiple indexing
    return -pre[range(tar.shape[0]), tar].mean()

def cross_entropy(inp, tar):
    return nll_loss(log_softmax(inp), tar)

def compute_accuracy(pre, tar):
    return (torch.argmax(pre, dim=1) == tar).float().mean()

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