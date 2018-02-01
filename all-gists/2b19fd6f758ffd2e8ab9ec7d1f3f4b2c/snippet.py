# Toy example of using a deep neural network to predict average temperature
# by month. Note that this is not any better than just taking the average
# of the dataset; it's just meant as an example of a regression analysis using
# neural networks.

import logging
import datetime

import pandas as pd
import torch
import torch.nn as nn
from torch.autograd import Variable
import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')

log = logging.getLogger(__name__)

BATCH_SIZE = 12
HIDDEN_SIZE = 512
NUM_LAYERS = 2
NUM_EPOCHS = 100
LEARNING_RATE = 0.005
DROPOUT = 0.2

class RNN(nn.Module):

    def __init__(self, input_size, hidden_size, output_size, n_layers=1, dropout=DROPOUT):
        super(RNN, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.n_layers = n_layers

        self.encoder = nn.Embedding(input_size, hidden_size)
        self.m = nn.Sequential(nn.ReLU(),
                               nn.Dropout(p=0.2),
                               nn.ReLU())
        self.decoder = nn.Linear(hidden_size, output_size)

    def forward(self, inp, hidden):
        inp = self.encoder(inp)
        # output = BATCH_SIZE, SEQLEN, HIDDEN_SIZE
        # ex. torch.Size([30, 50, 512])
        output = self.m(inp)

        # Now BATCHSIZE * SEQLEN, HIDDEN_SIZE
        # torch.Size([1500, 512])
        output = output.contiguous().view(-1, hidden.size(2))

        # Should now be BATCH_SIZE * SEQLEN, VOCAB_SIZE
        # torch.Size([1500, 154])
        logits = self.decoder(output)

        return logits, hidden

    def init_hidden(self):
        # The hidden state will use BATCH_SIZE in the 1st position even if we hand data as batch_first
        return Variable(torch.zeros(self.n_layers, BATCH_SIZE, self.hidden_size).cuda())


def main():

    print_every = 10
    # Data from https://www.kaggle.com/berkeleyearth/climate-change-earth-surface-temperature-data
    # licened under https://creativecommons.org/licenses/by-nc-sa/4.0/
    df = pd.read_csv('GlobalLandTemperaturesByState.csv')
    df = df.loc[df.State == 'Massachusetts']
    df = df.dropna()
    df['dt'] = pd.to_datetime(df.dt)
    df = df.loc[df.dt >= datetime.datetime(1800, 1, 1)]  # Dates before this are too variable
    df = df.loc[df.dt < datetime.datetime(2012, 1, 1)]  # 2013 has incomplete data
    df['month'] = df.dt.dt.month
    df['year'] = df.dt.dt.year

    rnn = RNN(12, HIDDEN_SIZE, 1, n_layers=NUM_LAYERS)
    rnn.cuda()

    optimizer = torch.optim.Adam(rnn.parameters(), lr=LEARNING_RATE)
    criterion = torch.nn.MSELoss(size_average=False)
    criterion.cuda()

    loss_avg = 0
    total_count = 0
    for epoch in range(0, NUM_EPOCHS + 1):
        df = df.sample(frac=1)  # Shuffle

        # For each year in the sequence, create a batch of length 12 (each month)
        for year in range(df.year.min(), df.year.max()):
            data = df.loc[df.year == year]

            inp = Variable(torch.LongTensor([int(i - 1) for i in data.month.values]), requires_grad=False).cuda()
            targets = Variable(torch.FloatTensor([float(f) for f in data.AverageTemperature.values]), requires_grad=False).cuda()
            hidden = rnn.init_hidden()
            rnn.train()
            rnn.zero_grad()

            output, _ = rnn(inp, hidden)

            loss = criterion(output, targets)
            loss_avg += loss.data[0]  # [ BATCHSIZE x SEQLEN ]

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_count += 1

        if epoch % print_every == 0:
            log.info("epoch=%d, %d%% loss=%.4f", epoch, epoch / NUM_EPOCHS * 100, loss_avg / total_count)


    torch.save(rnn, "weather-predictor")
    # I'm an American
    df['f'] = df.AverageTemperature.apply(lambda x: (9.0 / 5.0 * x) + 32)
    temps = []

    # Prediction stage: predict by month
    for i in range(0, 12):
        rnn.eval()
        inp = Variable(torch.LongTensor([[i]]), volatile=True).cuda()
        hidden = rnn.init_hidden()
        logits, hidden = rnn(inp, hidden)
        pred = logits[-1, :].data[0]
        temp = (9.0 / 5.0 * pred) + 32
        temps.append(temp)
        print("Average temp in month ", i + 1, int(temp))

    # Compare against the most recent year for which we have data excluded from our training set
    year = df.loc[df.year == 2012]
    p = pd.DataFrame([year.f, temps], index=[year.month])
    p.plot()
    plt.show()

if __name__ == '__main__':
    main()
