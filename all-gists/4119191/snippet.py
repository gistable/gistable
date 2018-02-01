import theano
import theano.tensor as T
import numpy as np
import cPickle as pickle
#theano.config.compute_test_value = 'warn'

class Meta(object):

    def __init__(self):

        self.activation = T.nnet.sigmoid
        self.rng = np.random.RandomState(1234)

        vocab_size = 25000
        self.n_in = 100
        self.n_hidden = 100

        """
        Initialising weights for variables
        """
        r = np.sqrt(6. / (self.n_in + self.n_hidden))
        if self.activation == T.nnet.sigmoid:
            r *= 4

        self.We   = theano.shared(value=np.asarray(self.rng.uniform(low=-r,high=r,size=(vocab_size, self.n_in)), dtype=theano.config.floatX),name='We')
        self.W12  = theano.shared(value=np.asarray(self.rng.uniform(low=-r,high=r,size=(2 * self.n_in, self.n_hidden)), dtype=theano.config.floatX),name='W12')
        self.W34  = theano.shared(value=np.asarray(self.rng.uniform(low=-r,high=r,size=(self.n_hidden, 2 * self.n_in)), dtype=theano.config.floatX),name='W34')
        self.b1   = theano.shared(value=np.zeros((self.n_hidden,),dtype=theano.config.floatX),name='b1')
        self.b23  = theano.shared(value=np.zeros((2 * self.n_in,),dtype=theano.config.floatX),name='b23')

        self.W12grad  = theano.shared(value=np.zeros((2 * self.n_in, self.n_hidden), dtype=theano.config.floatX),name='W12grad')
        self.W34grad  = theano.shared(value=np.zeros((self.n_hidden, 2 * self.n_in), dtype=theano.config.floatX),name='W34grad')
        self.b1grad   = theano.shared(value=np.zeros((self.n_hidden,),dtype=theano.config.floatX),name='b1grad')
        self.b23grad  = theano.shared(value=np.zeros((2 * self.n_in,),dtype=theano.config.floatX),name='b23grad')

    def resetGradients(self):

        self.W12grad  = theano.shared(value=np.zeros((2 * self.n_in, self.n_hidden), dtype=theano.config.floatX),name='W12grad')
        self.W34grad  = theano.shared(value=np.zeros((self.n_hidden, 2 * self.n_in), dtype=theano.config.floatX),name='W34grad')
        self.b1grad   = theano.shared(value=np.zeros((self.n_hidden,),dtype=theano.config.floatX),name='b1grad')
        self.b23grad  = theano.shared(value=np.zeros((2 * self.n_in,),dtype=theano.config.floatX),name='b23grad')

    def getTreeDict(self,sent_length):
        ae = {}
        cb = {}

        counter = 0

        for i in xrange(0,sent_length):
            cb[(i,1)] = counter
            counter += 1

        for p_length in xrange(2,sent_length+1):
            for p_left in xrange(0,sent_length - p_length + 1):
                for p_split in xrange(p_left+1, p_left+p_length):
                    ae[(p_left,p_length,p_split)] = counter
                    counter += 1
                cb[(p_left,p_length)] = counter
                counter += 1

        return counter,ae,cb

    def sharedForwardProp(self,data,sent_length,ae,cb):

        W = self.Winternal
        # Put sentence data into the bottom cb layer
        for i in xrange(0,sent_length):
            self.initAE(cb[(i,1)],data[i].eval())

        # propagate everything up
        for p_length in xrange(2,sent_length+1):
            for p_left in xrange(0,sent_length - p_length + 1):
                comb_children = []
                for p_split in xrange(p_left+1, p_left+p_length):
                    """
                    Forward Propagate autoencoders
                    """
                    y = self.get_shr_enc( ae[(p_left,p_length,p_split)], cb[(p_left,p_split-p_left)], cb[(p_split,p_length+p_left-p_split)])
                    comb_children.append(y)
                """
                Forward Propagate combinator
                """
                self.set_combined( cb[(p_left,p_length)], np.vstack(comb_children))

    def backPropAndCost(self,sent_length,ae,cb):

        # CrossEntropy Error at the label level (tree root)
        self.deltas[cb[(0,sent_length)]] = 0

        for p_length in xrange(sent_length,1,-1):
            for p_left in xrange(sent_length - p_length,-1,-1):
                """
                nothing to do here. my children can pick up my delta easily
                \eta_k &= \sum_{p \in \text{Downstream}} w_{pk} \delta_{p} \\
                
                child_delta = weight * (own_delta)
                as weights are shared, we can already multiply them inside the delta matrix
                """
                for p_split in xrange(p_left+p_length-1,p_left,-1):

                    # \delta_{ks} &= o_{ks} (1 - o_{ks}) \left(\eta_k + \delta_{\text{rec}} w_{\text{rec}}\right) \\

                    # Get eta from parent combinator
                    delta_tree = self.deltas[cb[(p_left,p_length)]]

                    # Add reconstruction error
                    # \delta_{\text{rec}} &= - (r_\text{rec} - o_\text{rec}) (1 - o_\text{rec}) o_\text{rec} * ?
                    # reconstruction_delta = (my_input - my_reconstruction) (-rec) (1-rec)
                    my_input = T.concatenate([self.Winternal[cb[(p_left,p_split-p_left)],:],self.Winternal[cb[(p_split,p_left+p_length-p_split)],:]],axis=0)
                    my_reconstruction = T.dot(self.Winternal[ae[(p_left,p_length,p_split)],:],self.W34) + self.b23
                    reconstruction_error = (my_input - my_reconstruction)
                    self.error += T.sum(T.sqr(reconstruction_error))
                    reconstruction_delta = reconstruction_error * (- my_reconstruction) * (1 - my_reconstruction)

                    self.W34grad += T.outer(self.Winternal[ae[(p_left,p_length,p_split)]],reconstruction_delta)
                    self.b23grad += reconstruction_delta

                    reconstruction_error = T.sum(self.W34 * reconstruction_delta,axis=1)

                    delta_combined = delta_tree + reconstruction_error

                    # Now, multiply with o_ks (1 - o_ks) [ which is my embedding ]
                    delta_combined *= np.multiply((1 - self.Winternal[ae[(p_left,p_length,p_split)]]),self.Winternal[ae[(p_left,p_length,p_split)]]) #.eval()
                    
                    z = T.outer(delta_combined,my_input)
                    self.W12grad += T.outer(my_input,delta_combined)
                    self.b1grad += delta_combined
                    
                    delta_p = np.sum(delta_combined * self.W12,axis=1)
                    #print delta_p.eval().shape

                    ## give delta to my specific children: [0,3,1] gives to [0,1] and [1,2]. 
                    self.deltas[cb[(p_left,p_split-p_left)]] += delta_p[:(self.n_hidden)].eval()
                    self.deltas[cb[(p_split,p_left+p_length-p_split)]] += delta_p[(self.n_hidden):].eval()
                   
                    print "."



    def run(self):

            """
            Loading Data
            """
            print "loading data ..."
            data_shape = 100 * 50 # sentences x words/sentence
            data = theano.shared(value=np.zeros(data_shape, dtype=np.int32))

            data_np = np.zeros(data_shape, dtype=np.int32)
            len_np = np.zeros(100, dtype=np.int32)
            data_loc = "../../data/movies"
            f = open("%s/data.pkl"%data_loc)
            data_list, classes = pickle.load(f), pickle.load(f)
            for sent in xrange(0,99):
                for word in xrange(0,min(50,len(data_list[sent]))):
                    data_np[sent*50+word] = data_list[sent][word]
                    len_np[sent] = min(50,len(data_list[sent]))
            data.set_value(np.concatenate([x.ravel() for x in (data_np)]))
            data = data.reshape((100,50))
            print "... done"

            m = 0
            for sentence in xrange(0,45):
                counter,a,c = self.getTreeDict(len_np[sentence])
                if counter > m: m = counter

            print "creating data ..."
            self.Winternal = theano.shared(value=np.zeros((m,self.n_hidden),dtype=theano.config.floatX),borrow=True)
            self.deltas = np.zeros((m,self.n_hidden),dtype=theano.config.floatX)
            print ".. done"

            self.A = T.vector()
            self.B = T.vector()
            self.b = T.lscalar()
            self.a = T.lscalar()
            self.y = T.scalar(dtype='int32')
            self.x = T.scalar(dtype='int32')

            self.C = T.matrix()
            self.cb_shared_combinator = T.mean(self.C,axis=0)
            #self.get_shr_comb       = theano.function([self.C],self.cb_shared_combinator)

            self.set_combined = theano.function([self.a,self.C], [],
                                            updates={self.Winternal: T.set_subtensor(self.Winternal[self.a],self.cb_shared_combinator)})

            self.cb_shared_encoding = self.activation(T.dot(T.concatenate([self.A,self.B]),self.W12) + self.b1)

            self.get_shr_enc    = theano.function([self.a, self.x,self.y],self.cb_shared_encoding,on_unused_input='warn',
                                            givens={self.A: self.Winternal[self.x,:],
                                                    self.B: self.Winternal[self.y,:]},
                                            updates={self.Winternal: T.set_subtensor(self.Winternal[self.a,:],self.cb_shared_encoding)})


            self.initAE = theano.function([self.a,self.b], [], updates={self.Winternal: T.set_subtensor(self.Winternal[self.a,:], self.We[self.b])}) 

            for sentence in xrange(0,45):
                print "Length %d" % len_np[sentence]
                counter,a,c = self.getTreeDict(len_np[sentence])
                print "Counter %d" % counter
                print "forward prop: learning outputs and encoding %d" % sentence
                self.sharedForwardProp(data[sentence],len_np[sentence],a,c)
                print "backprop: accumulating deltas and error"
                self.resetGradients()
                self.error = 0
                self.backPropAndCost(len_np[sentence],a,c)
                print "Errors", self.error.eval()
                print "Updating W12"
                print self.W12.eval().shape
                print self.W12grad.eval().shape
                self.W12 = self.W12 - 0.1 * self.W12grad
                print self.W12.eval().shape
                print "done"
                self.W34 = self.W34 - 0.1 * self.W34grad
                self.b1 = self.b1 - 0.1 * self.b1grad
                self.b23 = self.b23 - 0.1 * self.b23grad

                self.resetGradients()
                self.error = 0
                self.backPropAndCost(len_np[sentence],a,c)
                print "Errors", self.error.eval()
                


meta = Meta()
meta.run()