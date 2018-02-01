# Author: Kyle Kastner
# License: BSD 3-clause
# Thanks to Jose (@sotelo) for tons of guidance and debug help
# Credit also to Junyoung (@jych) and Shawn (@shawntan) for help/utility funcs
# Strangeness in init could be from onehots, via @igul222. Ty init for one hot layer as N(0, 1) just as in embedding
# since oh.dot(w) is basically an embedding
import os
import re
import tarfile
from collections import Counter
import sys
import pickle
import numpy as np
import theano
import theano.tensor as tensor
from theano.sandbox.rng_mrg import MRG_RandomStreams as RandomStreams
from scipy import linalg


class base_iterator(object):
    def __init__(self, list_of_containers, minibatch_size,
                 axis,
                 start_index=0,
                 stop_index=np.inf,
                 make_mask=False,
                 one_hot_class_size=None):
        self.list_of_containers = list_of_containers
        self.minibatch_size = minibatch_size
        self.make_mask = make_mask
        self.start_index = start_index
        self.stop_index = stop_index
        self.slice_start_ = start_index
        self.axis = axis
        if axis not in [0, 1]:
            raise ValueError("Unknown sample_axis setting %i" % axis)
        self.one_hot_class_size = one_hot_class_size
        if one_hot_class_size is not None:
            assert len(self.one_hot_class_size) == len(list_of_containers)

    def reset(self):
        self.slice_start_ = self.start_index

    def __iter__(self):
        return self

    def next(self):
        return self.__next__()

    def __next__(self):
        self.slice_end_ = self.slice_start_ + self.minibatch_size
        if self.slice_end_ > self.stop_index:
            # TODO: Think about boundary issues with weird shaped last mb
            self.reset()
            raise StopIteration("Stop index reached")
        ind = slice(self.slice_start_, self.slice_end_)
        self.slice_start_ = self.slice_end_
        if self.make_mask is False:
            res = self._slice_without_masks(ind)
            if not all([self.minibatch_size in r.shape for r in res]):
                # TODO: Check that things are even
                self.reset()
                raise StopIteration("Partial slice returned, end of iteration")
            return res
        else:
            res = self._slice_with_masks(ind)
            # TODO: Check that things are even
            if not all([self.minibatch_size in r.shape for r in res]):
                self.reset()
                raise StopIteration("Partial slice returned, end of iteration")
            return res

    def _slice_without_masks(self, ind):
        raise AttributeError("Subclass base_iterator and override this method")

    def _slice_with_masks(self, ind):
        raise AttributeError("Subclass base_iterator and override this method")


class list_iterator(base_iterator):
    def _slice_without_masks(self, ind):
        sliced_c = [np.asarray(c[ind]) for c in self.list_of_containers]
        if min([len(i) for i in sliced_c]) < self.minibatch_size:
            self.reset()
            raise StopIteration("Invalid length slice")
        for n in range(len(sliced_c)):
            sc = sliced_c[n]
            if self.one_hot_class_size is not None:
                convert_it = self.one_hot_class_size[n]
                if convert_it is not None:
                    raise ValueError("One hot conversion not implemented")
            if not isinstance(sc, np.ndarray) or sc.dtype == np.object:
                maxlen = max([len(i) for i in sc])
                # Assume they at least have the same internal dtype
                if len(sc[0].shape) > 1:
                    total_shape = (maxlen, sc[0].shape[1])
                elif len(sc[0].shape) == 1:
                    total_shape = (maxlen, 1)
                else:
                    raise ValueError("Unhandled array size in list")
                if self.axis == 0:
                    raise ValueError("Unsupported axis of iteration")
                    new_sc = np.zeros((len(sc), total_shape[0],
                                       total_shape[1]))
                    new_sc = new_sc.squeeze().astype(sc[0].dtype)
                else:
                    new_sc = np.zeros((total_shape[0], len(sc),
                                       total_shape[1]))
                    new_sc = new_sc.astype(sc[0].dtype)
                    for m, sc_i in enumerate(sc):
                        new_sc[:len(sc_i), m, :] = sc_i
                sliced_c[n] = new_sc
        return sliced_c

    def _slice_with_masks(self, ind):
        cs = self._slice_without_masks(ind)
        if self.axis == 0:
            ms = [np.ones_like(c[:, 0]) for c in cs]
        elif self.axis == 1:
            ms = [np.ones_like(c[:, :, 0]) for c in cs]
        assert len(cs) == len(ms)
        return [i for sublist in list(zip(cs, ms)) for i in sublist]


def get_dataset_dir(dataset_name):
    """ Get dataset directory path """
    return os.sep.join(os.path.realpath(__file__).split
                       (os.sep)[:-1] + [dataset_name])


def check_fetch_iamondb():
    """ Check for IAMONDB data

        This dataset cannot be downloaded automatically!
    """
    partial_path = get_dataset_dir("iamondb")
    ascii_path = os.path.join(partial_path, "lineStrokes-all.tar.gz")
    lines_path = os.path.join(partial_path, "ascii-all.tar.gz")
    files_path = os.path.join(partial_path, "task1.tar.gz")
    for p in [ascii_path, lines_path, files_path]:
        if not os.path.exists(p):
            files = "lineStrokes-all.tar.gz, ascii-all.tar.gz, and task1.tar.gz"
            url = "http://www.iam.unibe.ch/fki/databases/"
            url += "iam-on-line-handwriting-database/"
            url += "download-the-iam-on-line-handwriting-database"
            err = "Path %s does not exist!" % p
            err += " Download the %s files from %s" % (files, url)
            err += " and place them in the directory %s" % partial_path
            raise ValueError(err)
    return partial_path


def dense_to_one_hot(labels_dense, num_classes=10):
    """Convert class labels from scalars to one-hot vectors."""
    labels_shape = labels_dense.shape
    labels_dense = labels_dense.reshape([-1])
    num_labels = labels_dense.shape[0]
    index_offset = np.arange(num_labels) * num_classes
    labels_one_hot = np.zeros((num_labels, num_classes))
    labels_one_hot.flat[index_offset + labels_dense.ravel()] = 1
    labels_one_hot = labels_one_hot.reshape(labels_shape+(num_classes,))
    return labels_one_hot


def tokenize_ind(phrase, vocabulary):
    phrase = phrase + " "
    vocabulary_size = len(vocabulary.keys())
    phrase = [vocabulary[char_] for char_ in phrase]
    phrase = np.array(phrase, dtype='int32').ravel()
    phrase = dense_to_one_hot(phrase, vocabulary_size)
    return phrase


def fetch_iamondb():
    from lxml import etree
    partial_path = check_fetch_iamondb()
    pickle_path = os.path.join(partial_path, "iamondb_saved.pkl")
    if not os.path.exists(pickle_path):
        input_file = os.path.join(partial_path, 'lineStrokes-all.tar.gz')
        raw_data = tarfile.open(input_file)
        transcript_files = []
        strokes = []
        idx = 0
        for member in raw_data.getmembers():
            if member.isreg():
                transcript_files.append(member.name)
                content = raw_data.extractfile(member)
                tree = etree.parse(content)
                root = tree.getroot()
                content.close()
                points = []
                for StrokeSet in root:
                    for i, Stroke in enumerate(StrokeSet):
                        for Point in Stroke:
                            points.append([i,
                                int(Point.attrib['x']),
                                int(Point.attrib['y'])])
                points = np.array(points)
                points[:, 2] = -points[:, 2]
                change_stroke = points[:-1, 0] != points[1:, 0]
                pen_up = points[:, 0] * 0
                pen_up[:-1][change_stroke] = 1
                pen_up[-1] = 1
                points[:, 0] = pen_up
                strokes.append(points)
                idx += 1

        strokes_bp = strokes

        strokes = [x[1:] - x[:-1] for x in strokes]
        strokes = [np.vstack([[0, 0, 0], x]) for x in strokes]

        for i, stroke in enumerate(strokes):
            strokes[i][:, 0] = strokes_bp[i][:, 0]

        # Computing mean and variance seems to not be necessary.
        # Training is going slower than just scaling.

        data_mean = np.array([0., 0., 0.])
        data_std = np.array([1., 20., 20.])

        strokes = [(x - data_mean) / data_std for x in strokes]

        transcript_files = [x.split(os.sep)[-1]
                            for x in transcript_files]
        transcript_files = [re.sub('-[0-9][0-9].xml', '.txt', x)
                            for x in transcript_files]

        counter = Counter(transcript_files)

        input_file = os.path.join(partial_path, 'ascii-all.tar.gz')

        raw_data = tarfile.open(input_file)
        member = raw_data.getmembers()[10]

        all_transcripts = []
        for member in raw_data.getmembers():
            if member.isreg() and member.name.split("/")[-1] in transcript_files:
                fp = raw_data.extractfile(member)

                cleaned = [t.strip() for t in fp.readlines()
                        if t != '\r\n'
                        and t != '\n'
                        and t != '\r\n'
                        and t.strip() != '']

                # Try using CSR
                idx = [n for n, li in enumerate(cleaned) if li == "CSR:"][0]
                cleaned_sub = cleaned[idx + 1:]
                corrected_sub = []
                for li in cleaned_sub:
                    # Handle edge case with %%%%% meaning new line?
                    if "%" in li:
                        li2 = re.sub('\%\%+', '%', li).split("%")
                        li2 = [l.strip() for l in li2]
                        corrected_sub.extend(li2)
                    else:
                        corrected_sub.append(li)

                if counter[member.name.split("/")[-1]] != len(corrected_sub):
                    pass

                all_transcripts.extend(corrected_sub)

        # Last file transcripts are almost garbage
        all_transcripts[-1] = 'A move to stop'
        all_transcripts.append('garbage')
        all_transcripts.append('A move to stop')
        all_transcripts.append('garbage')
        all_transcripts.append('A move to stop')
        all_transcripts.append('A move to stop')
        all_transcripts.append('Marcus Luvki')
        all_transcripts.append('Hallo Well')
        # Remove outliers and big / small sequences
        # Makes a BIG difference.
        filter_ = [len(x) <= 1200 and len(x) >= 300 and
                   x.max() <= 100 and x.min() >= -50 for x in strokes]

        strokes = [x for x, cond in zip(strokes, filter_) if cond]
        all_transcripts = [x for x, cond in
                           zip(all_transcripts, filter_) if cond]

        num_examples = len(strokes)

        # Shuffle for train/validation/test division
        rng = np.random.RandomState(1999)
        shuffle_idx = rng.permutation(num_examples)

        strokes = [strokes[x] for x in shuffle_idx]
        all_transcripts = [all_transcripts[x] for x in shuffle_idx]

        all_chars = ([chr(ord('a') + i) for i in range(26)] +
                     [chr(ord('A') + i) for i in range(26)] +
                     [chr(ord('0') + i) for i in range(10)] +
                     [',', '.', '!', '?', ';', ' ', ':'] +
                     ["#", '&', '+', '[', ']', '{', '}'] +
                     ["/", "*"] +
                     ['(', ')', '"', "'", '-', '<UNK>'])

        code2char = dict(enumerate(all_chars))
        char2code = {v: k for k, v in code2char.items()}
        vocabulary_size = len(char2code.keys())
        unk_char = '<UNK>'

        y = []
        for n, li in enumerate(all_transcripts):
            y.append(tokenize_ind(li, char2code))

        pickle_dict = {}
        pickle_dict["target_phrases"] = all_transcripts
        pickle_dict["vocabulary_size"] = vocabulary_size
        pickle_dict["vocabulary_tokenizer"] = tokenize_ind
        pickle_dict["vocabulary"] = char2code
        pickle_dict["data"] = strokes
        pickle_dict["target"] = y
        f = open(pickle_path, "wb")
        pickle.dump(pickle_dict, f, -1)
        f.close()
    with open(pickle_path, "rb") as f:
        pickle_dict = pickle.load(f)
    return pickle_dict


def plot_lines_iamondb_example(X, title="", save_name=None):
    import matplotlib.pyplot as plt
    f, ax = plt.subplots()
    x = np.cumsum(X[:, 1])
    y = np.cumsum(X[:, 2])

    size_x = x.max() - x.min()
    size_y = y.max() - y.min()

    f.set_size_inches(5 * size_x / size_y, 5)
    cuts = np.where(X[:, 0] == 1)[0]
    start = 0

    for cut_value in cuts:
        ax.plot(x[start:cut_value], y[start:cut_value],
                'k-', linewidth=1.5)
        start = cut_value + 1
    ax.axis('equal')
    ax.axes.get_xaxis().set_visible(False)
    ax.axes.get_yaxis().set_visible(False)
    ax.set_title(title)

    if save_name is None:
        plt.show()
    else:
        plt.savefig(save_name, bbox_inches='tight', pad_inches=0)


def implot(arr, title="", cmap="gray", save_name=None):
    import matplotlib.pyplot as plt
    f, ax = plt.subplots()
    ax.matshow(arr, cmap=cmap)
    plt.axis("off")

    def autoaspect(x_range, y_range):
        """
        The aspect to make a plot square with ax.set_aspect in Matplotlib
        """
        mx = max(x_range, y_range)
        mn = min(x_range, y_range)
        if x_range <= y_range:
            return mx / float(mn)
        else:
            return mn / float(mx)

    x1 = arr.shape[0]
    y1 = arr.shape[1]
    asp = autoaspect(x1, y1)
    ax.set_aspect(asp)
    plt.title(title)
    if save_name is None:
        plt.show()
    else:
        plt.savefig(save_name)


def np_zeros(shape):
    return np.zeros(shape).astype(theano.config.floatX)


def np_normal(shape, random_state, scale=0.01):
    if type(shape[0]) is tuple:
        shp = (shape[1][0], shape[0][0]) + shape[1][1:]
    else:
        shp = shape
    return (scale * random_state.randn(*shp)).astype(theano.config.floatX)


def np_ortho(shape, random_state, scale=1.):
    if type(shape[0]) is tuple:
        shp = (shape[1][0], shape[0][0]) + shape[1][1:]
        flat_shp = (shp[0], np.prd(shp[1:]))
    else:
        shp = shape
        flat_shp = shape
    g = random_state.randn(*flat_shp)
    U, S, VT = linalg.svd(g, full_matrices=False)
    res = U if U.shape == flat_shp else VT  # pick one with the correct shape
    res = res.reshape(shp)
    return (scale * res).astype(theano.config.floatX)


def as_shared(arr, name=None):
    """ Quick wrapper for theano.shared """
    if type(arr) in [float, int]:
        if name is not None:
            return theano.shared(np.cast[theano.config.floatX](arr))
        else:
            return theano.shared(np.cast[theano.config.floatX](arr), name=name)
    if name is not None:
        return theano.shared(value=arr, borrow=True)
    else:
        return theano.shared(value=arr, name=name, borrow=True)


def apply_shared(list_of_numpy):
    return [as_shared(arr) for arr in list_of_numpy]


def make_weights(in_dim, out_dims, random_state):
    return apply_shared([np_normal((in_dim, out_dim), random_state)
                         for out_dim in out_dims])


def gru_weights(input_dim, hidden_dim, random_state):
    shape = (input_dim, hidden_dim)
    W = np.hstack([np_normal(shape, random_state),
                   np_normal(shape, random_state),
                   np_normal(shape, random_state)])
    b = np_zeros((3 * shape[1],))
    Wur = np.hstack([np_normal((shape[1], shape[1]), random_state),
                     np_normal((shape[1], shape[1]), random_state), ])
    U = np_normal((shape[1], shape[1]), random_state)
    return W, b, Wur, U


class GRU(object):
    def __init__(self, input_dim, hidden_dim, random_state):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        W, b, Wur, U = gru_weights(input_dim, hidden_dim, random_state)
        self.Wur = as_shared(Wur)
        self.U = as_shared(U)
        self.shape = (input_dim, hidden_dim)

    def get_params(self):
        return self.Wur, self.U

    def step(self, inp, gate_inp, prev_state):
        dim = self.shape[1]
        gates = tensor.nnet.sigmoid(tensor.dot(prev_state, self.Wur) + gate_inp)
        update = gates[:, :dim]
        reset = gates[:, dim:]
        state_reset = prev_state * reset
        next_state = tensor.tanh(tensor.dot(state_reset, self.U) + inp)
        next_state = next_state * update + prev_state * (1 - update)
        return next_state


class GRUFork(object):
    def __init__(self, input_dim, hidden_dim, random_state):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        W, b, Wur, U = gru_weights(input_dim, hidden_dim, random_state)
        self.W = as_shared(W)
        self.b = as_shared(b)
        self.shape = (input_dim, hidden_dim)

    def get_params(self):
        return self.W, self.b

    def proj(self, inp):
        dim = self.shape[1]
        projected = tensor.dot(inp, self.W) + self.b
        if projected.ndim == 3:
            d = projected[:, :, :dim]
            g = projected[:, :, dim:]
        else:
            d = projected[:, :dim]
            g = projected[:, dim:]
        return d, g


def logsumexp(x, axis=None):
    x_max = tensor.max(x, axis=axis, keepdims=True)
    z = tensor.log(tensor.sum(tensor.exp(x - x_max),
                              axis=axis, keepdims=True)) + x_max
    return z.sum(axis=axis)


def bernoulli_and_bivariate_gmm(true, mu, sigma, corr, coeff, binary,
                                epsilon=1E-5):
    n_dim = true.ndim
    shape_t = true.shape
    true = true.reshape((-1, shape_t[-1]))
    true = true.dimshuffle(0, 1, 'x')

    mu_1 = mu[:, 0, :]
    mu_2 = mu[:, 1, :]

    sigma_1 = sigma[:, 0, :]
    sigma_2 = sigma[:, 1, :]

    binary = (binary + epsilon) * (1 - 2 * epsilon)
    theano.printing.Print("binary")(binary.shape)
    theano.printing.Print("true")(true.shape)

    c_b = tensor.sum(tensor.xlogx.xlogy0(true[:, 0],  binary) + tensor.xlogx.xlogy0(
        1 - true[:, 0], 1 - binary), axis=1)

    inner1 = (0.5 * tensor.log(1. - corr ** 2 + epsilon))
    inner1 += tensor.log(sigma_1) + tensor.log(sigma_2)
    inner1 += tensor.log(2. * np.pi)

    t1 = true[:, 1]
    t2 = true[:, 2]
    theano.printing.Print("t1")(t1.shape)
    theano.printing.Print("mu1")(mu_1.shape)
    theano.printing.Print("sigma1")(sigma_1.shape)
    Z = (((t1 - mu_1)/sigma_1)**2) + (((t2 - mu_2) / sigma_2)**2)
    Z -= (2. * (corr * (t1 - mu_1)*(t2 - mu_2)) / (sigma_1 * sigma_2))
    inner2 = 0.5 * (1. / (1. - corr**2 + epsilon))
    cost = - (inner1 + (inner2 * Z))

    nll = -logsumexp(tensor.log(coeff) + cost, axis=1)
    nll -= c_b
    return nll.reshape(shape_t[:-1], ndim=n_dim-1)


def sample_bernoulli_and_bivariate_gmm(mu, sigma, corr, coeff, binary,
                                       theano_rng, epsilon=1E-5):

    idx = tensor.argmax(theano_rng.multinomial(pvals=coeff, dtype=coeff.dtype),
                        axis=1)

    mu = mu[tensor.arange(mu.shape[0]), :, idx]
    sigma = sigma[tensor.arange(sigma.shape[0]), :, idx]
    corr = corr[tensor.arange(corr.shape[0]), idx]

    mu_x = mu[:, 0]
    mu_y = mu[:, 1]
    sigma_x = sigma[:, 0]
    sigma_y = sigma[:, 1]

    z = theano_rng.normal(size=mu.shape, avg=0., std=1., dtype=mu.dtype)

    un = theano_rng.uniform(size=binary.shape)
    binary = tensor.cast(un < binary, theano.config.floatX)

    s_x = (mu_x + sigma_x * z[:, 0]).dimshuffle(0, 'x')
    s_y = mu_y + sigma_y * (
        (z[:, 0] * corr) + (z[:, 1] * tensor.sqrt(1. - corr ** 2)))
    s_y = s_y.dimshuffle(0, 'x')
    s = tensor.concatenate([binary, s_x, s_y], axis=1)
    return s


def gradient_clipping(grads, rescale=5.):
    grad_norm = tensor.sqrt(sum(map(lambda x: tensor.sqr(x).sum(), grads)))
    scaling_num = rescale
    scaling_den = tensor.maximum(rescale, grad_norm)
    scaling = scaling_num / scaling_den
    return [g * scaling for g in grads]


class adam(object):
    """
    Adam optimizer

    Based on implementation from @NewMu / Alex Radford
    """
    def __init__(self, params, learning_rate, b1=0.1, b2=0.001, eps=1E-8):
        self.learning_rate = as_shared(learning_rate)
        self.b1 = b1
        self.b2 = b2
        self.eps = eps
        self.memory_ = [theano.shared(np.zeros_like(p.get_value()))
                        for p in params]
        self.velocity_ = [theano.shared(np.zeros_like(p.get_value()))
                          for p in params]
        self.itr_ = theano.shared(np.array(0.).astype(theano.config.floatX))

    def updates(self, params, grads):
        learning_rate = self.learning_rate
        b1 = self.b1
        b2 = self.b2
        eps = self.eps
        updates = []
        itr = self.itr_
        i_t = itr + 1.
        fix1 = 1. - (1. - b1) ** i_t
        fix2 = 1. - (1. - b2) ** i_t
        lr_t = learning_rate * (tensor.sqrt(fix2) / fix1)
        for n, (param, grad) in enumerate(zip(params, grads)):
            memory = self.memory_[n]
            velocity = self.velocity_[n]
            m_t = (b1 * grad) + ((1. - b1) * memory)
            v_t = (b2 * tensor.sqr(grad)) + ((1. - b2) * velocity)
            g_t = m_t / (tensor.sqrt(v_t) + eps)
            p_t = param - (lr_t * g_t)
            updates.append((memory, m_t))
            updates.append((velocity, v_t))
            updates.append((param, p_t))
        updates.append((itr, i_t))
        return updates


def get_shared_variables_from_function(func):
    shared_variable_indices = [n for n, var in enumerate(func.maker.inputs)
                               if isinstance(var.variable,
                                             theano.compile.SharedVariable)]
    shared_variables = [func.maker.inputs[i].variable
                        for i in shared_variable_indices]
    return shared_variables


def get_values_from_function(func):
    return [v.get_value() for v in get_shared_variables_from_function(func)]


def safe_zip(*args):
    """Like zip, but ensures arguments are of same length.

       Borrowed from pylearn2
    """
    base = len(args[0])
    for i, arg in enumerate(args[1:]):
        if len(arg) != base:
            raise ValueError("Argument 0 has length %d but argument %d has "
                             "length %d" % (base, i+1, len(arg)))
    return zip(*args)


def set_shared_variables_in_function(func, list_of_values):
    # TODO : Add checking that sizes are OK
    shared_variable_indices = [n for n, var in enumerate(func.maker.inputs)
                               if isinstance(var.variable,
                                             theano.compile.SharedVariable)]
    shared_variables = [func.maker.inputs[i].variable
                        for i in shared_variable_indices]
    [s.set_value(v) for s, v in safe_zip(shared_variables, list_of_values)]


def save_weights(save_weights_path, items_dict):
    print("Saving weights to %s" % save_weights_path)
    weights_dict = {}
    # k is the function name, v is a theano function
    for k, v in items_dict.items():
        if isinstance(v, theano.compile.function_module.Function):
            # w is all the numpy values from a function
            w = get_values_from_function(v)
            for n, w_v in enumerate(w):
                weights_dict[k + "_%i" % n] = w_v
    if len(weights_dict.keys()) > 0:
        np.savez(save_weights_path, **weights_dict)
    else:
        print("Possible BUG: no theano functions found in items_dict, "
              "unable to save weights!")


def save_checkpoint(save_path, pickle_item):
    old_recursion_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(40000)
    with open(save_path, mode="wb") as f:
        pickle.dump(pickle_item, f, protocol=-1)
    sys.setrecursionlimit(old_recursion_limit)


def load_checkpoint(saved_checkpoint_path):
    old_recursion_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(40000)
    with open(saved_checkpoint_path, mode="rb") as f:
        pickle_item = pickle.load(f)
    sys.setrecursionlimit(old_recursion_limit)
    return pickle_item


def handwriting_sample(rval, random_state, idx=-1):
    # mu
    # sigma
    # corr
    # coeff
    # binary
    mu, sigma, corr, coeff, binary = rval
    binary = binary[idx:, 0]
    coeff = coeff[idx:, :]
    # Renormalize coeffs
    eps = 1E-6
    coeff = (coeff / (coeff.sum(axis=-1, keepdims=True) + eps))
    mu_x = mu[idx:, 0, :]
    mu_y = mu[idx:, 1, :]
    sigma_x = sigma[idx:, 0, :] + eps
    sigma_y = sigma[idx:, 1, :] + eps
    corr = corr[idx:, :]
    z_x = random_state.randn(*mu_x.shape)
    z_y = random_state.randn(*mu_y.shape)
    chosen = []
    for i in range(len(coeff)):
        chosen.append(np.argmax(random_state.multinomial(1, coeff[i])))
    chosen = np.array(chosen)
    s_x = mu_x + sigma_x * z_x
    s_y = mu_y + sigma_y * ((z_x * corr) + z_y * np.sqrt(1. - corr ** 2))
    binarized = random_state.binomial(1, binary).ravel()[:, None]
    s_x = s_x[np.arange(len(s_x)), chosen.ravel()][:, None]
    s_y = s_y[np.arange(len(s_x)), chosen.ravel()][:, None]
    return binarized, s_x, s_y, chosen

if __name__ == "__main__":
    import argparse

    iamondb = fetch_iamondb()
    X = iamondb["data"]
    y = iamondb["target"]
    vocabulary = iamondb["vocabulary"]
    vocabulary_size = iamondb["vocabulary_size"]
    X = np.array([x.astype(theano.config.floatX) for x in X])
    y = np.array([yy.astype(theano.config.floatX) for yy in y])

    minibatch_size = 50
    n_epochs = 100  # Used way at the bottom in the training loop!
    cut_len = 300  # Used way at the bottom in the training loop!
    random_state = np.random.RandomState(1999)

    train_itr = list_iterator([X, y], minibatch_size, axis=1, stop_index=10000,
                              make_mask=True)
    valid_itr = list_iterator([X, y], minibatch_size, axis=1, start_index=10000,
                              make_mask=True)

    X_mb, X_mb_mask, c_mb, c_mb_mask = next(train_itr)
    train_itr.reset()

    input_dim = X_mb.shape[-1]
    n_hid = 400
    att_size = 10
    n_components = 20
    n_out = 3
    n_chars = vocabulary_size
    n_density = 1 + 6 * n_components

    desc = "Handwriting generation based on Graves' "
    desc += " Generating Sequences with Recurrent Neural Networks"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-s', '--sample',
                        help='Sample from a checkpoint file',
                        default=None,
                        required=False)
    parser.add_argument('-p', '--plot',
                        help='Plot training curves from a checkpoint file',
                        default=None,
                        required=False)
    parser.add_argument('-w', '--write',
                        help='The string to write out (default first minibatch)',
                        default=None,
                        required=False)
    # http://stackoverflow.com/questions/12116685/how-can-i-require-my-python-scripts-argument-to-be-a-float-between-0-0-1-0-usin
    def restricted_float(x):
        x = float(x)
        if x < 0.0:
            raise argparse.ArgumentTypeError("%r not range [0.0, inf]" % (x,))
        return x
    parser.add_argument('-b', '--bias',
                        help='Bias parameter as a float',
                        type=restricted_float,
                        default=.1,
                        required=False)

    def restricted_int(x):
        if x is None:
            # None makes it "auto" sample
            return x
        x = int(x)
        if x < 1:
            raise argparse.ArgumentTypeError("%r not range [1, inf]" % (x,))
        return x
    parser.add_argument('-sl', '--sample_length',
                        help='Number of steps to sample, default is automatic',
                        type=restricted_int,
                        default=None,
                        required=False)
    parser.add_argument('-c', '--continue', dest="cont",
                        help='Continue training from another saved model',
                        default=None,
                        required=False)
    args = parser.parse_args()
    if args.plot is not None or args.sample is not None:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        if args.sample is not None:
            checkpoint_file = args.sample
        else:
            checkpoint_file = args.plot
        if not os.path.exists(checkpoint_file):
            raise ValueError("Checkpoint file path %s" % checkpoint_file,
                             " does not exist!")
        print(checkpoint_file)
        checkpoint_dict = load_checkpoint(checkpoint_file)
        train_costs = checkpoint_dict["overall_train_costs"]
        valid_costs = checkpoint_dict["overall_valid_costs"]
        plt.plot(train_costs)
        plt.plot(valid_costs)
        plt.savefig("costs.png")

        X_mb, X_mb_mask, c_mb, c_mb_mask = next(valid_itr)
        valid_itr.reset()
        prev_h1, prev_h2, prev_h3 = [np_zeros((minibatch_size, n_hid))
                                     for i in range(3)]
        prev_kappa = np_zeros((minibatch_size, att_size))
        prev_w = np_zeros((minibatch_size, n_chars))
        bias = args.bias
        if args.sample is not None:
            predict_function = checkpoint_dict["predict_function"]
            attention_function = checkpoint_dict["attention_function"]
            sample_function = checkpoint_dict["sample_function"]
            if args.write is not None:
                sample_string = args.write
                print("Sampling using sample string %s" % sample_string)
                oh = dense_to_one_hot(
                    np.array([vocabulary[c] for c in sample_string]),
                    vocabulary_size)
                c_mb[:len(oh), :, :] = oh[:, None, :]
                c_mb = c_mb[:len(oh)]
                c_mb_mask = c_mb_mask[:len(oh)]

            if args.sample_length is None:
                # Automatic sampling stop as described in Graves' paper
                # Assume an average of 30 timesteps per char
                n_steps = 30 * c_mb.shape[0]
                step_inc = n_steps
                max_steps = 25000
                max_steps_buf = max_steps + n_steps
                completed = [np.zeros((max_steps_buf, 3))
                             for i in range(c_mb.shape[1])]
                max_indices = [None] * c_mb.shape[1]
                completed_indices = set()
                # hardcoded upper limit
                while n_steps < max_steps:
                    rvals = sample_function(c_mb, c_mb_mask, prev_h1, prev_h2,
                                            prev_h3, prev_kappa, prev_w, bias,
                                            n_steps)
                    sampled, h1_s, h2_s, h3_s, k_s, w_s, stop_s, stop_h = rvals
                    for i in range(c_mb.shape[1]):
                        max_ind = None
                        for j in range(len(stop_s)):
                            if np.all(stop_h[j, i] > stop_s[j, i]):
                                max_ind = j

                        if max_ind is not None:
                            completed_indices = completed_indices | set([i])
                            completed[i][:max_ind] = sampled[:max_ind, i]
                            max_indices[i] = max_ind
                    # if most samples meet the criteria call it good
                    if len(completed_indices) >= .8 * c_mb.shape[1]:
                        break
                    n_steps += step_inc
                print("Completed sampling after %i steps" % n_steps)
                # cut out garbage
                completed = [completed[i] for i in completed_indices]
                cond = c_mb[:, np.array(list(completed_indices))]
            else:
                fixed_steps = args.sample_length
                rvals = sample_function(c_mb, c_mb_mask, prev_h1, prev_h2,
                                        prev_h3, prev_kappa, prev_w, bias,
                                        fixed_steps)
                sampled, h1_s, h2_s, h3_s, k_s, w_s, stop_s, stop_h = rvals
                completed = [sampled[:, i]
                             for i in range(sampled.shape[1])]
                cond = c_mb
                print("Completed sampling after %i steps" % fixed_steps)

            rlookup = {v: k for k, v in vocabulary.items()}
            for i in range(len(completed)):
                ex = completed[i]
                ex_str = "".join([rlookup[c]
                                  for c in np.argmax(cond[:, i], axis=1)])
                s = "lines_%i.png" % i
                plot_lines_iamondb_example(ex, title=ex_str, save_name=s)
        valid_itr.reset()
        print("Plotting complete, exiting...")
        sys.exit()
    else:
        print("No plotting arguments, starting training mode!")

    X_sym = tensor.tensor3("X_sym")
    X_sym.tag.test_value = X_mb
    X_mask_sym = tensor.matrix("X_mask_sym")
    X_mask_sym.tag.test_value = X_mb_mask
    c_sym = tensor.tensor3("c_sym")
    c_sym.tag.test_value = c_mb
    c_mask_sym = tensor.matrix("c_mask_sym")
    c_mask_sym.tag.test_value = c_mb_mask
    bias_sym = tensor.scalar("bias_sym")
    bias_sym.tag.test_value = 0.

    init_h1 = tensor.matrix("init_h1")
    init_h1.tag.test_value = np_zeros((minibatch_size, n_hid))

    init_h2 = tensor.matrix("init_h2")
    init_h2.tag.test_value = np_zeros((minibatch_size, n_hid))

    init_h3 = tensor.matrix("init_h3")
    init_h3.tag.test_value = np_zeros((minibatch_size, n_hid))

    init_kappa = tensor.matrix("init_kappa")
    init_kappa.tag.test_value = np_zeros((minibatch_size, att_size))

    init_w = tensor.matrix("init_w")
    init_w.tag.test_value = np_zeros((minibatch_size, n_chars))

    params = []

    cell1 = GRU(input_dim, n_hid, random_state)
    cell2 = GRU(n_hid, n_hid, random_state)
    cell3 = GRU(n_hid, n_hid, random_state)

    params += cell1.get_params()
    params += cell2.get_params()
    params += cell3.get_params()

    # Use GRU classes only to fork 1 inp to 2 inp:gate pairs
    inp_to_h1 = GRUFork(input_dim, n_hid, random_state)
    inp_to_h2 = GRUFork(input_dim, n_hid, random_state)
    inp_to_h3 = GRUFork(input_dim, n_hid, random_state)
    att_to_h1 = GRUFork(n_chars, n_hid, random_state)
    att_to_h2 = GRUFork(n_chars, n_hid, random_state)
    att_to_h3 = GRUFork(n_chars, n_hid, random_state)
    h1_to_h2 = GRUFork(n_hid, n_hid, random_state)
    h1_to_h3 = GRUFork(n_hid, n_hid, random_state)
    h2_to_h3 = GRUFork(n_hid, n_hid, random_state)

    params += inp_to_h1.get_params()
    params += inp_to_h2.get_params()
    params += inp_to_h3.get_params()
    params += att_to_h1.get_params()
    params += att_to_h2.get_params()
    params += att_to_h3.get_params()
    params += h1_to_h2.get_params()
    params += h1_to_h3.get_params()
    params += h2_to_h3.get_params()

    h1_to_att_a, h1_to_att_b, h1_to_att_k = make_weights(n_hid, 3 * [att_size],
                                                         random_state)
    h1_to_outs, = make_weights(n_hid, [n_density], random_state)
    h2_to_outs, = make_weights(n_hid, [n_density], random_state)
    h3_to_outs, = make_weights(n_hid, [n_density], random_state)

    params += [h1_to_att_a, h1_to_att_b, h1_to_att_k]
    params += [h1_to_outs, h2_to_outs, h3_to_outs]

    inpt = X_sym[:-1]
    target = X_sym[1:]
    mask = X_mask_sym[1:]
    context = c_sym * c_mask_sym.dimshuffle(0, 1, 'x')

    inp_h1, inpgate_h1 = inp_to_h1.proj(inpt)
    inp_h2, inpgate_h2 = inp_to_h2.proj(inpt)
    inp_h3, inpgate_h3 = inp_to_h3.proj(inpt)

    u = tensor.arange(c_sym.shape[0]).dimshuffle('x', 'x', 0)
    u = tensor.cast(u, theano.config.floatX)

    def calc_phi(k_t, a_t, b_t, u_c):
        a_t = a_t.dimshuffle(0, 1, 'x')
        b_t = b_t.dimshuffle(0, 1, 'x')
        ss1 = (k_t.dimshuffle(0, 1, 'x') - u_c) ** 2
        ss2 = -b_t * ss1
        ss3 = a_t * tensor.exp(ss2)
        ss4 = ss3.sum(axis=1)
        return ss4

    def step(xinp_h1_t, xgate_h1_t,
             xinp_h2_t, xgate_h2_t,
             xinp_h3_t, xgate_h3_t,
             h1_tm1, h2_tm1, h3_tm1,
             k_tm1, w_tm1, ctx):

        attinp_h1, attgate_h1 = att_to_h1.proj(w_tm1)

        h1_t = cell1.step(xinp_h1_t + attinp_h1, xgate_h1_t + attgate_h1,
                          h1_tm1)
        h1inp_h2, h1gate_h2 = h1_to_h2.proj(h1_t)
        h1inp_h3, h1gate_h3 = h1_to_h3.proj(h1_t)

        a_t = h1_t.dot(h1_to_att_a)
        b_t = h1_t.dot(h1_to_att_b)
        k_t = h1_t.dot(h1_to_att_k)

        a_t = tensor.exp(a_t)
        b_t = tensor.exp(b_t)
        k_t = k_tm1 + tensor.exp(k_t)

        ss4 = calc_phi(k_t, a_t, b_t, u)
        ss5 = ss4.dimshuffle(0, 1, 'x')
        ss6 = ss5 * ctx.dimshuffle(1, 0, 2)
        w_t = ss6.sum(axis=1)

        attinp_h2, attgate_h2 = att_to_h2.proj(w_t)
        attinp_h3, attgate_h3 = att_to_h3.proj(w_t)

        h2_t = cell2.step(xinp_h2_t + h1inp_h2 + attinp_h2,
                          xgate_h2_t + h1gate_h2 + attgate_h2, h2_tm1)

        h2inp_h3, h2gate_h3 = h2_to_h3.proj(h2_t)

        h3_t = cell3.step(xinp_h3_t + h1inp_h3 + h2inp_h3 + attinp_h3,
                          xgate_h3_t + h1gate_h3 + h2gate_h3 + attgate_h3,
                          h3_tm1)
        return h1_t, h2_t, h3_t, k_t, w_t

    init_x = as_shared(np_zeros((minibatch_size, n_out)))
    srng = RandomStreams(1999)

    def _slice_outs(outs):
        k = n_components
        outs = outs.reshape((-1, n_density))
        mu = outs[:, 0:2*k].reshape((-1, 2, k))
        sigma = outs[:, 2*k:4*k].reshape((-1, 2, k))
        corr = outs[:, 4*k:5*k]
        coeff = outs[:, 5*k:6*k]
        binary = outs[:, 6*k:]
        sigma = tensor.exp(sigma - bias_sym) + 1E-6
        corr = tensor.tanh(corr)
        coeff = tensor.nnet.softmax(coeff * (1. + bias_sym)) + 1E-6
        binary = tensor.nnet.sigmoid(binary * (1. + bias_sym))
        return mu, sigma, corr, coeff, binary

    # Used to calculate stopping heuristic from sections 5.3
    u_max = 0. * tensor.arange(c_sym.shape[0]) + c_sym.shape[0]
    u_max = u_max.dimshuffle('x', 'x', 0)
    u_max = tensor.cast(u_max, theano.config.floatX)

    def sample_step(x_tm1, h1_tm1, h2_tm1, h3_tm1, k_tm1, w_tm1, ctx):
        xinp_h1_t, xgate_h1_t = inp_to_h1.proj(x_tm1)
        xinp_h2_t, xgate_h2_t = inp_to_h2.proj(x_tm1)
        xinp_h3_t, xgate_h3_t = inp_to_h3.proj(x_tm1)

        attinp_h1, attgate_h1 = att_to_h1.proj(w_tm1)

        h1_t = cell1.step(xinp_h1_t + attinp_h1, xgate_h1_t + attgate_h1,
                          h1_tm1)
        h1inp_h2, h1gate_h2 = h1_to_h2.proj(h1_t)
        h1inp_h3, h1gate_h3 = h1_to_h3.proj(h1_t)

        a_t = h1_t.dot(h1_to_att_a)
        b_t = h1_t.dot(h1_to_att_b)
        k_t = h1_t.dot(h1_to_att_k)

        a_t = tensor.exp(a_t)
        b_t = tensor.exp(b_t)
        k_t = k_tm1 + tensor.exp(k_t)

        ss_t = calc_phi(k_t, a_t, b_t, u)
        # calculate and return stopping criteria
        sh_t = calc_phi(k_t, a_t, b_t, u_max)
        ss5 = ss_t.dimshuffle(0, 1, 'x')
        ss6 = ss5 * ctx.dimshuffle(1, 0, 2)
        w_t = ss6.sum(axis=1)

        attinp_h2, attgate_h2 = att_to_h2.proj(w_t)
        attinp_h3, attgate_h3 = att_to_h3.proj(w_t)

        h2_t = cell2.step(xinp_h2_t + h1inp_h2 + attinp_h2,
                          xgate_h2_t + h1gate_h2 + attgate_h2, h2_tm1)

        h2inp_h3, h2gate_h3 = h2_to_h3.proj(h2_t)

        h3_t = cell3.step(xinp_h3_t + h1inp_h3 + h2inp_h3 + attinp_h3,
                          xgate_h3_t + h1gate_h3 + h2gate_h3 + attgate_h3,
                          h3_tm1)
        out_t = h1_t.dot(h1_to_outs) + h2_t.dot(h2_to_outs) + h3_t.dot(
            h3_to_outs)

        mu, sigma, corr, coeff, binary = _slice_outs(out_t)
        s = sample_bernoulli_and_bivariate_gmm(mu, sigma, corr, coeff, binary,
                                               srng)
        x_t = s
        return x_t, h1_t, h2_t, h3_t, k_t, w_t, ss_t, sh_t

    n_steps_sym = tensor.iscalar()
    (sampled, h1_s, h2_s, h3_s, k_s, w_s, stop_s, stop_h), supdates = theano.scan(
        fn=sample_step,
        n_steps=n_steps_sym,
        sequences=[],
        outputs_info=[init_x, init_h1, init_h2, init_h3,
                      init_kappa, init_w, None, None],
        non_sequences=[context])


    """
    # Testing step function
    r = step(inp_h1[0], inpgate_h1[0], inp_h2[0], inpgate_h2[0],
             inp_h3[0], inpgate_h3[0],
             init_h1, init_h2, init_h3, init_kappa, init_w, context)

    r = step(inp_h1[1], inpgate_h1[1], inp_h2[1], inpgate_h2[1],
             inp_h3[1], inpgate_h3[1],
             r[0], r[1], r[2], r[3], r[4], context)
    """
    (h1, h2, h3, kappa, w), updates = theano.scan(
        fn=step,
        sequences=[inp_h1, inpgate_h1,
                   inp_h2, inpgate_h2,
                   inp_h3, inpgate_h3],
        outputs_info=[init_h1, init_h2, init_h3, init_kappa, init_w],
        non_sequences=[context])

    outs = h1.dot(h1_to_outs) + h2.dot(h2_to_outs) + h3.dot(h3_to_outs)

    mu, sigma, corr, coeff, binary = _slice_outs(outs)

    cost = bernoulli_and_bivariate_gmm(target, mu, sigma, corr, coeff, binary)

    cost = cost * mask
    cost = cost.sum() / mask.sum()  # / cut_len might make more sense
    grads = tensor.grad(cost, params)
    grads = gradient_clipping(grads, 10.)

    learning_rate = 1E-4

    opt = adam(params, learning_rate)
    updates = opt.updates(params, grads)

    train_function = theano.function([X_sym, X_mask_sym, c_sym, c_mask_sym,
                                      init_h1, init_h2, init_h3, init_kappa,
                                      init_w, bias_sym],
                                     [cost, h1, h2, h3, kappa, w],
                                     updates=updates)
    cost_function = theano.function([X_sym, X_mask_sym, c_sym, c_mask_sym,
                                     init_h1, init_h2, init_h3, init_kappa,
                                     init_w, bias_sym],
                                    [cost, h1, h2, h3, kappa, w])
    predict_function = theano.function([X_sym, X_mask_sym, c_sym, c_mask_sym,
                                        init_h1, init_h2, init_h3, init_kappa,
                                        init_w, bias_sym],
                                       [mu, sigma, corr, coeff, binary],
                                       on_unused_input='warn')
    attention_function = theano.function([X_sym, X_mask_sym, c_sym, c_mask_sym,
                                          init_h1, init_h2, init_h3, init_kappa,
                                          init_w],
                                         [kappa, w], on_unused_input='warn')
    sample_function = theano.function([c_sym, c_mask_sym, init_h1, init_h2,
                                       init_h3, init_kappa, init_w, bias_sym,
                                       n_steps_sym],
                                      [sampled, h1_s, h2_s, h3_s, k_s, w_s,
                                       stop_s, stop_h],
                                      updates=supdates)

    checkpoint_dict = {}
    checkpoint_dict["train_function"] = train_function
    checkpoint_dict["cost_function"] = cost_function
    checkpoint_dict["predict_function"] = predict_function
    checkpoint_dict["attention_function"] = attention_function
    checkpoint_dict["sample_function"] = sample_function

    print("Beginning training loop")
    train_mb_count = 0
    valid_mb_count = 0
    start_epoch = 0
    monitor_frequency = 1000 // minibatch_size
    overall_train_costs = []
    overall_valid_costs = []

    if args.cont is not None:
        continue_path = args.cont
        if not os.path.exists(continue_path):
            raise ValueError("Continue model %s, path not "
                             "found" % continue_path)
        saved_checkpoint = load_checkpoint(continue_path)
        trained_weights = get_values_from_function(
            saved_checkpoint["train_function"])
        set_shared_variables_in_function(train_function, trained_weights)
        try:
            overall_train_costs = saved_checkpoint["overall_train_costs"]
            overall_valid_costs = saved_checkpoint["overall_valid_costs"]
            start_epoch = len(overall_train_costs)
        except KeyError:
            print("Key not found - model structure may have changed.")
            print("Continuing anyways - statistics may not be correct!")


    def _loop(function, itr):
        prev_h1, prev_h2, prev_h3 = [np_zeros((minibatch_size, n_hid))
                                     for i in range(3)]
        prev_kappa = np_zeros((minibatch_size, att_size))
        prev_w = np_zeros((minibatch_size, n_chars))
        X_mb, X_mb_mask, c_mb, c_mb_mask = next(itr)
        n_cuts = len(X_mb) // cut_len + 1
        partial_costs = []
        for n in range(n_cuts):
            start = n * cut_len
            stop = (n + 1) * cut_len
            if len(X_mb[start:stop]) < 1:
                # edge case where there is only one sample left
                # just ignore the last sample
                break
            bias = 0. # No bias in training
            rval = function(X_mb[start:stop],
                            X_mb_mask[start:stop],
                            c_mb, c_mb_mask,
                            prev_h1, prev_h2, prev_h3, prev_kappa, prev_w, bias)
            current_cost = rval[0]
            prev_h1, prev_h2, prev_h3 = rval[1:4]
            prev_h1 = prev_h1[-1]
            prev_h2 = prev_h2[-1]
            prev_h3 = prev_h3[-1]
            prev_kappa = rval[4][-1]
            prev_w = rval[5][-1]
        partial_costs.append(current_cost)
        return partial_costs

    for e in range(start_epoch, start_epoch + n_epochs):
        train_costs = []
        try:
            while True:
                partial_train_costs = _loop(train_function, train_itr)
                train_costs.append(np.mean(partial_train_costs))
                if train_mb_count % monitor_frequency == 0:
                    print("starting train mb %i" % train_mb_count)
                    print("current epoch mean cost %f" % np.mean(train_costs))
                train_mb_count += 1
        except StopIteration:
            valid_costs = []
            try:
                while True:
                    partial_valid_costs = _loop(cost_function, valid_itr)
                    valid_costs.append(np.mean(partial_valid_costs))
                    if valid_mb_count % monitor_frequency == 0:
                        print("starting valid mb %i" % valid_mb_count)
                        print("current validation mean cost %f" % np.mean(
                            valid_costs))
                    valid_mb_count += 1
            except StopIteration:
                pass
            mean_epoch_train_cost = np.mean(train_costs)
            mean_epoch_valid_cost = np.mean(valid_costs)
            overall_train_costs.append(mean_epoch_train_cost)
            overall_valid_costs.append(mean_epoch_valid_cost)
            checkpoint_dict["overall_train_costs"] = overall_train_costs
            checkpoint_dict["overall_valid_costs"] = overall_valid_costs
            print("epoch %i complete" % e)
            print("epoch mean train cost %f" % mean_epoch_train_cost)
            print("epoch mean valid cost %f" % mean_epoch_valid_cost)
            print("overall train costs %s" % overall_train_costs)
            print("overall valid costs %s" % overall_valid_costs)
            checkpoint_save_path = "model_checkpoint_%i.pkl" % e
            weights_save_path = "model_weights_%i.npz" % e
            save_checkpoint(checkpoint_save_path, checkpoint_dict)
            save_weights(weights_save_path, checkpoint_dict)
