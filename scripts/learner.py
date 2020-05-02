# ---------------------------------------------
# | THIS FILE WAS AUTOGENERATED! DO NOT EDIT! |
# ---------------------------------------------
# edit notebooks/12_learner.ipynb and run generate_all.py

import sys
from os.path import join

sys.path.insert(0, '/'.join(sys.path[0].split('/')[:-1] + ['scripts']))
from callback import *

class EpochLogger(Callback):
    def before_epoch(self):
        print(f'Epoch {self.epoch}')

class CancelTrainException(Exception): pass
class CancelEpochException(Exception): pass
class CancelBatchException(Exception): pass

class Learner():
    def __init__(self, data_bunch, model, loss_fn, optimizer, callbacks=[]):
        self.data_bunch = data_bunch
        self.model = model
        self.loss_fn = loss_fn
        self.optimizer = optimizer
        self.callbacks = sorted([TrainEval()] + callbacks, key=lambda cb: cb.order)
        for callback in self.callbacks:
            callback.learner = self

    def __repr__(self):
        return f'{self.data_bunch}\n{self.model}\n{self.loss_fn}\n{self.optimizer}\n(Callbacks) {[cb.__class__.__name__ for cb in self.callbacks]}'

    def one_batch(self, x_batch, y_batch):
        try:
            self.x_batch = x_batch
            self.y_batch = y_batch
            if self('before_batch'):     return
            self.pred = self.model(self.x_batch)
            if self('after_pred'):       return
            self.loss = self.loss_fn(self.pred, self.y_batch)
            if self('after_loss'):       return
            if not self.model.training:  return
            self.loss_fn.backward()
            if self('after_loss_back'):  return
            self.model.backward()
            if self('after_model_back'): return
            self.optimizer.step()
            if self('after_step'):       return
            self.optimizer.zero_grad()
        except CancelBatchException:
            self('after_cancel_batch')

    def all_batches(self):
        data_loader = self.data_bunch.train_dl if self.model.training else self.data_bunch.valid_dl
        self.iters_count, self.iters = 0, len(data_loader)
        try:
            for x_batch, y_batch in data_loader:
                self.one_batch(x_batch, y_batch)
                self.iters_count += 1
                self('after_batch')
        except CancelEpochException:
            self('after_cancel_epoch')

    def fit(self, num_epochs):
        self.num_epochs = num_epochs

        for callback in self.callbacks:
            callback.set_learner(self)

        if self('before_fit'):       return
        try:
            for epoch in range(1, num_epochs+1):
                self.epoch = epoch
                if self('before_epoch'): return
                if self('before_train'): return
                self.all_batches()
                if self('before_valid'): return
                self.all_batches()
                if self('after_epoch'): break
        except CancelTrainException:
            self('after_cancel_train')
        finally:
            self('after_fit')

    def __call__(self, callback_name):
        for callback in self.callbacks:
            if callback(callback_name):
                return True
        return False