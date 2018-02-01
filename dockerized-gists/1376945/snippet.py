# -*- encoding: utf-8 -*-
"""
ticket recommendation: concept proof
"""
import pa

tickets = """
Windows環境で日本語を含むパスに対して、File.expand_path が存在しないパスを返すパターンが存在する。
Please backport thread-safe autoloading patch
Ruby 1.9.3 fails to compile in directories with accent in their names
Windows上でFile.utimeにtime_tの負の値を与えるとSEGV
Windows上で \\.\ から始まるデバイスをopenするとクラッシュ
ruby-1.9.3-p0 mswin IO#write still slower than 1.9.2
RSpec 2.7.1 and Ruby 1.9.3
Ruby can't pass test-all (x86_64-darwin11.2.0 built by Xcode 4.2 's clang)
ruby does not compile on Lion with Xcode 4.2
Please backport r33556 (Bug #5243)	
""".strip().split("\n")


def to_feature_vec(data):
    vec_in = pa.create_blank_weight_vec()
    vec_in = pa.tweak_weight_vec(vec_in)
    vec_in = pa.unigram(vec_in, data)
    vec_in = pa.bigram(vec_in, data)
    return vec_in

feature_vecs = dict((t, to_feature_vec(t)) for t in tickets)

weight_vec = pa.create_blank_weight_vec()

def calc_score(ticket):
    return pa.calc_score(feature_vecs[ticket], weight_vec)


def recommend():
    """
    recommend a ticket
    """
    tickets.sort(key=calc_score, reverse=True)
    score = calc_score(tickets[0])
    print tickets[0]


def no():
    global weight_vec
    weight_vec = pa.learn(weight_vec, feature_vecs[tickets[0]], -1)
    recommend()


def ok():
    global weight_vec
    weight_vec = pa.learn(weight_vec, feature_vecs[tickets[0]], 1)
    tickets.pop(0)
    recommend()
    
    
def debug():
    with_score = [(calc_score(t), t) for t in tickets]
    with_score.sort(reverse=True)
    for score, ticket in with_score:
        print "%0.2f %s" % (score, ticket)
