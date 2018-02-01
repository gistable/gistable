from __future__ import print_function

"""
Using OpenDNS domain query activity, we retrieve 5 days
of queries/hour to a domain for 240+ domains (stored
in dns.json). We predict the number of queries in
the next hour using a LSTM recurrent neural network.

An ad hoc anomaly detection is outlined in the final
for loop.

Refer to:
    http://stackoverflow.com/questions/25967922/pybrain-time-series-prediction-using-lstm-recurrent-nets
    https://github.com/pybrain/pybrain/blob/master/examples/supervised/neuralnets%2Bsvm/example_rnn.py

"""

from pybrain.supervised import RPropMinusTrainer
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure.modules import LSTMLayer
from pybrain.datasets import SequentialDataSet
from pybrain.tools.xml import NetworkWriter
from sys import stdout
import numpy as np
import random
import json

# Get queries/hr data
with open('dns.json', 'r') as f:
    samples = map(lambda x: x['ts'][:-2], json.load(f))

# Shuffle to partition test/train
random.shuffle(samples)

# Set train & test data
train_data, test_data = samples[:50], samples[200:]

# Initialize ds for rnn for 1 obsv and 1 next
ds = SequentialDataSet(1, 1)

# Add each timeseries (ts)
for ts in train_data:
    ds.newSequence()
    # Add obsv and next
    for t_1, t_2 in zip(ts, ts[1:]):
        ds.addSample(t_1, t_2)

# RNN with 1-5-1 architecture: 1 input, 5 hidden, 1 output layer
rnn = buildNetwork(1, 5, 1,
                   hiddenclass=LSTMLayer, outputbias=False, recurrent=True)

# Initialize trainer
trainer = RPropMinusTrainer(rnn, dataset=ds)

# Predefine iterations: epochs & cycles
EPOCHS_PER_CYCLE = 5
CYCLES = 100
EPOCHS = EPOCHS_PER_CYCLE * CYCLES

# Training loop
for i in xrange(CYCLES):
    trainer.trainEpochs(EPOCHS_PER_CYCLE)
    error = trainer.testOnData()
    epoch = (i + 1) * EPOCHS_PER_CYCLE
    print("\r Epoch: {}/{} Error: {}".format(epoch, EPOCHS, error), end="")
    stdout.flush()

# Save model
NetworkWriter.writeToFile(rnn, 'rnn3.xml')

# Ad hoc test
for test in test_data:
    for i in xrange(0, len(test) - 6, 5):
        # Get 5 obs, 6th we wish to predict
        obs, nxt = test[i:i + 5], test[i + 6]

        # Predict all
        prds = map(rnn.activate, obs)
        # Get 6th prediction
        prd = prds.pop()[0]

        # Test if prd is anomalous
        anm = prd > (1 + np.mean(obs) + 2 * np.std(obs))
        # Get previous 5 obs,prd error rate
        mse = ((np.array(obs[1:]) - np.concatenate(prds)) ** 2).mean()

        print("\nSaw: {}\nNext/Prediction: {} / {}\nIs Anomaly: {}\nPrior MSE: {}".format(
            obs, round(nxt, 3), round(prd, 3), anm, mse, end=""))
        raw_input("[PRESS ENTER] for next prediction...\n")

    print("[NEXT DOMAIN] ... \n")
