"""
Dist-Keras Spark ML Pipelines
Copyright (C) 2017 Principal Academy Inc.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.
"""


from keras.layers import Activation, Dense, Dropout
from distkeras import predictors, trainers
from keras.optimizers import SGD
from pyspark import ml


class DistKeras(ml.Estimator):
    
    def __init__(self, *args, **kwargs):
        self.__trainer_klass = args[0]
        self.__trainer_params = args[1]
        self.__build_trainer(**kwargs)
        super(DistKeras, self).__init__()
    
    @classmethod
    def __build_keras_model(klass, *args, **kwargs):
        loss = kwargs['loss']
        metrics = kwargs['metrics']
        layer_dims = kwargs['layer_dims']
        hidden_activation, output_activation = kwargs['activations']
        dropout_rate = kwargs['dropout_rate']
        reg_strength = kwargs['reg_strength']
        reg_decay = kwargs['reg_decay']
        keras_model = Sequential()
        for idx in range(1, len(layer_dims)-1, 1):
            keras_model.add(Dense(layer_dims[idx],
                                  input_dim=layer_dims[idx-1],
                                  bias_initializer='glorot_normal',
                                  kernel_initializer='glorot_normal',
                                  kernel_regularizer=l1_l2(reg_strength)))
            keras_model.add(Activation(hidden_activation))
            keras_model.add(Dropout(dropout_rate))
            reg_strength *= reg_decay
        keras_model.add(Dense(layer_dims[-1],
                              input_dim=layer_dims[-2],
                              bias_initializer='glorot_uniform',
                              kernel_initializer='glorot_uniform',
                              kernel_regularizer=l1_l2(reg_strength)))
        keras_model.add(Activation(output_activation))
        return keras_model
    
    def __build_trainer(self, *args, **kwargs):
        loss = kwargs['loss']
        learning_rate = kwargs['learning_rate']
        lr_decay = kwargs['lr_decay']
        keras_optimizer = SGD(learning_rate, decay=lr_decay)
        keras_model = DistKeras.__build_keras_model(**kwargs)
        self._trainer = self.__trainer_klass(keras_model, keras_optimizer, loss, **self.__trainer_params)
    
    def _fit(self, *args, **kwargs):
        data_frame = args[0]
        if kwargs is not None:
            self.__build_trainer(**kwargs)
        keras_model = self._trainer.train(data_frame)
        return DistKerasModel(keras_model)


class DistKerasModel(ml.Model):
    
    def __init__(self, *args, **kwargs):
        keras_model = args[0]
        self._predictor = predictors.ModelPredictor(keras_model)
        super(DistKerasModel, self).__init__()
    
    def _transform(self, *args, **kwargs):
        data_frame = args[0]
        return self._predictor.predict(data_frame)

