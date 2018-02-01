# Author: Kyle Kastner
# License: BSD 3-Clause
# See core implementations here http://geekyisawesome.blogspot.ca/2016/10/using-beam-search-to-generate-most.html
# Also includes a reduction of the post by Yoav Goldberg to a script
# markov_lm.py
# https://gist.github.com/yoavg/d76121dfde2618422139

# These datasets can be a lot of fun...
#
# https://github.com/frnsys/texts
# python minimal_beamsearch.py 2600_phrases_for_effective_performance_reviews.txt -o 5 -d 0
#
# Download kjv.txt from http://www.ccel.org/ccel/bible/kjv.txt
# python minimal_beamsearch.py kjv.txt -o 5 -d 2 -r 2145
# Snippet:
#  Queen ording found Raguel: I kill.
#  THROUGH JESUS OF OUR BRETHREN, AND PEACE,
#
#  NUN.


import numpy as np
import heapq
from collections import defaultdict, Counter
import collections
import os
import sys
import argparse
import cPickle as pickle
import time
from itertools import izip


class Beam(object):
    """
    From http://geekyisawesome.blogspot.ca/2016/10/using-beam-search-to-generate-most.html
    For comparison of prefixes, the tuple (prefix_probability, complete_sentence) is used.
    This is so that if two prefixes have equal probabilities then a complete sentence is preferred
    over an incomplete one since (0.5, False, whatever_prefix) < (0.5, True, some_other_prefix)
    """
    def __init__(self, beam_width, init_beam=None, use_log=True,
                 stochastic=False, temperature=1.0, random_state=None):
        if init_beam is None:
            self.heap = list()
        else:
            self.heap = init_beam
            heapq.heapify(self.heap)
        self.stochastic = stochastic
        self.random_state = random_state
        self.temperature = temperature
        # use_log currently unused...
        self.use_log = use_log
        self.beam_width = beam_width

    def add(self, score, complete, prob, prefix):
        heapq.heappush(self.heap, (score, complete, prob, prefix))
        while len(self.heap) > self.beam_width:
            if self.stochastic:
                # same whether logspace or no?
                probs = np.array([h[0] for h in self.heap])
                probs = probs / self.temperature
                e_x = np.exp(probs - np.max(probs))
                s_x = e_x / e_x.sum()
                is_x = 1. - s_x
                is_x = is_x / is_x.sum()
                to_remove = self.random_state.multinomial(1, is_x).argmax()
                completed = [n for n, h in enumerate(self.heap) if h[1] == True]
                # Don't remove completed sentences by randomness
                if to_remove not in completed:
                    # there must be a faster way...
                    self.heap.pop(to_remove)
                    heapq.heapify(self.heap)
                else:
                    heapq.heappop(self.heap)
            else:
                # remove lowest score from heap
                heapq.heappop(self.heap)

    def __iter__(self):
        return iter(self.heap)


def beamsearch(probabilities_function, beam_width=10, clip_len=-1,
               start_token="<START>", end_token="<EOS>", use_log=True,
               renormalize=True, length_score=True,
               diversity_score=True,
               stochastic=False, temperature=1.0,
               random_state=None, eps=1E-9):
    """
    From http://geekyisawesome.blogspot.ca/2017/04/getting-top-n-most-probable-sentences.html

    returns a generator, which will yield beamsearched sequences in order of their probability

    "probabilities_function" returns a list of (next_prob, next_word) pairs given a prefix.

    "beam_width" is the number of prefixes to keep (so that instead of keeping the top 10 prefixes you can keep the top 100 for example).
    By making the beam search bigger you can get closer to the actual most probable sentence but it would also take longer to process.

    "clip_len" is a maximum length to tolerate, beyond which the most probable prefix is returned as an incomplete sentence.
    Without a maximum length, a faulty probabilities function which does not return a highly probable end token
    will lead to an infinite loop or excessively long garbage sentences.

    "start_token" can be a single string (token), or a sequence of tokens

    "end_token" is a single string (token), or a sequence of tokens that signifies end of the sequence

    "use_log, renormalize, length_score" are all related to calculation of beams to keep
    and should improve results when True

    "stochastic" uses a different sampling algorithm for reducing/aggregating beams
    it should result in more diverse and interesting outputs

    "temperature" is the softmax temperature for the underlying stochastic
    beamsearch - the default of 1.0 is usually fine

    "random_state" is a np.random.RandomState() object, passed when using the
    stochastic beamsearch in order to control randomness

    "eps" minimum probability for log-space calculations, to avoid numerical issues
    """
    if stochastic:
        if random_state is None:
            raise ValueError("Must pass np.random.RandomState() object if stochastic=True")

    completed_beams = 0
    prev_beam = Beam(beam_width - completed_beams, None, use_log, stochastic,
                     temperature, random_state)
    try:
        basestring
    except NameError:
        basestring = str

    if isinstance(start_token, collections.Sequence) and not isinstance(start_token, basestring):
        start_token_is_seq = True
    else:
        # make it a list with 1 entry
        start_token = [start_token]
        start_token_is_seq = False

    if isinstance(end_token, collections.Sequence) and not isinstance(end_token, basestring):
        end_token_is_seq = True
    else:
        # make it a list with 1 entry
        end_token = [end_token]
        end_token_is_seq = False

    if use_log:
        prev_beam.add(.0, False, .0, start_token)
    else:
        prev_beam.add(1.0, False, 1.0, start_token)


    while True:
        curr_beam = Beam(beam_width - completed_beams, None, use_log, stochastic,
                         temperature, random_state)
        if renormalize:
            sorted_prev_beam = sorted(prev_beam)
            # renormalize by the previous minimum value in the beam
            min_prob = sorted_prev_beam[0][0]
        else:
            if use_log:
                min_prob = 0.
            else:
                min_prob = 1.

        if diversity_score:
            # get prefixes
            pre = [r[-1][len(start_token):] for r in prev_beam]
            base = set(pre[0])
            diversity_scores = []
            # score for first entry
            if use_log:
               diversity_scores.append(0.)
            else:
               diversity_scores.append(1.)
            if len(pre) > 1:
                for pre_i in pre[1:]:
                    s = set(pre_i)
                    union = base | s
                    # number of new things + (- number of repetitions)
                    sc = (len(union) - len(base)) - (len(pre_i) - len(s))
                    # update it
                    base = union
                    if use_log:
                        diversity_scores.append(sc)
                    else:
                        diversity_scores.append(np.exp(sc))

        # Add complete sentences that do not yet have the best probability to the current beam, the rest prepare to add more words to them.
        for ni, (prefix_score, complete, prefix_prob, prefix) in enumerate(prev_beam):
            if complete == True:
                curr_beam.add(prefix_score, True, prefix_prob, prefix)
            else:
                # Get probability of each possible next word for the incomplete prefix
                for (next_prob, next_word) in probabilities_function(prefix):
                    # use eps tolerance to avoid log(0.) issues
                    if next_prob > eps:
                        n = next_prob
                    else:
                        n = eps

                    # score is renormalized prob
                    if use_log:
                        if length_score:
                            score = prefix_prob + np.log(n) + np.log(len(prefix)) - min_prob
                        else:
                            score = prefix_prob + np.log(n) - min_prob
                        if diversity_score:
                            score = score + diversity_scores[ni]
                        prob = prefix_prob + np.log(n)
                    else:
                        if length_score:
                            score = (prefix_prob * n * len(prefix)) / min_prob
                        else:
                            score = (prefix_prob * n) / min_prob
                        if diversity_score:
                            score = score * diversity_scores[ni]
                        prob = prefix_prob * n

                    if end_token_is_seq:
                        left_cmp = prefix[-len(end_token) + 1:] + [next_word]
                        right_cmp = end_token
                    else:
                        left_cmp = next_word
                        right_cmp = end_token

                    if left_cmp == right_cmp:
                        # If next word is the end token then mark prefix as complete
                        curr_beam.add(score, True, prob, prefix + [next_word])
                    else:
                        curr_beam.add(score, False, prob, prefix + [next_word])

        # Get all prefixes in beam sorted by probability
        sorted_beam = sorted(curr_beam)

        any_removals = False
        while True:
            # Get highest probability prefix - heapq is sorted in ascending order
            (best_score, best_complete, best_prob, best_prefix) = sorted_beam[-1]
            if best_complete == True or len(best_prefix) - 1 == clip_len:
                # If most probable prefix is a complete sentence or has a length that
                # exceeds the clip length (ignoring the start token) then return it
                # yield best without start token, along with probability
                if start_token_is_seq:
                    skip = len(start_token)
                else:
                    skip = 1

                if end_token_is_seq:
                    stop = None
                else:
                    stop = -1

                yield (best_prefix[skip:stop], best_score, best_prob)
                sorted_beam.pop()
                completed_beams += 1
                any_removals = True
                # If there are no more sentences in the beam then stop checking
                if len(sorted_beam) == 0:
                    break
            else:
                break

        if any_removals == True:
            if len(sorted_beam) == 0:
                break
            else:
                prev_beam = Beam(beam_width - completed_beams, sorted_beam, use_log,
                                 stochastic, temperature, random_state)
        else:
            prev_beam = curr_beam

# Reduce memory on python 2
if sys.version_info < (3, 0):
    range = xrange


def train_char_lm(fname, order=4, temperature=1.0):
    data = file(fname).read()
    lm = defaultdict(Counter)
    pad = "~" * order
    data = pad + data

    for i in range(len(data) - order):
        history, char = data[i:i + order], data[i + order]
        lm[history][char] += 1

    def normalize(counter):
        # Use a proper softmax with temperature
        t = temperature
        ck = counter.keys()
        cv = counter.values()
        # Keep it in log space
        s = float(sum([pi for pi in cv]))
        # 0 to 1 to help numerical issues
        p = [pi / s for pi in cv]
        # log_space
        p = [pi / float(t) for pi in p]
        mx = max(p)
        # log sum exp
        s_p = mx + np.log(sum([np.exp(pi - mx) for pi in p]))
        # Calculate softmax in a hopefully more stable way
        # s(xi) = exp ^ (xi / t) / sum exp ^ (xi / t)
        # log s(xi) = log (exp ^ (xi / t) / sum exp ^ (xi / t))
        # log s(xi) = log exp ^ (xi / t) - log sum exp ^ (xi / t)
        # with pi = xi / t
        # with s_p = log sum exp ^ (xi / t)
        # log s(xi) = pi - s_p
        # s(xi) = np.exp(pi - s_p)
        p = [np.exp(pi - s_p) for pi in p]
        return [(pi, ci) for ci, pi in zip(ck, p)]

    outlm = {hist: normalize(chars) for hist, chars in lm.iteritems()}
    return outlm


def generate_letter(lm, history, order, stochastic, random_state):
    history = history[-order:]
    dist = lm[history]
    if stochastic:
        x = random_state.rand()
        for v, c in dist:
            x = x - v
            if x <= 0:
                return c
        # randomize choice if it all failed
        li = list(range(len(dist)))
        random_state.shuffle(li)
        _, c = dist[li[0]]
    else:
        probs = np.array([d[0] for d in dist])
        ii = np.argmax(probs)
        _, c = dist[ii]
    return c


def step_text(lm, order, stochastic, random_seed, history=None, end=None,
              beam_width=1, n_letters=1000, verbose=False):
    # beam_width argument is ignored, as is end, and verbose
    if history is None or history == "<START>":
        history = "~" * order
    else:
        history = "".join(history).decode("string_escape")

    out = []
    random_state = np.random.RandomState(random_seed)
    for i in range(n_letters):
        c = generate_letter(lm, history, order, stochastic, random_state)
        history = history[-order:] + c
        out.append(c)
    # return list to match beam_text
    return ["".join(out)]


def beam_text(lm, order, stochastic, random_seed, history=None,
              end=None, beam_width=10, n_letters=1000, verbose=False):
    def pf(prefix):
        history = prefix[-order:]
        # lm wants key as a single string
        k = "".join(history).decode("string_escape")
        # sometimes the distribution "dead-ends"...
        try:
            dist = lm[k]
        except KeyError:
            alt_keys = [i for i in lm.keys()
                        if "".join(prefix[-order:-1]) in i
                        and "".join(prefix[-order-1:-1]) != i]
            # if no alternates, start from a random place
            if len(alt_keys) == 0:
                # choose a key at semi-random
                ak = lm.keys()
                dist = lm[ak[random_seed % len(ak)]]
            else:
                dist = lm[alt_keys[0]]
        return dist

    if history is None or history == "<START>":
        start_token = ["~"] * order
    else:
        start_token = history
        if len(start_token) != order:
            raise ValueError("Start length must match order setting of {}! {} is length {}".format(order, history, len(history)))

    if end is None:
        end_token = "<EOS>"
    else:
        end_token = end

    random_state = np.random.RandomState(random_seed)
    b = beamsearch(pf, beam_width, start_token=start_token,
                   end_token=end_token,
                   clip_len=n_letters,
                   stochastic=stochastic,
                   diversity_score=True,
                   random_state=random_state)
    # it is a generator but do this so that function prototypes are consistent
    all_r = []
    for r in b:
        all_r.append((r[0], r[1], r[2]))

    # reorder so final scoring is matched (rather than completion order)
    all_r = sorted(all_r, key=lambda x: x[1])

    returns = []
    for r in all_r:
        s_r = "".join(r[0])
        if verbose:
            s_r = s_r + "\nScore: {}".format(r[1]) + "\nProbability: {}".format(r[2])
        returns.append(s_r)
    # return list of all beams, ordered by score
    return returns


if __name__ == "__main__":
    default_order = 6
    default_temperature = 1.0
    default_beamwidth = 10
    default_start = "<START>"
    default_end = "<EOS>"
    default_beamwidth = 10
    default_decoder = 0
    default_randomseed = 1999
    default_maxlength = 500
    default_cache = 1
    default_print = 1
    default_verbose = 1

    # TODO: Faster cache
    parser = argparse.ArgumentParser(description="A Markov chain character level language model with beamsearch decoding",
                                     epilog="Simple usage:\n    python minimal_beamsearch.py shakespeare_input.txt -o 10\nFull usage:\n    python minimal_beamsearch.py shakespeare_input.txt -o 10 -d 0 -s 'HOLOFERNES' -e 'crew?\\n' -r 2177",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("filepath", help="Path to file to use for language modeling. For an example file, try downloading\nhttp://cs.stanford.edu/people/karpathy/char-rnn/shakespeare_input.txt", default=None)
    parser.add_argument("-o", "--order", help="Markov chain order, higher will make better text but takes longer to process.\nDefault {}".format(default_order), default=default_order)
    parser.add_argument("-t", "--temperature", help="Temperature for Markov chain softmax, higher is more random, lower more static.\nDefault {}".format(default_temperature), default=default_temperature)
    parser.add_argument("-d","--decoder", help="Decoder for Markov chain, 0 is stochastic beamsearch, 1 is argmax beamsearch, 2 is sampled next-step, 3 is argmax next-step.\nDefault {}".format(default_decoder), default=default_decoder)
    parser.add_argument("-b", "--beamwidth", help="Beamwidth to use for beamsearch.\nDefault {}".format(default_beamwidth), default=default_beamwidth)
    parser.add_argument("-r", "--randomseed", help="Random seed to initialize randomness.\nDefault {}".format(default_randomseed), default=default_randomseed)
    parser.add_argument("-s", "--starttoken", help="Start sequence token. Can be a string such as 'hello\\n', extra padding will be inferred from the data.\nDefault {}".format(default_start), default=default_start)
    parser.add_argument("-e", "--endtoken", help="Random seed to initialize randomness. Can be a string such as 'goodbye\\n'.\nDefault {}".format(default_end), default=default_end)
    parser.add_argument("-m", "--maxlength", help="Max generation length.\nDefault {}".format(default_maxlength), default=default_maxlength)
    parser.add_argument("-c", "--cache", help="Whether to cache models for faster use.\nDefault {}".format(default_cache), default=default_cache)
    parser.add_argument("-a", "--allbeams", help="Print all beams for beamsearch, 0 for top only, 1 for all.\nDefault {}".format(default_print), default=default_print)
    parser.add_argument("-v", "--verbose", help="Print the score and probability for beams.\nDefault {}".format(default_verbose), default=default_verbose)

    args = parser.parse_args()

    if args.filepath is None:
        raise ValueError("No text filepath provided!")
    else:
        fpath = args.filepath
        if not os.path.exists(fpath):
            raise ValueError("Unable to find file at %s" % fpath)

    decoder_settings = [0, 1, 2, 3]
    decoder = int(args.decoder)

    # TODO: gumbel-max in stochastic beam decoder...?
    beam_width = int(args.beamwidth)
    temperature = float(args.temperature)
    random_seed = int(args.randomseed)
    maxlength = int(args.maxlength)
    allbeams = int(args.allbeams)
    verbose = int(args.verbose)

    order = int(args.order)
    if order < 1:
        raise ValueError("Order must be greater than 1! Was set to {}".format(order))

    cache = int(args.cache)
    if cache not in [0, 1]:
        raise ValueError("Cache must be either 0 (no save) or 1 (save)! Was set to {}".format(cache))

    start_token = args.starttoken.decode("string_escape")
    if start_token != default_start:
        user_start_token = True
    else:
        user_start_token = False

    end_token = args.endtoken.decode("string_escape")
    if end_token != default_end:
        user_end_token = True
    else:
        user_end_token = False

    if decoder == 0:
        # stochastic beam
        stochastic = True
        decode_fun = beam_text
        type_tag = "Stochastic beam search, beam width {}, Markov order {}, temperature {}, seed {}".format(beam_width, order, temperature, random_seed)
    elif decoder == 1:
        # argmax beam
        stochastic = False
        decode_fun = beam_text
        type_tag = "Argmax beam search, beam width {}, Markov order {}".format(beam_width, order)
    elif decoder == 2:
        # stochastic next-step
        stochastic = True
        decode_fun = step_text
        type_tag = "Stochastic next step, Markov order {}, temperature {}, seed {}".format(order, temperature, random_seed)
    elif decoder == 3:
        # argmax next-step
        stochastic = False
        decode_fun = step_text
        type_tag = "Argmax next step, Markov order {}".format(order)
    else:
        raise ValueError("Decoder must be 0, 1, 2, or 3! Was set to {}".format(decoder))

    # only things that affect the language model are training data, temperature, order
    cached_name = "model_{}_t{}_o{}.pkl".format("".join(fpath.split(".")[:-1]), str(temperature).replace(".", "pt"), order)
    if cache == 1 and os.path.exists(cached_name):
        print("Found cached model at {}, loading...".format(cached_name))
        start_time = time.time()
        with open(cached_name, "rb") as f:
            lm = pickle.load(f)
        """
        # codec troubles :(
        with open(cached_name, "r") as f:
            lm = json.load(f, encoding="latin1")
        """
        stop_time = time.time()
        print("Time to load: {} s".format(stop_time - start_time))
    else:
        start_time = time.time()
        lm = train_char_lm(fpath, order=order,
                           temperature=temperature)
        stop_time = time.time()
        print("Time to train: {} s".format(stop_time - start_time))
        if cache == 1:
            print("Caching model now...")
            with open(cached_name, "wb") as f:
                pickle.dump(lm, f)
            """
            # codec troubles :(
            with open(cached_name, "w") as f:
                json.dump(lm, f, encoding="latin1")
            """
            print("Caching complete!")

    # All this logic to handle/match different start keys
    rs = np.random.RandomState(random_seed)
    if user_start_token:
        if len(start_token) > order:
            start_token = start_token[-order:]
            print("WARNING: specified start token larger than order, truncating to\n{}".format(start_token))

        if len(start_token) <= order:
            matching_keys = [k for k in lm.keys() if k.endswith(start_token)]
            all_keys = [k for k in lm.keys()]
            while True:
                if len(matching_keys) == 0:
                    rs.shuffle(all_keys)
                    print("No matching key for `{}` in language model!".format(start_token))
                    print("Please enter another one (suggestions in backticks)\n`{}`\n`{}`\n`{}`)".format(all_keys[0], all_keys[1], all_keys[2]))
                    line = raw_input('Prompt ("Ctrl-C" to quit): ')
                    line = line.strip()
                    if len(line) == 0:
                        continue
                    else:
                        start_token = line
                        matching_keys = [k for k in lm.keys() if k.endswith(start_token)]
                else:
                    break

        if len(start_token) < order:
            # choose key at random
            matching_keys = [k for k in lm.keys() if k.endswith(start_token)]
            rs.shuffle(matching_keys)
            start_token = matching_keys[0]
            print("WARNING: start key shorter than order, set to\n`{}`".format(start_token))

        start_token = list(start_token)

    if user_end_token:
        end_token = list(end_token)
    if allbeams == 0:
        return_count = 1
    elif allbeams == 1:
        pass
    else:
        raise ValueError("Unknown setting for allbeams {}".format(allbeams))

    if verbose == 0:
        verbose = False
    elif verbose == 1:
        verbose = True
    else:
        raise ValueError("Unknown setting for verbose {}".format(verbose))

    start_time = time.time()
    all_o = decode_fun(lm, order, stochastic, random_seed, history=start_token,
                       end=end_token, beam_width=beam_width,
                       n_letters=maxlength, verbose=verbose)
    stop_time = time.time()

    print(type_tag)
    print("Time to decode: {} s".format(stop_time - start_time))
    print("----------")

    if allbeams == 0:
        all_o = [all_o[0]]

    for n, oi in enumerate(all_o):
        if len(all_o) > 1:
            if n == 0:
                print("BEAM {} (worst score)".format(n + 1))
            elif n != (len(all_o) - 1):
                print("BEAM {}".format(n + 1))
            else:
                print("BEAM {} (best score)".format(n + 1))
            print("----------")
        if user_start_token:
            print("".join(start_token) + oi)
        else:
            print(oi)
        print("----------")
