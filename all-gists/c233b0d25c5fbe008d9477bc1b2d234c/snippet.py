import tensorflow as tf
import numpy as np

def smoothed_metric_loss(input_tensor, name='smoothed_triplet_loss', margin=1):
    '''
    input_tensor: require a tensor with predefined dimensions (No None dimension)
                  Every two consecutive vectors must be a positive pair. There
                  should not be more than one pair from each class.
    '''
    with tf.variable_scope(name):
        # Song et al., Deep Metric Learning via Lifted Structured Feature Embedding
        # Define feature X \in \mathbb{R}^{N \times C}
        X = input_tensor
        m = margin

        # Compute the pairwise distance
        Xe = tf.expand_dims(X, 1)
        Dsq = tf.reduce_sum(tf.square(Xe - tf.transpose(Xe, (1, 0, 2))), 2, keep_dims=False)
        D = tf.sqrt(Dsq + 1e-8)
        expmD = tf.exp(m - D)

        # Compute the loss
        # Assume that the input data is aligned in a way that two consecutive data form a pair
        batch_size, _ = X.get_shape().as_list()

        # L_{ij} = \log (\sum_{i, k} exp\{m - D_{ik}\} + \sum_{j, l} exp\{m - D_{jl}\}) + D_{ij}
        # L = \frac{1}{2|P|}\sum_{(i,j)\in P} \max(0, J_{i,j})^2
        J_all = []
        for pair_ind in range(batch_size // 2):
            i = pair_ind * 2
            j = i + 1
            ind_rest = np.hstack([np.arange(0, pair_ind * 2),
                                  np.arange(pair_ind * 2 + 2, batch_size)])

            inds = [[i, k] for k in ind_rest]
            inds.extend([[j, l] for l in ind_rest])
            J_ij = tf.log(tf.reduce_sum(tf.gather_nd(expmD, inds))) + tf.gather_nd(D, [[i, j]])
            J_all.append(J_ij)

        J_all = tf.convert_to_tensor(J_all)
        loss = tf.divide(tf.reduce_mean(tf.square(tf.maximum(J_all, 0))), 2.0, name='metric_loss')
        tf.add_to_collection(tf.GraphKeys.LOSSES, loss)
    return loss