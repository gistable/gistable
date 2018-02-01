import numpy as np
from keras.layers import Dense, Input
from keras.models import Model

x = Input((1,))
y = Dense(1, activation ='linear')(x)

m = Model(x,y)
m.compile(loss = 'mse', optimizer='sgd')
_x = np.linspace(1,2, num = 1e3)
m.fit(_x, 2*_x + 1, batch_size=1)

print m.get_weights()
