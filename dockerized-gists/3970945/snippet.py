#-*-coding: utf-8 -*-

'''

    This module represents the FriendsRecommender system for recommending
    new friends based on friendship similarity and state similarity.

'''
__author__ = 'Marcel Caraciolo <caraciol@gmail.com>'


from mrjob.job import MRJob


def combinations(iterable, r):
    """
    Implementation of itertools combinations method.
    Re-implemented here because of import issues in Amazon Elastic MapReduce.
    Was just easier to do this thanbootstrap.
    More info here:
    http://docs.python.org/library/itertools.html#itertools.combinations

    Input/Output:

    combinations('ABCD', 2) --> AB AC AD BC BD CD
    combinations(range(4), 3) --> 012 013 023 123
    """
    pool = tuple(iterable)
    n = len(pool)
    if r > n:
        return
    indices = range(r)
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != i + n - r:
                break
        else:
            return
        indices[i] += 1
        for j in range(i + 1, r):
            indices[j] = indices[j - 1] + 1
        yield tuple(pool[i] for i in indices)


TOP_N = 10


class FriendsRecommender(MRJob):

    def steps(self):
        return [self.mr(self.map_input, self.group_by_keys),
                self.mr(None, self.score_similarities),
                self.mr(None, self.top_recommendations)]

    def map_input(self, key, line):
        input = line.split(';')
        user_id, state, friend_ids = input[0], input[1], input[2:]
        for i in xrange(len(friend_ids)):
            f1 = friend_ids[i]
            yield ('f', f1), (user_id, 1, state, friend_ids)

        if state != 'None':
            yield ('s', state), (user_id, 1, state, friend_ids)

    def group_by_keys(self, type_and_key, values):
        final_list = list(values)

        key_type, key = type_and_key

        #pass friends through
        if key_type == 'f':
            for itemA, itemB in combinations(final_list, 2):
                user_idA, countA, stateA, f_idsA = itemA
                user_idB, countB, stateB, f_idsB = itemB
                union = set(f_idsA).union(f_idsB)
                if user_idB not in f_idsA:
                    yield (user_idA, user_idB), ('f', 1.0 / len(union))
                if user_idA not in f_idsB:
                    yield (user_idB, user_idA), ('f', 1.0 / len(union))
            return

        assert key_type == 's'

        for itemA, itemB in combinations(final_list, 2):
                user_idA, countA, stateA, f_idsA = itemA
                user_idB, countB, stateB, f_idsB = itemB
                if user_idB not in f_idsA:
                    yield (user_idA, user_idB), ('s', 1.0)
                if user_idA not in f_idsB:
                    yield (user_idB, user_idA), ('s', 1.0)

    def score_similarities(self, key, values):
        user_id, rec_id = key
        f_total = 0.0
        s_total = 0.0
        similarities = (list(values))
        for k, score in similarities:
            if k == 'f':
                f_total += score
            else:
                s_total += score

        f_similarity = (0.7 * f_total) + (0.3 * s_total)

        yield user_id, (rec_id, f_similarity)

    def top_recommendations(self, key, values):
        recommendations = []
        for idx, (item, score) in enumerate(values):
            recommendations.append((item, score))

        yield key, sorted(recommendations, key=lambda k: -k[1])[:TOP_N]


if __name__ == '__main__':
    FriendsRecommender.run()
