"""
When classifying upon a sequence usually we stack some LSTM returning sequences,
then one LSTM returning a point, then Dense with softmax activation.

Is it possible instead to give the last non-sequential LSTM a softmax activation?

The answer is yes.

In this example we have 3 sequential layers and one layer producing the final result.

The only difference is in the number of parameters of the last layer due to more
complex neurons in LSTM comprared to Dense.
"""

from keras.layers import Input, LSTM, Dense
from keras.models import Model

seq_length = 10
feature_count = 20
class_count = 2
rnn_width = 32

def classic_sequence_classifier():
  input = Input(shape=(seq_length, feature_count))
  x = LSTM(rnn_width, return_sequences=True)(input)
  x = LSTM(rnn_width, return_sequences=True)(x)
  x = LSTM(rnn_width)(x)
  x = Dense(class_count, activation='softmax')(x)
  return Model(input, x)

def proposed_sequence_classifier():
  input = Input(shape=(seq_length, feature_count))
  x = LSTM(rnn_width, return_sequences=True)(input)
  x = LSTM(rnn_width, return_sequences=True)(x)
  x = LSTM(rnn_width, return_sequences=True)(x)
  x = LSTM(class_count, activation='softmax')(x)
  return Model(input, x)

classic_model = classic_sequence_classifier()
proposed_model = proposed_sequence_classifier()

classic_model.summary()
# ____________________________________________________________________________________________________
# Layer (type)                     Output Shape          Param #     Connected to                     
# ====================================================================================================
# input_4 (InputLayer)             (None, 10, 20)        0                                            
# ____________________________________________________________________________________________________
# lstm_8 (LSTM)                    (None, 10, 32)        6784        input_4[0][0]                    
# ____________________________________________________________________________________________________
# lstm_9 (LSTM)                    (None, 10, 32)        8320        lstm_8[0][0]                     
# ____________________________________________________________________________________________________
# lstm_10 (LSTM)                   (None, 32)            8320        lstm_9[0][0]                     
# ____________________________________________________________________________________________________
# dense_2 (Dense)                  (None, 2)             66          lstm_10[0][0]                    
# ====================================================================================================
# Total params: 23490
# ____________________________________________________________________________________________________

proposed_model.summary()
# ____________________________________________________________________________________________________
# Layer (type)                     Output Shape          Param #     Connected to                     
# ====================================================================================================
# input_5 (InputLayer)             (None, 10, 20)        0                                            
# ____________________________________________________________________________________________________
# lstm_11 (LSTM)                   (None, 10, 32)        6784        input_5[0][0]                    
# ____________________________________________________________________________________________________
# lstm_12 (LSTM)                   (None, 10, 32)        8320        lstm_11[0][0]                    
# ____________________________________________________________________________________________________
# lstm_13 (LSTM)                   (None, 10, 32)        8320        lstm_12[0][0]                    
# ____________________________________________________________________________________________________
# lstm_14 (LSTM)                   (None, 2)             280         lstm_13[0][0]                    
# ====================================================================================================
# Total params: 23704
# ____________________________________________________________________________________________________