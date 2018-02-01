"""
Here is a dice loss for keras which is smoothed to approximate a linear (L1) loss.
It ranges from 1 to 0 (no error), and returns results similar to binary crossentropy
"""

# define custom loss and metric functions 

from keras import backend as K

def dice_coef(y_true, y_pred, smooth=1):
    """
    Dice = (2*|X & Y|)/ (|X|+ |Y|)
         =  2*sum(|A*B|)/(sum(A^2)+sum(B^2))
    ref: https://arxiv.org/pdf/1606.04797v1.pdf
    """
    intersection = K.sum(K.abs(y_true * y_pred), axis=-1)
    return (2. * intersection + smooth) / (K.sum(K.square(y_true),-1) + K.sum(K.square(y_pred),-1) + smooth)

def dice_coef_loss(y_true, y_pred):
    return 1-dice_coef(y_true, y_pred)
    
    
# Test
y_true = np.array([[0,0,1,0],[0,0,1,0],[0,0,1.,0.]])
y_pred = np.array([[0,0,0.9,0],[0,0,0.1,0],[1,1,0.1,1.]])

r = dice_coef_loss(
    K.theano.shared(y_true),
    K.theano.shared(y_pred),
).eval()
print('dice_coef_loss',r)


r = keras.objectives.binary_crossentropy(
    K.theano.shared(y_true),
    K.theano.shared(y_pred),
).eval()
print('binary_crossentropy',r)
print('binary_crossentropy_scaled',r/r.max())
# TYPE                 |Almost_right |half right |all_wrong
# dice_coef_loss      [ 0.00355872    0.40298507  0.76047904]
# binary_crossentropy [ 0.0263402     0.57564635  12.53243514]
