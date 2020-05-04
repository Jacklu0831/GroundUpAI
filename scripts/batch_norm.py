# ---------------------------------------------
# | THIS FILE WAS AUTOGENERATED! DO NOT EDIT! |
# ---------------------------------------------
# edit notebooks/11_batch_norm.ipynb and run generate_all.py

import sys
sys.path.insert(0, '/'.join(sys.path[0].split('/')[:-1] + ['scripts']))

from pooling import *

def weighted_sum(t1, t2, ratio):
    '''Util function for linear combination of two elements'''
    return t1 * ratio + t2 * (1 - ratio)

class BatchNorm(Module):
    '''Batch normalization layer'''
    def __init__(self, c, momentum=0.1, epsilon=1e-6):
        super().__init__()
        self.momentum = momentum
        self.epsilon = epsilon
        self.mean = torch.zeros(1,c,1,1)
        self.var  = torch.ones (1,c,1,1)
        # trainable linear transformation
        self.gamma = Parameter(torch.ones (1,c,1,1))
        self.beta  = Parameter(torch.zeros(1,c,1,1))

    def update_stats(self, inp):
        mean = inp.mean((0,2,3), keepdim=True)
        var =  inp.var ((0,2,3), keepdim=True)
        self.mean = weighted_sum(self.mean, mean, self.momentum)
        self.var = weighted_sum(self.var, var, self.momentum)
        return mean, var

    def fwd(self, inp):
        mean, var = self.update_stats(inp)
        self.x_hat = (inp - mean) / (var + self.epsilon).sqrt()
        return self.gamma.data * self.x_hat + self.beta.data

    def bwd(self, out, inp):
        # learned from: https://kratzert.github.io/2016/02/12/understanding-the-gradient-flow-through-the-batch-normalization-layer.html
        dL = out.g
        dLdg = (dL * self.x_hat).sum((0,2,3), keepdim=True)
        dLdb = dL.sum((0,2,3), keepdim=True)
        self.gamma.update(dLdg)
        self.beta.update(dLdb)

        n = dL.shape[0]
        dLdx = dL * self.gamma.data

        denom = (self.var + self.epsilon).sqrt()
        numer = inp - self.mean

        dv = (-1/2)*dLdx*numer / (self.var+self.epsilon)**1.5
        dm = ( 2/n)*dLdx/denom + numer*dv

        inp.g = (2*dv*numer + dm)/n + dLdx/denom

    def __repr__(self, t=''):
        return f"{t+'    '}BatchNorm()"

def get_conv_final_model(data_bunch):
    '''Util function to get convolutional model with pooling and batch normalization layers'''
    return Sequential(Reshape((1, 28, 28)),
                      Conv(c_in=1, c_out=4, k_s=5, stride=2, pad=1), # 4, 13, 13
                      AvgPool(k_s=2, pad=0), # 4, 12, 12
                      BatchNorm(4),
                      Conv(c_in=4, c_out=16, stride=2, leak=1.), # 16, 5, 5
                      BatchNorm(16),
                      Flatten(),
                      Linear(400, 64),
                      ReLU(),
                      Linear(64, 10, True))