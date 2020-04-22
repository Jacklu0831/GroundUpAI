
#################################################
### THIS FILE WAS AUTOGENERATED! DO NOT EDIT! ###
#################################################
# file to edit: notebooks/operations.ipynb

from fastai import datasets
from pathlib import Path
import torch
import gzip
import pickle
import matplotlib as mpl
import matplotlib.pyplot as plt
from torch import tensor
import random
import operator
import os

os.environ['KMP_DUPLICATE_LIB_OK']='True'

mpl.rcParams['image.cmap'] = 'gray'

def get_mnist_data():
    return get_data('http://deeplearning.net/data/mnist/mnist.pkl')

def get_data(URL):
    path = datasets.download_data(URL, ext='.gz')
    with gzip.open(path, 'rb') as f:
        ((x_train, y_train), (x_valid, y_valid), _) = pickle.load(f, encoding='latin-1')
    x_train, y_train, x_valid, y_valid = map(tensor, (x_train, y_train, x_valid, y_valid))
    return x_train.float(), y_train.float(), x_valid.float(), y_valid.float()

def show_image(imgs):
    img = random.choice(imgs)
    if len(img.shape) == 1:
        size = int(img.shape[0] ** 0.5)
        shape = (size, size)
    else:
        shape = img.shape
    plt.imshow(img.view(shape))

def test(a, b, cmp, cname=None):
    assert cmp(a, b), f"{cname or cmp.__name__}: \n{a}\n{b}"

def near(a, b):
    return torch.allclose(a, b, rtol=1e-3, atol=1e-5)

def test_near(a, b):
    test(a, b, near)

def test_near_zero(a,tol=1e-3):
    assert a.abs() < tol, f"Near zero: {a}"

def matmul_naive(a, b):
    ar,ac = a.shape
    br,bc = b.shape
    assert ac==br
    c = torch.zeros(ar, bc)
    for i in range(ar):
        for j in range(bc):
            for k in range(ac): # or br
                c[i,j] += a[i,k] * b[k,j]
    return c

def matmul_element(a, b):
    ar,ac = a.shape
    br,bc = b.shape
    assert ac==br
    c = torch.zeros(ar, bc)
    for i in range(ar):
        for j in range(bc):
            c[i,j] = (a[i,:] * b[:,j]).sum()
    return c

def matmul_broadcast(a, b):
    ar,ac = a.shape
    br,bc = b.shape
    assert ac==br
    c = torch.zeros(ar, bc)
    for i in range(ar):
        c[i] = (a[i].unsqueeze(-1) * b).sum(dim=0)
    return c

def matmul_einsum(a, b):
    return torch.einsum('ik,kj->ij', a, b)

def matmul_torch(a, b):
    return a@b

def normalize(x, m=None, s=None):
    m = m if m else x.mean()
    s = s if s else x.std()
    return (x-m)/s

def normalize_data(x_train, x_valid):
    m, s = x_train.mean(), x_train.std()
    x_train, xv = normalize(x_train), normalize(x_valid, m, s)
    return x_train, x_valid