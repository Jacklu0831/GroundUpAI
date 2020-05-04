# ---------------------------------------------
# | THIS FILE WAS AUTOGENERATED! DO NOT EDIT! |
# ---------------------------------------------
# edit notebooks/20_early_stopping.ipynb and run generate_all.py

import sys
sys.path.insert(0, '/'.join(sys.path[0].split('/')[:-1] + ['scripts']))

from param_scheduling import *

class ItersStopper(Callback):
    '''Callback to stop on specified batch/iteration (good for debugging training loop)'''
    def __init__(self, end_iter=10):
        self.end_iter = end_iter

    def after_step(self):
        print(f'iteration: {self.iters_count}')
        if self.iters_count >= self.end_iter:
            raise CancelTrainException()

    def after_cancel_train(self):
        print(f'Training cancelled at the end of iteration {self.end_iter}')

class EpochsStopper(Callback):
    '''Callback for stopping at specified epoch'''
    def __init__(self, end_epoch=10):
        self.end_epoch = end_epoch

    def before_epoch(self):
        if self.epoch > self.end_epoch:
            raise CancelTrainException()

    def after_cancel_train(self):
        print(f'Training cancelled at the end of epoch {self.end_epoch}')

class AccuracyStopper(Callback):
    '''Callback for stopping training after model does not receive improvement in specific number of epochs'''
    def __init__(self, patience=5, verbose=True):
        self.valid_stats = AvgStats([compute_accuracy], False)
        self.patience = patience
        self.verbose = verbose
        self.best_acc = 0
        self.waited = 0

    def before_epoch(self):
        self.valid_stats.reset()

    def after_loss(self):
        self.valid_stats.accumulate(self.learner)

    def _update(self):
        self.waited += 1
        if self.best_acc < self.valid_stats.avg_stats[1]:
            self.best_acc = self.valid_stats.avg_stats[1]
            self.waited = 0

    def after_epoch(self):
        if self.verbose: print(f'Epoch - {self.epoch}    Acc: {self.valid_stats.avg_stats[1]}')
        self._update()
        if self.waited > self.patience:
            raise CancelTrainException()