import mock, keras

def custom(x): 
  return x # Replace this with your activation function.

model_json = open('config.json').read()

'''
Trying to run:

model_from_json(model_json, custom_objects={'custom': custom}

Raises:

Exception: Invalid activation function: one_to_five_star
'''

old_get = keras.activations.get
def patch_get(x): 
  return custom if x == 'custom' else old_get(x)
@mock.patch('keras.activations.get', patch_get)
def load():
  return model_from_json(model_json, custom_objects={'custom': custom}

model = load()

  


