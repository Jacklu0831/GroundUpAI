# ---------------------------------------------
# | THIS FILE WAS AUTOGENERATED! DO NOT EDIT! |
# ---------------------------------------------
# edit notebooks/16_progress_bar.ipynb and run generate_all.py

import sys
from os.path import join
from fastprogress import master_bar, progress_bar
from fastprogress.fastprogress import format_time

sys.path.insert(0, '/'.join(sys.path[0].split('/')[:-1] + ['scripts']))
from early_stopping import *

class StatsLogging(Callback):
    def __init__(self, metrics=[compute_accuracy]):
        self.train_stats = AvgStats(metrics, True)
        self.valid_stats = AvgStats(metrics, False)

    def before_fit(self):
        metric_names = ['loss'] + [m.__name__ for m in self.train_stats.metrics]
        names = ['epoch'] + [f'train_{n}' for n in metric_names] + [
            f'valid_{n}' for n in metric_names] + ['time']
        self.logger(names)

    def before_epoch(self):
        self.train_stats.reset()
        self.valid_stats.reset()
        self.start_time = time.time()

    def after_loss(self):
        stats = self.train_stats if self.model.training else self.valid_stats
        stats.accumulate(self.learner)

    def after_epoch(self):
        stats = [str(self.epoch)]
        for o in [self.train_stats, self.valid_stats]:
            stats += [f'{v:.6f}' for v in o.avg_stats]
        stats += [format_time(time.time() - self.start_time)]
        self.logger(stats)

class ProgressViewer(Callback):
    order = -1

    def before_fit(self):
        self.mbar = master_bar(range(self.num_epochs))
        self.mbar.on_iter_begin()
        self.learner.logger = partial(self.mbar.write, table=True)

    def after_fit(self):
        self.mbar.on_iter_end()

    def after_batch(self):
        self.pb.update(self.iters_count)

    def set_pb(self, data_loader):
        self.pb = progress_bar(data_loader, parent=self.mbar)
        self.mbar.update(self.epoch)

    def before_epoch(self):
        self.set_pb(self.data_bunch.train_dl)

    def before_valid(self):
        self.set_pb(self.data_bunch.valid_dl)