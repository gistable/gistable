# a short implementation of arow in theano

def arow(params, loss, lbda1, lbda2):
   sigma = [theano.shared(value=np.ones(p.value.shape)) for p in params]
   gl = [T.grad(cost=loss, wrt=p) for p in params]
   ups = {}
   for i in xrange(len(params)):
       ups[params[i]] = params[i] - lbda1*gl[i]/sigma[i]
       ups[sigma[i]] = sigma[i] + lbda2*gl[i]*gl[i]
   return ups