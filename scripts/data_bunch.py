# ---------------------------------------------
# | THIS FILE WAS AUTOGENERATED! DO NOT EDIT! |
# ---------------------------------------------
# edit notebooks/03_data_bunch.ipynb and run generate_all.py

import sys
sys.path.insert(0, '/'.join(sys.path[0].split('/')[:-1] + ['scripts']))

import math
from data_block import *

class Dataset():
    def __init__(self, x_data, y_data):
        '''Dataset class to store data and labels.
            x_data: input data
            y_data: output labels
        '''
        self.x_data = x_data
        self.y_data = y_data

    def __repr__(self, t=''):
        return f'{t}(Dataset) x: {tuple(self.x_data.shape)}, y: {tuple(self.y_data.shape)}'

    def __len__(self): return len(self.x_data)

    def __getitem__(self, i): return self.x_data[i], self.y_data[i]

class Sampler():
    def __init__(self, size, batch_size, shuffle):
        '''Simple indices generator with option to randomly sample input data.
            size: total size of data
            batch_size: number of items per iteration
            shuffle: boolean of whether to shuffle the data
        '''
        self.size = size
        self.batch_size = batch_size
        self.shuffle = shuffle

    def __iter__(self):
        self.idxs = torch.randperm(self.size) if self.shuffle else torch.arange(self.size)
        for i in range(0, self.size, self.batch_size):
            yield self.idxs[i: i+self.batch_size]

    def __repr__(self, t=''):
        return f'{t}(Sampler) total: {self.size}, batch_size: {self.batch_size}, shuffle: {self.shuffle}'

    def __len__(self): return self.batch_size

def collate(batch):
    '''Util function to stack batches of x and y data.
        batch: container of input data
    '''
    x_batch, y_batch = zip(*batch)
    return torch.stack(x_batch), torch.stack(y_batch)

class DataLoader():
    def __init__(self, dataset, sampler, collate_fn=collate):
        '''Data loader class with data/label data and sampler to batch generation.
            dataset: Dataset class with x and y data
            sampler: Sampler class
            collate_fn: collate function for sampled batches
        '''
        self.dataset = dataset
        self.sampler = sampler
        self.collate_fn = collate_fn

    def __iter__(self):
        for idxs in self.sampler:
            yield self.collate_fn([self.dataset[i] for i in idxs])

    def __repr__(self, t=''):
        tt = t + '    '
        return f'{t}(DataLoader) \n{self.dataset.__repr__(tt)}\n{self.sampler.__repr__(tt)}'

    def __len__(self):
        return math.ceil(len(self.dataset) / len(self.sampler))

class DataBunch():
    def __init__(self, train_dl, valid_dl):
        '''Data bunch class with both training and validation data loaders.
            train_dl: data loader for training data
            valid_dl: data loader for validation data
        '''
        self.train_dl = train_dl
        self.valid_dl = valid_dl

    @property
    def train_ds(self): return self.train_dl.dataset

    @property
    def valid_ds(self): return self.valid_dl.dataset

    def __repr__(self, t=''):
        tt = t + '    '
        return f'{t}(DataBunch) \n{self.train_dl.__repr__(tt)}\n{self.valid_dl.__repr__(tt)}'

    def __len__(self): return len(self.train_dl)

def get_data_bunch(xt, yt, xv, yv, batch_size):
    '''Util function for converting existing data to data bunch class for training.
        xt: x (input) training data
        yt: y (label) training data
        xv: x (input) validation data
        yv: y (label) validation data
        batch_size: number of items per iteration
    '''
    train_ds = Dataset(xt, yt)
    valid_ds = Dataset(xv, yv)
    train_dl = DataLoader(train_ds, Sampler(len(train_ds), batch_size, True))
    valid_dl = DataLoader(valid_ds, Sampler(len(valid_ds), batch_size*2, False)) # twice batch size (no backprop)
    return DataBunch(train_dl, valid_dl)