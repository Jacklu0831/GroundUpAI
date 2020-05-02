# ---------------------------------------------
# | THIS FILE WAS AUTOGENERATED! DO NOT EDIT! |
# ---------------------------------------------
# edit notebooks/13_stats_logging.ipynb and run generate_all.py

import sys
from os.path import join

sys.path.insert(0, '/'.join(sys.path[0].split('/')[:-1] + ['scripts']))
from learner import *

class AvgStats():
    def __init__(self, metrics, training):
        self.metrics = metrics
        self.training = training

    def reset(self):
        self.count = 0
        self.total_loss = torch.Tensor([0])
        self.totals = [torch.Tensor([0])] * len(self.metrics)

    @property
    def all_stats(self): return [self.total_loss] + self.totals

    @property
    def avg_stats(self): return [s.item()/self.count for s in self.all_stats]

    def __repr__(self):
        if not self.count:
            return ''
        return f"{'train' if self.training else 'valid'} metrics - {self.avg_stats}"

    def accumulate(self, learner):
        batch_size = learner.x_batch.shape[0]
        self.count += batch_size
        self.total_loss = learner.loss * batch_size
        for i, metric in enumerate(self.metrics):
            self.totals[i] += metric(learner.pred, learner.y_batch) * batch_size

class StatsLogging(Callback):
    def __init__(self, metrics=[compute_accuracy]):
        self.train_stats = AvgStats(metrics, True)
        self.valid_stats = AvgStats(metrics, False)

    def before_epoch(self):
        self.train_stats.reset()
        self.valid_stats.reset()

    def after_loss(self):
        stats = self.train_stats if self.model.training else self.valid_stats
        stats.accumulate(self.learner)

    def after_epoch(self):
        print(f'Epoch - {self.epoch}\n{self.train_stats}\n{self.valid_stats}\n')