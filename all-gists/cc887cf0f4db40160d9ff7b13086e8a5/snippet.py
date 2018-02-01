def _phase_shift(I, r):
    bsize, a, b, c = I.get_shape().as_list()
    X = tf.reshape(I, (bsize, a, b, r, r))
    X = tf.transpose(X, (0, 1, 2, 4, 3))  # bsize, a, b, 1, 1
    X = tf.split(1, a, X)  # a, [bsize, b, r, r]
    X = tf.concat(2, [tf.squeeze(x, [1]) for x in X])  # bsize, b, a*r, r
    X = tf.split(1, b, X)  # b, [bsize, a*r, r]
    X = tf.concat(2, [tf.squeeze(x, [1]) for x in X])  # bsize, a*r, b*r
    return tf.reshape(X, (bsize, a*r, b*r, 1))


def PS(X, r, color=False):
    if color:
        Xc = tf.split(3, 3, X)
        X = tf.concat(3, [_phase_shift(x, r) for x in Xc])
    else:
        X = _phase_shift(X, r)
    return X

%pylab inline
import tensorflow as tf

# Feature map with shape [1, 8, 8, 4] with each feature map i having value i
x = np.ones((1, 8, 8, 4)) * np.arange(4)[None, None, None, :]
# Convert to a [1, 16, 16, 1] Tensor
y = tf.depth_to_space(tf.constant(x), 2)

sess = tf.InteractiveSession()
out = sess.run(y)

# Plot results
figure(figsize=(8, 3))
gs = GridSpec(2, 4, width_ratios=[1, 1, 2, 2])
for i in xrange(4):
  subplot(gs[i//2, i%2])
  imshow(x[:, :, :, i].squeeze(), cmap=cm.jet, vmin=0, vmax=4, interpolation='nearest'); 
  # Add ticks at pixels, annoyingly have to offset by 0.5 to line up with pixels
  xticks(0.5 + np.arange(8)); yticks(0.5 + np.arange(8));
  gca().set_xticklabels([]); gca().set_yticklabels([]);
  title('feature %d'%i)
  
  
subplot(gs[:, 2])
print x.shape
out_ps = sess.run(PS(tf.constant(x), 2))
imshow(out_ps.squeeze(), cmap=cm.jet, vmin=0, vmax=4, interpolation='nearest'); 
axis('off')
title('phase shift')

subplot(gs[:, 3])
imshow(out.squeeze(), cmap=cm.jet, vmin=0, vmax=4, interpolation='nearest'); 
axis('off')
title('depth_to_space')


gcf().tight_layout()