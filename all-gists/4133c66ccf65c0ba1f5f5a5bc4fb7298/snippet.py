import torch
import torch.nn as nn
from torch.autograd import Variable
import numpy as np
import torch.utils.data as data_utils
import pandas as pd
import os
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import pickle as pkl

torch.manual_seed(1)  # reproducible
torch.cuda.set_device(1)


batch_size = 1000
seq_len = 1
out_size = 1
pred_date_len = 60

#Importing dataset
if os.path.exists('../../data/train_1.hdf'):
    pass
else:
    print('reading train_1.csv ...')
    train = pd.read_csv('../../data/train_1.csv').fillna(0) #145063*551
    print(train.columns)
    page = train['Page']
    train.head()
    #Dropping Page Column
    X = train.drop('Page',axis = 1)
    Y = X['2016-12-31'].values
    X = X.values
    shape = X.shape
    print("X",shape)

print('scale data now...')
sc = MinMaxScaler()
X = np.reshape(sc.fit_transform(np.reshape(X,(-1,1))), shape)
Y = np.reshape(sc.fit_transform(np.reshape(Y,(-1,1))), -1)
print('done.')


#trian and test split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.05)
print('Train size:',X_train.shape,'Test size:',X_test.shape)

trainDB=data_utils.TensorDataset(torch.from_numpy(X_train).float().unsqueeze(2),\
                                torch.from_numpy(Y_train).float().unsqueeze(1))
trainloader=data_utils.DataLoader(trainDB,batch_size=batch_size,shuffle=True)
testDB=data_utils.TensorDataset(torch.from_numpy(X_test).float().unsqueeze(2),\
                                torch.from_numpy(Y_test).float().unsqueeze(1))
testloader=data_utils.DataLoader(testDB,batch_size=batch_size,shuffle=True)
testdataiter=iter(testloader)

class RNN(nn.Module):
    def __init__(self):
        super(RNN, self).__init__()

        self.hidden_units = 128
        self.model = nn.Sequential()

        self.rnn = nn.RNN(
            input_size=seq_len,
            hidden_size=self.hidden_units,  # rnn hidden unit
            num_layers=2,  # number of rnn layer
            batch_first=True, # input & output will has batch size as 1st dimension. e.g. (batch, time_step, input_size)
            nonlinearity='relu',
            dropout=0.2
        )
        self.out = nn.Linear(self.hidden_units, 1)

    def forward(self, x, h_state):
        # x (batch, time_step, input_size)
        # h_state (n_layers, batch, hidden_size)
        # r_out (batch, time_step, hidden_size)
        r_out, h_state = self.rnn(x, h_state)

        outs = []  # save all predictions
        for time_step in range(r_out.size(1)):  # calculate output for each time step
            outs.append(self.out(r_out[:, time_step, :]))
        return torch.stack(outs, dim=1)[:,-1,:], h_state

        # instead, for simplicity, you can replace above codes by follows
        # r_out = r_out.view(-1, 32)
        # outs = self.out(r_out)
        # return outs, h_state



def predict():
    rnn = torch.load('rnn.mdl')
    h_state = pkl.load(open('h_state','rb'))

    trainDB = data_utils.TensorDataset(torch.from_numpy(X).float().unsqueeze(2), \
                                       torch.from_numpy(Y).float().unsqueeze(1))
    trainloader = data_utils.DataLoader(trainDB, batch_size=batch_size, shuffle=False)

    dataiter = iter(trainloader)
    x_all, _ = dataiter.next()
    y_all = torch.FloatTensor().cuda()
    while x_all.size(0) == batch_size:
        x = Variable(x_all).cuda()

        prediction, h_state = rnn(x, h_state)  # rnn output
        h_state = Variable(h_state.data)
        y_all = torch.cat((y_all,prediction.data),dim=0)
        x_all, _ = dataiter.next()
    print('last x_all size:',x_all.size())

    x = Variable(torch.cat( (x_all, torch.zeros((batch_size-x_all.size(0),x_all.size(1),1)) )
                   ,dim=0)
                 ).cuda()
    prediction, h_state = rnn(x, h_state)  # rnn output
    h_state = Variable(h_state.data)
    y_all = torch.cat((y_all,prediction.data[:x_all.size(0)]),dim=0)
    y_all = torch.squeeze(y_all,dim=1).cpu().numpy()
    print('sc before:',y_all)
    y_all = sc.inverse_transform(y_all)
    print('total y_all size:',len(y_all))
    print('sc after:',y_all)

    return y_all


def submit(y_all):
    key_1 = pd.read_csv('../../data/key_1.csv')
    ss_1 = pd.read_csv('../../data/sample_submission_1.csv')

    sub = pd.read_csv("../../data/key_1.csv", converters={'Page': lambda p: p[:-11]}, index_col='Page')\
        .join(pd.Series(y_all).to_frame(name='Visits'), how='left').fillna(0)
    print(sub)
    sub.to_csv('sub.csv', float_format='%.0f', index=False)
    return

    ids = key_1.Id.values
    pages = key_1.Page.values

    d_pages = {}
    for id, page in zip(ids, pages):
        d_pages[id] = page[:-11]

    d_visits = {}
    for page, visits_number in zip(pages, y_all):
        d_visits[page] = visits_number
    print(len(d_visits))

    print('Modifying sample submission...')
    ss_ids = ss_1.Id.values
    ss_visits = ss_1.Visits.values

    for i, ss_id in enumerate(ss_ids):
        try:
            ss_visits[i] = d_visits[d_pages[ss_id]]
        except KeyError as err:
            print('err:',i,ss_id)
            return

    print('Saving submission...')
    subm = pd.DataFrame({'Id': ss_ids, 'Visits': ss_visits})
    subm.to_csv('../../data/submission.csv', index=False)
    print('done.')

def evaluate(rnn, h_state):
    total_error=0
    dataiter = iter(testloader)
    x_all, _ = dataiter.next()
    counter = 0
    loss_func = nn.MSELoss()
    while x_all.size(0) == batch_size:
        pos = np.random.randint(pred_date_len, x_all.size(1) - pred_date_len)
        # print('pos:',pos,x_all.size())
        x = Variable(x_all[:, :pos, :]).cuda()
        y = Variable(x_all[:, pos:pos + pred_date_len, :]).cuda()
        y = y.view(batch_size, pred_date_len)
        y = y.sum(dim=1)
        # print(x, y)

        prediction,_ = rnn.forward(x,h_state)
        error = loss_func(prediction, y)
        total_error += error.data[0]

        x_all, _ = dataiter.next()
        counter+=1
    print('total error:',total_error)

def train():
    rnn = RNN().cuda()
    print(rnn)
    optimizer = torch.optim.Adam(rnn.parameters(), lr=1e-3)   # optimize all cnn parameters
    loss_func = nn.MSELoss()
    h_state = None      # for initial hidden state

    dataiter=iter(trainloader)
    for step in range(200):
        x_all, _ = dataiter.next()
        if x_all.size(0)<batch_size:
            dataiter = iter(trainloader)
            x_all, _ = dataiter.next()
        pos=np.random.randint(pred_date_len,x_all.size(1)-pred_date_len)
        # print('pos:',pos,x_all.size())
        x=Variable(x_all[:,:pos,:]).cuda()
        y=Variable(x_all[:,pos:pos+pred_date_len,:]).cuda()
        y=y.view(batch_size,pred_date_len)
        y=y.sum(dim=1)
        # print(x, y)

        prediction, h_state = rnn(x, h_state)   # rnn output
        # !! next step is important !!
        h_state = Variable(h_state.data)        # repack the hidden state, break the connection from last iteration

        loss = loss_func(prediction, y)         # cross entropy loss
        optimizer.zero_grad()                   # clear gradients for this training step
        loss.backward()                         # backpropagation, compute gradients
        print(step,loss.data[0])
        optimizer.step()                        # apply gradients

        # if step%10==0:
        #     evaluate(rnn,h_state)

    torch.save(rnn,'rnn.mdl')
    pkl.dump(h_state,open('h_state','wb'))
    print('saved rnn.mdl and h_state.')

if __name__=='__main__':
    #uncommnet the following code to predict
    #y_all = predict()
    #submit(y_all)
    #uncomment the following code to train
    train()