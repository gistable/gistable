# required tensorflow 0.12
# required gensim 0.13.3+ for new api model.wv.index2word or just use model.index2word

from gensim.models import Word2Vec
import tensorflow as tf
from tensorflow.contrib.tensorboard.plugins import projector

# loading your gensim
model = Word2Vec.load("YOUR-MODEL")

# project part of vocab, 10K of 300 dimension
w2v_10K = np.zeros((10000,300))
with open("./projector/prefix_metadata.tsv", 'w+') as file_metadata:
    for i,word in enumerate(model.wv.index2word[:10000]):
        w2v_10K[i] = model[word]
        file_metadata.write(word.encode('utf-8') + '\n')
        

# define the model without training
sess = tf.InteractiveSession()

with tf.device("/cpu:0"):
    embedding = tf.Variable(w2v_10K, trainable=False, name='prefix_embedding')

tf.global_variables_initializer().run()

saver = tf.train.Saver()
writer = tf.summary.FileWriter('./projector', sess.graph)

# adding into projector
config = projector.ProjectorConfig()
embed= config.embeddings.add()
embed.tensor_name = 'fs_embedding:0'
embed.metadata_path = './projector/prefix_metadata.tsv'

# Specify the width and height of a single thumbnail.
projector.visualize_embeddings(writer, config)

saver.save(sess, './projector/prefix_model.ckpt', global_step=10000)

# open tensorboard with logdir, check localhost:6006 for viewing your embedding.
# tensorboard --logdir="./projector/"
