#!/usr/bin/env python
import tensorflow as tf
import numpy as np
from numpy import genfromtxt

# Build Example Data is CSV format, but use Iris data
from sklearn import datasets
from sklearn.model_selection import train_test_split
import sklearn
def buildDataFromIris():
    iris = datasets.load_iris()
    X_train, X_test, y_train, y_test = train_test_split(iris.data, iris.target, test_size=0.33, random_state=42)
    f=open('cs-training.csv','w')
    for i,j in enumerate(X_train):
        k=np.append(np.array(y_train[i]),j   )
        f.write(",".join([str(s) for s in k]) + '\n')
    f.close()
    f=open('cs-testing.csv','w')
    for i,j in enumerate(X_test):
        k=np.append(np.array(y_test[i]),j   )
        f.write(",".join([str(s) for s in k]) + '\n')
    f.close()


# Convert to one hot
def convertOneHot(data):
    y=np.array([int(i[0]) for i in data])
    y_onehot=[0]*len(y)
    for i,j in enumerate(y):
        y_onehot[i]=[0]*(y.max() + 1)
        y_onehot[i][j]=1
    return (y,y_onehot)


buildDataFromIris()


data = genfromtxt('cs-training.csv',delimiter=',')  # Training data
test_data = genfromtxt('cs-testing.csv',delimiter=',')  # Test data

x_train=np.array([ i[1::] for i in data])
y_train,y_train_onehot = convertOneHot(data)

x_test=np.array([ i[1::] for i in test_data])
y_test,y_test_onehot = convertOneHot(test_data)


#  A number of features, 4 in this example
#  B = 3 species of Iris (setosa, virginica and versicolor)
A=data.shape[1]-1 # Number of features, Note first is y
B=len(y_train_onehot[0])
tf_in = tf.placeholder("float", [None, A]) # Features
tf_weight = tf.Variable(tf.zeros([A,B]))
tf_bias = tf.Variable(tf.zeros([B]))
tf_softmax = tf.nn.softmax(tf.matmul(tf_in,tf_weight) + tf_bias)




# Training via backpropagation
tf_softmax_correct = tf.placeholder("float", [None,B])
tf_cross_entropy = -tf.reduce_sum(tf_softmax_correct*tf.log(tf_softmax))

# Train using tf.train.GradientDescentOptimizer
tf_train_step = tf.train.GradientDescentOptimizer(0.01).minimize(tf_cross_entropy)

# Add accuracy checking nodes
tf_correct_prediction = tf.equal(tf.argmax(tf_softmax,1), tf.argmax(tf_softmax_correct,1))
tf_accuracy = tf.reduce_mean(tf.cast(tf_correct_prediction, "float"))



# Recreate logging dir
import shutil, os, sys
TMPDir='./tenIrisSave'
try:
 shutil.rmtree(TMPDir)
except:
 print "Tmp Dir did not exist"
os.mkdir(TMPDir, 0755 )

# Initialize and run
sess = tf.Session()
#sess = tf.InteractiveSession()
init = tf.initialize_all_variables()
sess.run(init)

# Build the summary operation based on the TF collection of Summaries.
tf.train.write_graph(sess.graph_def, TMPDir + '/logsd','graph.pbtxt')

#acc = tf.scalar_summary("Accuracy:", tf_accuracy)
tf.scalar_summary("Accuracy:", tf_accuracy)
tf.histogram_summary('weights', tf_weight)
tf.histogram_summary('bias', tf_bias)
tf.histogram_summary('softmax', tf_softmax)
tf.histogram_summary('accuracy', tf_accuracy)


summary_op = tf.merge_all_summaries()
#summary_writer = tf.train.SummaryWriter('./tenIrisSave/logs',graph_def=sess.graph_def)
summary_writer = tf.train.SummaryWriter(TMPDir + '/logs',sess.graph_def)

# This will not work. You need the full path.                                        
# tensorboard --logdir=./tenIrisSave/   # BAD!
# tensorboard --logdir=$(pwd)/tenIrisSave/  # Good!

# This is for saving all our work
saver = tf.train.Saver([tf_weight,tf_bias])

print("...")
# Run the training

k=[]
saved=0
for i in range(100):
    sess.run(tf_train_step, feed_dict={tf_in: x_train, tf_softmax_correct: y_train_onehot})
# Print accuracy
    result = sess.run(tf_accuracy, feed_dict={tf_in: x_test, tf_softmax_correct: y_test_onehot})
    print "Run {},{}".format(i,result)
    k.append(result)
    summary_str = sess.run(summary_op,feed_dict={tf_in: x_test, tf_softmax_correct: y_test_onehot})
    summary_writer.add_summary(summary_str, i)
    if result == 1 and saved == 0:
        saved=1
        print "saving"
        saver.save(sess,"./tenIrisSave/saveOne")


k=np.array(k)
print(np.where(k==k.max()))
print "Max: {}".format(k.max())

print "\nTo see the output, run the following:"
print "tensorboard --logdir=$(pwd)/tenIrisSave"






