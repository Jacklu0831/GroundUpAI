# ---------------------------------------------
# | THIS FILE WAS AUTOGENERATED! DO NOT EDIT! |
# ---------------------------------------------
# edit notebooks/15_training.ipynb and run generate_all.py

import sys
sys.path.insert(0, '/'.join(sys.path[0].split('/')[:-1] + ['scripts']))

from optimizer import *

def fit(num_epochs, data_bunch, model, loss_fn, optimizer):
    accuracies, losses = [], []

    for epoch in range(1, num_epochs+1):
        for x_batch, y_batch in data_bunch.train_dl:
            pred = model(x_batch)
            loss = loss_fn(pred, y_batch)

            loss_fn.backward()
            model.backward()

            optimizer.step()
            optimizer.zero_grad()

        count = accuracy = loss = 0
        for x_batch, y_batch in data_bunch.valid_dl:
            pred = model(x_batch)
            accuracy += compute_accuracy(pred, y_batch)
            loss += loss_fn(pred, y_batch)
            count += 1
        accuracy /= count
        loss /= count

        accuracies.append(accuracy)
        losses.append(loss)
        print(f'Epoch {epoch}  Accuracy {round(accuracy.item(), 3)}  Loss {round(loss.item(), 3)}')

    return accuracies, losses