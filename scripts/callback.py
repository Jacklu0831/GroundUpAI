# ---------------------------------------------
# | THIS FILE WAS AUTOGENERATED! DO NOT EDIT! |
# ---------------------------------------------
# edit notebooks/16_callback.ipynb and run generate_all.py

import sys
sys.path.insert(0, '/'.join(sys.path[0].split('/')[:-1] + ['scripts']))

from training import *

import re

def camel2snake(name):
    camel_re1 = re.compile('(.)([A-Z][a-z]+)')
    camel_re2 = re.compile('([a-z0-9])([A-Z])')
    s1 = re.sub(camel_re1, r'\1_\2', name)
    return re.sub(camel_re2, r'\1_\2', s1).lower()

class Callback():
    order = 0
    def __getattr__(self, k):
        # delegate attribute checking to learner
        return getattr(self.learner, k)

    def set_learner(self, learner):
        self.learner = learner

    @property
    def name(self):
        return re.sub(r'Callback$', '', self.__class__.__name__) or 'callback'

    def __repr__(self):
        return f'(callback) {camel2snake(self.name)}'

    def __call__(self, cb_name):
        fn = getattr(self, cb_name, None)
        if fn and fn():
            return True
        return False

class TrainEval(Callback):
    def before_train(self):
        self.model.train()

    def before_valid(self):
        self.model.eval_()