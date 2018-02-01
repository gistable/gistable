import graphlab as gl

# Load the data
train = gl.SFrame.read_csv('data/train.csv')
test = gl.SFrame.read_csv('data/test.csv')
sample = gl.SFrame.read_csv('data/sampleSubmission.csv')

del train['id']

# Train a model
m = gl.boosted_trees_classifier.create(train, target='target',
                                       max_iterations=50)

# Make submission
preds = m.predict_topk(test, output_type='probability', k=9)
preds['id'] = preds['id'].astype(int) + 1
preds = preds.unstack(['class', 'probability'], 'probs').unpack('probs', '')
preds = preds.sort('id')

assert sample.num_rows() == preds.num_rows()
