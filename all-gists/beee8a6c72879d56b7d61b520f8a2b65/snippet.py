from math import log
import unittest


def dcg_at_k(scores):
    assert scores
    return scores[0] + sum(sc / log(ind, 2) for sc, ind in zip(scores[1:], range(2, len(scores)+1)))

def ndcg_at_k(predicted_scores, user_scores):
    assert len(predicted_scores) == len(user_scores)
    idcg = dcg_at_k(sorted(user_scores, reverse=True))
    return (dcg_at_k(predicted_scores) / idcg) if idcg > 0.0 else 0.0


class TestMetrics(unittest.TestCase):

    def test_dcg_small(self):
        scores = [3, 2]
        self.assertAlmostEqual(dcg_at_k(scores), 5.0)


    def test_dcg_large(self):
        scores = [3, 2, 3, 0, 0, 1, 2, 2, 3, 0]
        self.assertAlmostEqual(dcg_at_k(scores), 9.6051177391888114)


    def test_ndcg(self):
        predicted1 = [.4, .1, .8]
        predicted2 = [.0, .1, .4]
        predicted3 = [.4, .1, .0]
        actual = [.8, .4, .1, .0]
        self.assertAlmostEqual(ndcg_at_k(predicted1, actual[:3]), 0.795, 3)
        self.assertAlmostEqual(ndcg_at_k(predicted2, actual[:3]), 0.279, 3)
        self.assertAlmostEqual(ndcg_at_k(predicted3, actual[:3]), 0.396, 3)
