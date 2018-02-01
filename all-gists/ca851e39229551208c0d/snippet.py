"""
bitmap utils and much of the ctc code modified
From Shawn Tan, Rakesh and Mohammad Pezeshki
"""
# Author: Kyle Kastner
# License: BSD 3-clause
from theano import tensor
from scipy import linalg
import theano
import numpy as np
import matplotlib.pyplot as plt

eps = 1E-12

characters = np.array([
    0x0,
    0x808080800080000,
    0x2828000000000000,
    0x287C287C280000,
    0x81E281C0A3C0800,
    0x6094681629060000,
    0x1C20201926190000,
    0x808000000000000,
    0x810202010080000,
    0x1008040408100000,
    0x2A1C3E1C2A000000,
    0x8083E08080000,
    0x81000,
    0x3C00000000,
    0x80000,
    0x204081020400000,
    0x1824424224180000,
    0x8180808081C0000,
    0x3C420418207E0000,
    0x3C420418423C0000,
    0x81828487C080000,
    0x7E407C02423C0000,
    0x3C407C42423C0000,
    0x7E04081020400000,
    0x3C423C42423C0000,
    0x3C42423E023C0000,
    0x80000080000,
    0x80000081000,
    0x6186018060000,
    0x7E007E000000,
    0x60180618600000,
    0x3844041800100000,
    0x3C449C945C201C,
    0x1818243C42420000,
    0x7844784444780000,
    0x3844808044380000,
    0x7844444444780000,
    0x7C407840407C0000,
    0x7C40784040400000,
    0x3844809C44380000,
    0x42427E4242420000,
    0x3E080808083E0000,
    0x1C04040444380000,
    0x4448507048440000,
    0x40404040407E0000,
    0x4163554941410000,
    0x4262524A46420000,
    0x1C222222221C0000,
    0x7844784040400000,
    0x1C222222221C0200,
    0x7844785048440000,
    0x1C22100C221C0000,
    0x7F08080808080000,
    0x42424242423C0000,
    0x8142422424180000,
    0x4141495563410000,
    0x4224181824420000,
    0x4122140808080000,
    0x7E040810207E0000,
    0x3820202020380000,
    0x4020100804020000,
    0x3808080808380000,
    0x1028000000000000,
    0x7E0000,
    0x1008000000000000,
    0x3C023E463A0000,
    0x40407C42625C0000,
    0x1C20201C0000,
    0x2023E42463A0000,
    0x3C427E403C0000,
    0x18103810100000,
    0x344C44340438,
    0x2020382424240000,
    0x800080808080000,
    0x800180808080870,
    0x20202428302C0000,
    0x1010101010180000,
    0x665A42420000,
    0x2E3222220000,
    0x3C42423C0000,
    0x5C62427C4040,
    0x3A46423E0202,
    0x2C3220200000,
    0x1C201804380000,
    0x103C1010180000,
    0x2222261A0000,
    0x424224180000,
    0x81815A660000,
    0x422418660000,
    0x422214081060,
    0x3C08103C0000,
    0x1C103030101C0000,
    0x808080808080800,
    0x38080C0C08380000,
    0x324C000000,
], dtype=np.uint64)

bitmap = np.unpackbits(characters.view(np.uint8)).reshape(characters.shape[0],
                                                          8, 8)
bitmap = bitmap[:, ::-1, :]

chars = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
mapping = {c: i for i, c in enumerate(chars)}


def string_to_image(string):
    return np.hstack(np.array([bitmap[mapping[c]] for c in string])).T[:, ::-1]


def string_to_index(string):
    return np.asarray([mapping[c] for c in string])


def recurrence_relation(y, y_mask):
    # with blank symbol of -1 this falls back to the recurrence that fails
    # with repeating symbols!
    blank_symbol = -1
    n_y = y.shape[0]
    blanks = tensor.zeros((2, y.shape[1])) + blank_symbol
    ybb = tensor.concatenate((y, blanks), axis=0).T
    sec_diag = (tensor.neq(ybb[:, :-2], ybb[:, 2:]) *
                tensor.eq(ybb[:, 1:-1], blank_symbol) *
                y_mask.T)

    # r1: LxL
    # r2: LxL
    # r3: LxLxB
    r2 = tensor.eye(n_y, k=1)
    r3 = (tensor.eye(n_y, k=2).dimshuffle(0, 1, 'x') *
          sec_diag.dimshuffle(1, 'x', 0))
    return r2, r3


def _epslog(x):
    return tensor.cast(tensor.log(tensor.clip(x, 1E-12, 1E12)),
                       theano.config.floatX)


def _log_add(a, b):
    max_ = tensor.maximum(a, b)
    return (max_ + tensor.log1p(tensor.exp(a + b - 2 * max_)))


def _log_dot_matrix(x, z):
    inf = 1E12
    log_dot = tensor.dot(x, z)
    zeros_to_minus_inf = (z.max(axis=0) - 1) * inf
    return log_dot + zeros_to_minus_inf


def _log_dot_tensor(x, z):
    inf = 1E12
    log_dot = (x.dimshuffle(1, 'x', 0) * z).sum(axis=0).T
    zeros_to_minus_inf = (z.max(axis=0) - 1) * inf
    return log_dot + zeros_to_minus_inf.T


def class_batch_to_labeling_batch(y, y_hat, y_hat_mask):
    # ??
    y_hat = y_hat.dimshuffle(0, 2, 1)
    y_hat = y_hat * y_hat_mask.dimshuffle(0, 'x', 1)
    batch_size = y_hat.shape[2]
    res = y_hat[:, y.astype('int32'), tensor.arange(batch_size)]
    return res


def log_path_probs(y, y_mask, y_hat, y_hat_mask):
    pred_y = class_batch_to_labeling_batch(y, y_hat, y_hat_mask)
    r2, r3 = recurrence_relation(y, y_mask)

    def step(log_p_curr, log_p_prev):
        p1 = log_p_prev
        p2 = _log_dot_matrix(p1, r2)
        p3 = _log_dot_tensor(p1, r3)
        p123 = _log_add(p3, _log_add(p1, p2))

        return (log_p_curr.T +
                p123 +
                _epslog(y_mask.T))

    log_probabilities, _ = theano.scan(
        step,
        sequences=[_epslog(pred_y)],
        outputs_info=[_epslog(tensor.eye(y.shape[0])[0] *
                              tensor.ones(y.T.shape))])
    return log_probabilities


def log_ctc_cost(y, y_mask, y_hat, y_hat_mask):
    y_hat_mask_len = tensor.sum(y_hat_mask, axis=0, dtype='int32')
    y_mask_len = tensor.sum(y_mask, axis=0, dtype='int32')
    log_probs = log_path_probs(y, y_mask, y_hat, y_hat_mask)
    batch_size = log_probs.shape[1]
    labels_prob = _log_add(
        log_probs[y_hat_mask_len - 1, tensor.arange(batch_size),
                  y_mask_len - 1],
        log_probs[y_hat_mask_len - 1, tensor.arange(batch_size),
                  y_mask_len - 2])
    avg_cost = tensor.mean(-labels_prob)
    return avg_cost


def as_shared(arr, name=None):
    if type(arr) in [float, int]:
        if name is not None:
            return theano.shared(np.cast[theano.config.floatX](arr))
        else:
            return theano.shared(np.cast[theano.config.floatX](arr), name=name)
    if name is not None:
        return theano.shared(value=arr, borrow=True)
    else:
        return theano.shared(value=arr, name=name, borrow=True)


def np_zeros(shape):
    """ Builds a numpy variable filled with zeros """
    return np.zeros(shape).astype(theano.config.floatX)


def np_ones(shape):
    """ Builds a numpy variable filled with zeros """
    return np.ones(shape).astype(theano.config.floatX)


def np_rand(shape, random_state):
    # Make sure bounds aren't the same
    return random_state.uniform(low=-0.08, high=0.08, size=shape).astype(
        theano.config.floatX)


def np_randn(shape, random_state):
    """ Builds a numpy variable filled with random normal values """
    return (0.01 * random_state.randn(*shape)).astype(theano.config.floatX)


def np_tanh_fan(shape, random_state):
    # The . after the 6 is critical! shape has dtype int...
    bound = np.sqrt(6. / np.sum(shape))
    return random_state.uniform(low=-bound, high=bound,
                                size=shape).astype(theano.config.floatX)


def np_sigmoid_fan(shape, random_state):
    return 4 * np_tanh_fan(shape, random_state)


def np_ortho(shape, random_state):
    """ Builds a theano variable filled with orthonormal random values """
    g = random_state.randn(*shape)
    o_g = linalg.svd(g)[0]
    return o_g.astype(theano.config.floatX)


def build_tanh_rnn(hidden_input, mask_input, W_hidden_hidden, initial_hidden):
    def step(x_t, m_t, h_tm1, U):
        h_ti = tensor.tanh(x_t + tensor.dot(h_tm1, U))
        h_t = m_t[:, None] * h_ti + (1 - m_t)[:, None] * h_tm1
        return h_t

    h, updates = theano.scan(step,
                             sequences=[hidden_input, mask_input],
                             outputs_info=[initial_hidden],
                             non_sequences=[W_hidden_hidden])
    return h


def build_model(X, X_mask, minibatch_size, input_size, hidden_size,
                output_size):
    random_state = np.random.RandomState(1999)
    W_input_hidden = as_shared(np_tanh_fan((input_size, hidden_size),
                                           random_state))
    W_hidden_hidden = as_shared(np_ortho((hidden_size, hidden_size),
                                         random_state))
    W_hidden_output = as_shared(np_tanh_fan((hidden_size, output_size),
                                            random_state))
    initial_hidden = as_shared(np_zeros((minibatch_size, hidden_size)))
    b_hidden = as_shared(np_zeros((hidden_size,)))
    b_output = as_shared(np_zeros((output_size,)))
    hidden = build_tanh_rnn(tensor.dot(X, W_input_hidden) + b_hidden, X_mask,
                            W_hidden_hidden, initial_hidden)
    hidden_proj = tensor.dot(hidden, W_hidden_output) + b_output
    hidden_proj_shapes = hidden_proj.shape
    hidden_proj = hidden_proj.reshape((
        hidden_proj_shapes[0] * hidden_proj_shapes[1], hidden_proj_shapes[2]))
    predict = tensor.nnet.softmax(hidden_proj).reshape(hidden_proj_shapes)
    params = [W_input_hidden, W_hidden_hidden, W_hidden_output, initial_hidden,
              b_output]
    return X, predict, params


def theano_label_seq(y, y_mask):
    blank_symbol = -1
    # for y
    y_extended = y.T.dimshuffle(0, 1, 'x')
    blanks = tensor.zeros_like(y_extended) + blank_symbol
    concat = tensor.concatenate([y_extended, blanks], axis=2)
    res = concat.reshape((concat.shape[0],
                          concat.shape[1] * concat.shape[2])).T
    beginning_blanks = tensor.zeros((1, res.shape[1])) + blank_symbol
    blanked_y = tensor.concatenate([beginning_blanks, res], axis=0)

    y_mask_extended = y_mask.T.dimshuffle(0, 1, 'x')
    concat = tensor.concatenate([y_mask_extended,
                                 y_mask_extended], axis=2)
    res = concat.reshape((concat.shape[0],
                          concat.shape[1] * concat.shape[2])).T
    beginning_blanks = tensor.ones((1, res.shape[1]),
                                   dtype=theano.config.floatX)
    blanked_y_mask = tensor.concatenate([beginning_blanks, res], axis=0)
    return blanked_y, blanked_y_mask


class adadelta(object):
    """
    An adaptive learning rate optimizer

    For more information, see:
    Matthew D. Zeiler, "ADADELTA: An Adaptive Learning Rate Method"
    arXiv:1212.5701.
    """
    def __init__(self, params, running_grad_decay=0.95, running_up_decay=0.95,
                 eps=1E-6):
        self.running_grad_decay = running_grad_decay
        self.running_up_decay = running_up_decay
        self.eps = eps
        self.running_up2_ = [theano.shared(np.zeros_like(p.get_value()))
                             for p in params]
        self.running_grads2_ = [theano.shared(np.zeros_like(p.get_value()))
                                for p in params]
        self.previous_grads_ = [theano.shared(np.zeros_like(p.get_value()))
                                for p in params]

    def updates(self, params, grads):
        running_grad_decay = self.running_grad_decay
        running_up_decay = self.running_up_decay
        eps = self.eps
        updates = []
        for n, (param, grad) in enumerate(zip(params, grads)):
            running_grad2 = self.running_grads2_[n]
            running_up2 = self.running_up2_[n]
            previous_grad = self.previous_grads_[n]
            rg2up = running_grad_decay * running_grad2 + (
                1. - running_grad_decay) * (grad ** 2)
            updir = -tensor.sqrt(running_up2 + eps) / tensor.sqrt(
                running_grad2 + eps) * previous_grad
            ru2up = running_up_decay * running_up2 + (
                1. - running_up_decay) * (updir ** 2)
            updates.append((previous_grad, grad))
            updates.append((running_grad2, rg2up))
            updates.append((running_up2, ru2up))
            updates.append((param, param + updir))
        return updates


def ctc_prediction_to_string(y_pred):
    indices = y_pred.argmax(axis=1)
    # remove blanks
    indices = indices[indices != len(chars)]
    # remove repeats
    not_same = np.where((indices[1:] != indices[:-1]))[0]
    last_char = ""
    if len(not_same) > 0:
        last_char = chars[indices[-1]]
        indices = indices[not_same]
    s = "".join([chars[i] for i in indices])
    return s + last_char


def prediction_to_string(y_pred):
    indices = y_pred.argmax(axis=1)
    # remove blanks
    indices = indices[indices != len(chars)]
    s = "".join([chars[i] for i in indices])
    return s


def make_minibatch_from_strings(strings):
    X_shapes = [string_to_image(s).shape for s in strings]
    y_shapes = [string_to_index(s).shape for s in strings]
    max_X_len = max([sh[0] for sh in X_shapes])
    max_y_len = max([sh[0] for sh in y_shapes])
    minibatch_size = len(strings)
    # assume all feature dimensions are equal!
    X_mb = np.zeros((max_X_len, minibatch_size, X_shapes[-1][1])).astype(
        theano.config.floatX)
    X_mask = np.zeros((max_X_len, len(strings))).astype(theano.config.floatX)
    y_mb = np.zeros((max_y_len, minibatch_size)).astype("int32")
    y_mask = np.ones_like(y_mb).astype(theano.config.floatX)
    for n, s in enumerate(strings):
        X = string_to_image(s)
        y = string_to_index(s)
        X_mb[:X.shape[0], n, :] = X
        X_mask[:X.shape[0], n] = 1.
        y_mb[:y.shape[0], n] = y
        y_mask[:y.shape[0], n] = 1.
    return X_mb, X_mask, y_mb, y_mask


if __name__ == "__main__":
    true_strings = ["Hello", "World"]
    minibatch_size = len(true_strings)
    X, X_mask, y, y_mask = make_minibatch_from_strings(true_strings)

    X_sym = tensor.tensor3('X')
    X_mask_sym = tensor.matrix('X_mask')
    y_sym = tensor.imatrix('Y_s')
    y_mask_sym = tensor.matrix('Y_s_mask')
    X_sym.tag.test_value = X
    X_mask_sym.tag.test_value = X_mask
    y_sym.tag.test_value = y
    y_mask_sym.tag.test_value = y_mask

    X_res, predict, params = build_model(X_sym, X_mask_sym, minibatch_size,
                                         X.shape[-1], 256, len(chars) + 1)
    y_ctc_sym, y_ctc_mask_sym = theano_label_seq(y_sym, y_mask_sym)
    cost = log_ctc_cost(y_ctc_sym, y_ctc_mask_sym, predict, X_mask_sym)

    grads = tensor.grad(cost, wrt=params)
    opt = adadelta(params)
    train = theano.function(inputs=[X_sym, X_mask_sym, y_sym, y_mask_sym],
                            outputs=cost,
                            updates=opt.updates(params, grads))
    pred = theano.function(inputs=[X_sym, X_mask_sym], outputs=predict)

    for i in range(1000):
        train_cost = train(X, X_mask, y, y_mask)
        if i % 100 == 0:
            print("Iteration %i:" % i)
            print(train_cost)
            p = pred(X, X_mask)
            for n in range(p.shape[1]):
                print(prediction_to_string(p[:, n, :]))
                print(ctc_prediction_to_string(p[:, n, :]))
    p = pred(X, X_mask)
    f, axarr = plt.subplots(p.shape[1])
    print("Final predictions:")
    predicted_strings = []
    for n in range(p.shape[1]):
        p_n = p[:, n, :]
        s = ctc_prediction_to_string(p_n)
        predicted_strings.append(s)
        X_n = X[:, n, :]
        axarr[n].matshow(X_n.T[::-1], cmap="gray")
        axarr[n].set_xticks([])
        axarr[n].set_yticks([])
    plt.suptitle(" ".join(predicted_strings) + " : " + " ".join(true_strings))
    plt.tight_layout()
    plt.show()
