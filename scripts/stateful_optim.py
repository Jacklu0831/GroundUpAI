# ---------------------------------------------
# | THIS FILE WAS AUTOGENERATED! DO NOT EDIT! |
# ---------------------------------------------
# edit notebooks/24_stateful_optim.ipynb and run generate_all.py

import sys
sys.path.insert(0, '/'.join(sys.path[0].split('/')[:-1] + ['scripts']))

from stateless_optim import *

def momentum_step(param, learning_rate, avg_grad, **kwargs):
    '''Momentum Stepping Function'''
    param.data -= learning_rate * avg_grad

class StatefulOpt():
    '''Improved StatelessOpt by allowing past hyperparameters values to be stored in states'''

    def __init__(self, params, steppers=None, stats=None, **hyper_params):
        self.params = [params] if isinstance(params, list) else [[params]]
        self.steppers = steppers if steppers != None else [sgd_step]
        self.stats = stats if stats != None else []
        self.state = {}
        self.hypers = [dict(hyper_params) for p in self.params]

    def _grad_params(self):
        return [(p, h) for ps, h in zip(self.params, self.hypers) for p in ps if p.grad != None]

    def step(self):
        for p, hps in self._grad_params():
            if p not in self.state:
                self.state[p] = {}
                for stat in self.stats:
                    self.state[p].update(stat.init_state(p).items())
            # update individual stat states
            p_state = self.state[p]
            for stat in self.stats:
                p_state = stat.update_state(p, p_state, **hps)
            # step
            compose_inplace(p, self.steppers, **p_state, **hps)
            self.state[p] = p_state

    def zero_grad(self):
        for hps in self.params:
            for hp in hps:
                hp.zero_grad()

    def __repr__(self):
        return f'(StatefulOpt) steppers: {[stepper.__name__ for stepper in self.steppers]}, stats: {[stat.__class__.__name__ for stat in self.stats]}'

class Stat():
    '''Class for keeping track of measurement'''
    def init_state(self, param):
        raise NotImplementedError('Stat.init_state')

    def update_state(self, param, state, **kwargs):
        raise NotImplementedError('Stat.update')

class WeightedSumGrad(Stat):
    '''Weighted gradient measurement'''
    def init_state(self, param):
        return {'avg_grad': torch.zeros_like(param.grad.data)}

    def update_state(self, param, state, mom, **kwargs):
        state['avg_grad'] = weighted_sum(state['avg_grad'], param.grad, mom)
        return state

class StepCount(Stat):
    '''Simple measurement to keep track of how many updates were done'''
    def init_state(self,p):
        return {'step': 0}

    def update_state(self, p, state, **kwargs):
        state['step'] += 1
        return state

class ExpWeightedGrad(Stat):
    '''Exponentially weighted moving avg of gradient'''
    def __init__(self, dampening=False):
        self.dampening = dampening

    def init_state(self, param):
        return {'avg_grad': torch.zeros_like(param.grad.data)}

    def update_state(self, param, state, mom, **kwargs):
        state['damp_mom'] = 1. - mom if self.dampening else 1.
        state['avg_grad'].mul_(mom).add_(state['damp_mom'], param.grad.data)
        return state

class ExpWeightedSqrGrad(Stat):
    '''Exponentially weighted moving avg of squared gradient'''
    def __init__(self, dampening=True):
        self.dampening = dampening

    def init_state(self, param):
        return {'sqr_avg_grad': torch.zeros_like(param.grad.data)}

    def update_state(self, param, state, sqr_mom, **kwargs):
        state['sqr_damp_mom'] = 1. - sqr_mom if self.dampening else 1.
        state['sqr_avg_grad'].mul_(sqr_mom).addcmul_(state['sqr_damp_mom'], param.grad.data, param.grad.data)
        return state

def debias(mom, damp, step):
    '''Util function to compute the debias coefficient for adam optimizer'''
    return damp * (1. - mom**step) / (1. - mom)

def adam(param, learning_rate, mom, damp_mom, step, sqr_mom, sqr_damp_mom, avg_grad, sqr_avg_grad, eps=1e-5, **kwargs):
    '''Adam optimizer stepper'''
    debias1 = debias(mom,     damp_mom,     step)
    debias2 = debias(sqr_mom, sqr_damp_mom, step)
    param.data.addcdiv_(-learning_rate/debias1, avg_grad, (sqr_avg_grad/debias2).sqrt() + eps)
    return param

def adam_opt(model, beta1=0.9, beta2=0.99, **kwargs):
    '''Util function to get adam optimizer'''
    return StatefulOpt(list(model.parameters()), [adam, l2_reg],
                       [ExpWeightedGrad(True), ExpWeightedSqrGrad(), StepCount()],
                       mom=beta1, sqr_mom=beta2, **kwargs)

def lamb_step(param, learning_rate, mom, damp_mom, step, sqr_mom, sqr_damp_mom, avg_grad, sqr_avg_grad, weight_decay, eps=1e-5, **kwargs):
    '''LAMB optimizer stepper'''
    debias1 = debias(mom,     damp_mom,     step)
    debias2 = debias(sqr_mom, sqr_damp_mom, step)
    r1 = param.data.pow(2).mean().sqrt()
    step = (avg_grad/debias1) / ((sqr_avg_grad/debias2).sqrt() + eps) + weight_decay*param.data
    r2 = step.pow(2).mean().sqrt()
    param.data.add_(-learning_rate * min(r1/r2, 10), step)
    return param

def lamb_opt(model, beta1=0.9, beta2=0.99, **kwargs):
    '''Util function to get LAMB optimizer'''
    return StatefulOpt(list(model.parameters()), [lamb_step],
                       [ExpWeightedGrad(True), ExpWeightedSqrGrad(), StepCount()],
                       mom=beta1, sqr_mom=beta2, **kwargs)