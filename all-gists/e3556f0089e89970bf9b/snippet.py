import numpy as np
import chainer
import chainer.functions as F
from chainer import Variable,FunctionSet,optimizers,cuda
import argparse
import convert
import csv
import brica1

class LSTMmodel(FunctionSet):
    def __init__(self,n_input,n_hidden,n_output):
        super(LSTMmodel,self).__init__(
                                #l0 = F.Linear(n_input , n_hidden),
                                 l1_x = F.Linear(n_input ,  4*n_hidden),
                                 l1_h = F.Linear(n_hidden , 4*n_hidden),
                                 l2_x = F.Linear(n_hidden , 4*n_hidden),
                                 l2_h = F.Linear(n_hidden , 4*n_hidden),
                                 l3 = F.Linear(n_hidden , n_output)
                                 )
    

    def forward(self,x_data,y_data,train = True):
        x = Variable(np.array(x_data,dtype=np.float32),volatile=not train)
        t = Variable(y_data,volatile=not train)
        state_c1 = Variable(LSTMcomponent.inputs["state_c1"],volatile=not train)
        state_h1 = Variable(LSTMcomponent.inputs["state_h1"],volatile=not train)
        state_c2 = Variable(LSTMcomponent.inputs["state_c2"],volatile=not train)
        state_h2 = Variable(LSTMcomponent.inputs["state_h2"],volatile=not train)
        
        #h0 = self.l0(x)
        h1_in = self.l1_x(F.dropout(x,train=train)) + self.l1_h(state_h1)
        c1,h1 = F.lstm(c2,h1_in)
        h2_in = self.l2_x(F.dropout(state_h1,train=train)) + self.l2_h(state_h2)
        c2,h2 = F.lstm(state_c1,h2_in)
        y = self.l3(F.dropout(h2,train=train))
        LSTMcomponent.inputs["state_c1"] = c1
        LSTMcomponent.inputs["state_h1"] = h1
        LSTMcomponent.inputs["state_c2"] = c2
        LSTMcomponent.inputs["state_h2"] = h2

        loss = F.softmax_cross_entropy(y,t)
        accuracy = F.accuracy(y,t)
        
        return loss,accuracy
    
    def predict(self,x_data):
        x = Variable(x_data)
        h1_in = self.l1_x(x) + self.l1_h(state['h1'])
        c1,h1 = F.lstm(state['c1'],h1_in)
        h2_in = self.l2_x(h1) + self.l2_h(state['h2'])
        c2,h2 = F.lstm(state['c2'],h2_in)
        y = F.softmax(self.l3(h2))

        return y.data

class LSTMComponent(brica1.Component):
    def __init__(self,n_input,n_hidden,n_output,use_gpu=False):
        super(LSTMComponent,self).__init__()
        self.model = LSTMmodel(n_input,n_hidden,n_output)
        self.optimizer = optimizers.Adam()
        self.training = True

        self.make_in_port("input",n_input)
        self.make_in_port("hidden",n_hidden)
        self.make_in_port("state_c1",n_hidden)
        self.make_in_port("state_h1",n_hidden)
        self.make_in_port("state_c2",n_hidden)
        self.make_in_port("state_h2",n_hidden)
        self.make_out_port("loss",1)
        self.make_out_port("accuracy",1)
        self.make_out_port("output",n_output)
        
        self.use_gpu = use_gpu
        
        if self.use_gpu:
            self.model.to_gpu()

        self.optimizer.setup(self.model.collect_parameters())
    

    def fire(self):
        x_data = self.inputs["input"].astype(np.float32)
        t_data = self.inputs["target"].astype(np.int16)
        
        if self.use_gpu:
            x_data = cuda.to_gpu(x_data)
            t_data = cuda.to_gpu(t_data)
        
        self.optimizer.zero_grads()
        state, loss, accuracy = self.model.forward(x_data, t_data)
        loss.backward()
        self.optimizer.update()
        self.results["loss"] = loss.data

        y_data = self.model.output(x_data)
        self.results["output"] = y_data



class Autoencoder(FunctionSet):
    def __init__(self,n_input,n_output):
        super(Autoencoder,self).__init__(
                                         encoder = F.Linear(n_input , n_output),
                                         decoder = F.Linear(n_output , n_input)
                                         )
    
    def forward(self,x_data):
        x = Variable(x_data)
        t = Variable(x_data)
        x = F.dropout(x)
        h = F.sigmoid(self.encoder(x))
        y = F.sigmoid(self.decoder(h))
        loss = F.mean_squared_error(y,t)
        
        return loss
    
    def encode(self,x_data):
        x = Variable(x_data)
        h = F.sigmoid(self.encoder(x))
        
        return h.data

class AutoencoderComponent(brica1.Component):
    def __init__(self, n_input,n_output):
        super(AutoencoderComponent,self).__init__()
        self.model = Autoencoder(n_input,n_output)
        self.optimizer = optimizers.Adam()
        self.optimizer.setup(self.model.collect_parameters())
        
        self.make_in_port("input",n_input)
        self.make_out_port("output",n_output)
        self.make_out_port("loss",1)
    
    def fire(self):
        x_data = self.inputs["input"].astype(np.float32)
        
        self.optimizer.zero_grads()
        loss = self.model.forward(x_data)
        loss.backward()
        self.optimizer.update()
        self.results["loss"] = loss.data
        
        y_data = self.model.encode(x_data)
        self.results["output"] = y_data


def make_initial_state(lstm_n_units,train=True):
    return chainer.Variable(xp.zeros(lstm_n_units,dtype=np.float32),volatile=not train)

def make_initial_state2(lstm_n_units):
    return xp.zeros(lstm_n_units,dtype=np.float32)

def make_initial_state3(lstm_n_units):
    return xp.zeros((lstm_n_units,lstm_n_units),dtype=np.float32)

#evaluate only t = 15
def evaluate(ydata,tdata):
    while True:
        #first time
        if isinstance(ydata[0],int):
            break
                
        t = 15
        num = len(ydata)*len(ydata[0])/t
        ydata = xp.array(ydata)
        tdata = xp.array(tdata)
        
        ydata_reshape = xp.array(ydata).reshape((num,t))
        
        tdata_reshape = xp.array(tdata).reshape((num,t))

        tdata_last_all = tdata_reshape[:,14]
        ydata_last_all = ydata_reshape[:,14]
        
        allmatched_list = []
        for i in range(len(ydata_last_all)):
            if ydata_last_all[i] == tdata_last_all[i]:
                allmatched_list.append(ydata_last_all[i])
 
        size = 200
        start = tdata_reshape.shape[0] - size

        tdata_last = tdata_reshape[start:start+size,14]
        ydata_last = ydata_reshape[start:start+size,14]
    
        matched_list = []
        for i in range(len(ydata_last)):
            if ydata_last[i] == tdata_last[i]:
                matched_list.append(ydata_last[i])


        accuracy_last_all = float(len(allmatched_list))/float(len(ydata_last_all))
        accuracy_last = float(len(matched_list))/float(len(ydata_last))
        return accuracy_last_all,accuracy_last



if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpu", "-g", default=-1, type=int, help="GPU ID")
    
    args = parser.parse_args()
    
    xp = cuda.cupy if args.gpu >= 0 else np
    
    use_gpu = False
    if args.gpu >= 0:
        use_gpu = True
        cuda.check_cuda_available()
        cuda.get_device(args.gpu).use()
    

    #batchsize should be multiple of 15 for evaluate at 15t
    #voice batchsize:15 units : 50
    #img   batchsize:60 units : 200 over
    batchsize = 60
    n_epoch = 100
    lstm_n_units = 30

    #loding dataset
    data = convert.mfcc_convert()
    data2 = convert.mfcc_convert2(data)
    mfcc = {}
    mfcc['data'] = np.array(data2)
    mfcc['data'] = mfcc['data'].astype(np.float32)
    mfcc['data'] /= 255
    mfcc['target'] = convert.gen_target()
    mfcc['target'] = mfcc['target'].astype(np.int32)
    
    #concat mfcc,img
    
    #data 1800
    N_train = 1500
    x_train, x_test = np.split(mfcc['data'],   [N_train])
    y_train, y_test = np.split(mfcc['target'], [N_train])
    N_test = y_test.size
    
    component1 = AutoencoderComponent(117,80)
    component2 = AutoencoderComponent(80,60)
    component3 = AutoencoderComponent(60,lstm_n_units)
    LSTMcomponent = LSTMComponent(lstm_n_units,lstm_n_units,10)
    
    brica1.connect((component1,"output"),(component2,"input"))
    brica1.connect((component2,"output"),(component3,"input"))
    brica1.connect((component3,"output"),(LSTMcomponent,"input"))
    
    stacked_autoencoder = brica1.ComponentSet()
    
    stacked_autoencoder.add_component("component1",component1,1)
    stacked_autoencoder.add_component("component2",component2,2)
    stacked_autoencoder.add_component("component3",component3,3)
    stacked_autoencoder.add_component("LSTMcomponent",LSTMcomponent,4)
    
    stacked_autoencoder.make_in_port("input",117)
    stacked_autoencoder.make_in_port("target",1)
    stacked_autoencoder.make_in_port("state_c1",lstm_n_units)
    stacked_autoencoder.make_in_port("state_h1",lstm_n_units)
    stacked_autoencoder.make_in_port("state_c2",lstm_n_units)
    stacked_autoencoder.make_in_port("state_h2",lstm_n_units)
    stacked_autoencoder.make_out_port("output",10)
    stacked_autoencoder.make_out_port("loss1",1)
    stacked_autoencoder.make_out_port("loss2",1)
    stacked_autoencoder.make_out_port("loss3",1)
    stacked_autoencoder.make_out_port("loss4",1)
    stacked_autoencoder.make_out_port("accuracy",1)
    
    brica1.alias_in_port((stacked_autoencoder,"input"),(component1,"input"))
    brica1.alias_out_port((stacked_autoencoder,"output"),(LSTMcomponent,"output"))
    brica1.alias_out_port((stacked_autoencoder,"loss1"),(component1,"loss"))
    brica1.alias_out_port((stacked_autoencoder,"loss2"),(component2,"loss"))
    brica1.alias_out_port((stacked_autoencoder,"loss3"),(component3,"loss"))
    brica1.alias_out_port((stacked_autoencoder,"loss4"),(LSTMcomponent,"loss"))
    brica1.alias_out_port((stacked_autoencoder,"accuracy"),(LSTMcomponent,"accuracy"))
    brica1.alias_in_port((stacked_autoencoder,"target"),(LSTMcomponent,"target"))
   

    time = 0.0
    
    if use_gpu:
        stacked_autoencoder.to_gpu(stacked_autoencoder)

    l1_x_W = []
    l1_h_W = []
    l2_x_W = []
    l2_h_W = []
    l3_W = []

    y_array = []
    y_each = []
    t_array = []
        
    y_trainbackup = []
    t_trainbackup = []
    y_testbackup = []
    t_testbackup = []

    trainloss = []
    trainaccuracy = []
    trainaccuracylast = []

    testloss = []
    testaccuracy = []
    testaccuracylast = []

    for epoch in xrange(n_epoch):
        sum_loss1 = 0
        sum_loss2 = 0
        sum_loss3 = 0
        sum_loss4 = 0
        sum_accuracy = 0

        for batchnum in xrange(0 , N_train, batchsize):
            x_batch = xp.array(x_train[batchnum:batchnum+batchsize],dtype=np.float32)
            y_batch = xp.array(y_train[batchnum:batchnum+batchsize])

            if use_gpu:
                x_batch = cuda.to_gpu(x_batch)
                y_batch  = cuda.to_gpu(y_batch)
            
            stacked_autoencoder.get_in_port("input").buffer = x_batch
            stacked_autoencoder.get_in_port("target").buffer = y_batch
            stacked_autoencoder.get_in_port("state_c1").buffer = make_initial_state3(lstm_n_units)
            stacked_autoencoder.get_in_port("state_h1").buffer = make_initial_state3(lstm_n_units)
            stacked_autoencoder.get_in_port("state_c2").buffer = make_initial_state3(lstm_n_units)
            stacked_autoencoder.get_in_port("state_h2").buffer = make_initial_state3(lstm_n_units)
            
            stacked_autoencoder.input(time)
            stacked_autoencoder.fire()
            stacked_autoencoder.output(time+1.0)
            
            time += 1.0
            
            loss1 = stacked_autoencoder.get_out_port("loss1").buffer
            loss2 = stacked_autoencoder.get_out_port("loss2").buffer
            loss3 = stacked_autoencoder.get_out_port("loss3").buffer
            loss4 = stacked_autoencoder.get_out_port("loss4").buffer
            accuracy = stacked_autoencoder.get_out_port("accuracy").buffer

            sum_accuracy += accuracy.data * batchsize
            sum_loss += loss.data * batchsize
        
            sum_loss1 += loss1 * batchsize
            sum_loss2 += loss2 * batchsize
            sum_loss3 += loss3 * batchsize
            sum_loss4 += loss4 * batchsize
            sum_accuracy += sum_accuracy * batchsize
        
        mean_loss1 = sum_loss1 / N_train
        mean_loss2 = sum_loss2 / N_train
        mean_loss3 = sum_loss3 / N_train
        mean_loss4 = sum_loss4 / N_train
        mean_accuracy = sum_accuracy / N_train

        if use_gpu:
            mean_loss1 = cuda.to_cpu(mean_loss1)
            mean_loss2 = cuda.to_cpu(mean_loss2)
            mean_loss3 = cuda.to_cpu(mean_loss3)
            mean_loss4 = cuda.to_cpu(mean_loss4)
            mean_accuracy = cuda.to_cpu(mean_accuracy)

        print "Train Epoch  {} : loss1  {} : loss2  {} : loss3  {} : loss4  {} : Accuracy  {} ".format(epoch,mean_loss1,mean_loss2,mean_loss3,mean_loss4,mean_accuracy)

        sum_loss1 = 0
        sum_loss2 = 0
        sum_loss3 = 0
        sum_loss4 = 0
        sum_accuracy = 0

        for batchnum in xrange(0 , N_test, batchsize):
            x_batch = xp.array(x_test[batchnum:batchnum+batchsize])
            y_batch = xp.array(y_test[batchnum:batchnum+batchsize])
            
            if use_gpu:
                x_batch = cuda.to_gpu(x_batch)
                y_batch  = cuda.to_gpu(y_batch)

            stacked_autoencoder.get_in_port("input").buffer = x_batch
            stacked_autoencoder.get_in_port("target").buffer = y_batch
            stacked_autoencoder.get_in_port("state_c1").buffer = make_initial_state3(lstm_n_units)
            stacked_autoencoder.get_in_port("state_h1").buffer = make_initial_state3(lstm_n_units)
            stacked_autoencoder.get_in_port("state_c2").buffer = make_initial_state3(lstm_n_units)
            stacked_autoencoder.get_in_port("state_h2").buffer = make_initial_state3(lstm_n_units)

            stacked_autoencoder.input(time)
            stacked_autoencoder.fire()
            stacked_autoencoder.output(time+1.0)
            
            time += 1.0
            
            loss1 = stacked_autoencoder.get_out_port("loss1").buffer
            loss2 = stacked_autoencoder.get_out_port("loss2").buffer
            loss3 = stacked_autoencoder.get_out_port("loss3").buffer
            loss4 = stacked_autoencoder.get_out_port("loss4").buffer
            accuracy = stacked_autoencoder.get_out_port("accuracy").buffer
            
            sum_loss1 += loss1 * batchsize
            sum_loss2 += loss2 * batchsize
            sum_loss3 += loss3 * batchsize
            sum_loss4 += loss4 * batchsize
            sum_accuracy += sum_accuracy * batchsize
        
        mean_loss1 = sum_loss1 / N_test
        mean_loss2 = sum_loss2 / N_test
        mean_loss3 = sum_loss3 / N_test
        mean_loss4 = sum_loss4 / N_test
        mean_accuracy = sum_accuracy / N_test


        if use_gpu:
            mean_loss1 = cuda.to_cpu(mean_loss1)
            mean_loss2 = cuda.to_cpu(mean_loss2)
            mean_loss3 = cuda.to_cpu(mean_loss3)
            mean_loss4 = cuda.to_cpu(mean_loss4)
            mean_accuracy = cuda.to_cpu(mean_accuracy)


        print "Train Epoch  {} : loss1  {} : loss2  {} : loss3  {} : loss4  {} : Accuracy  {} ".format(epoch,mean_loss1,mean_loss2,mean_loss3,mean_loss4,mean_accuracy)


