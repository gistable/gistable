# -*- coding: utf-8 -*-
"""
Created on Fri Dec 02 22:07:31 2016

@author: Dave Ho
"""

### Question: You are given a final soccer score. Compute all the different combinations
### that can lead up to that score
#>>>pScore((1, 1))
#>>>[[(0, 0), (1, 0), (1, 1)], [(0, 0), (0, 1), (1, 1)]]
#
#

def create_score_graph(current_score, final_score, graph):
    (I, J) = final_score
    (i, j) = current_score
    if i < I:
        if (i+1, j) not in graph[(i, j)]:
            graph[(i, j)].append((i+1, j))
        if (i+1, j) not in graph.keys():
            graph[(i+1, j)] = []
        create_score_graph((i+1, j), final_score, graph)
    if j < J:
        if (i, j+1) not in graph[(i, j)]:
            graph[(i, j)].append((i, j+1))
        if (i, j+1) not in graph.keys():
            graph[(i, j+1)] = []
        create_score_graph((i, j+1), final_score, graph)

def pScores(current_score, final_score, graph):
    if current_score == final_score:
        return [[current_score]]
    result = [] 
    for score in graph[current_score]:
        for possibility in pScores(score, final_score, graph):
            result.append([current_score] + possibility)
    return result


def choose(n, r):
    if r == 1:
        result = []
        for i in n:
            result.append([i])
        return result
    result = []
    for i in range(0, (len(n)-r)+1):
        for possibility in choose(n[i+1:], r-1):
            result.append([n[i]]+possibility)
    return result

def pScore(final_score):
    result = []
    for possibility in choose(range(1, final_score[0]+final_score[1]+1), final_score[0]):
        tmp = [(0, 0)]
        for i in range(1, final_score[0]+final_score[1]+1):
            if i in possibility:
                tmp.append((tmp[-1][0]+1, tmp[-1][1]))
            else:
                tmp.append((tmp[-1][0], tmp[-1][1]+1))
        result.append(tmp)
    return result

graph = {(0,0): []}
final_score = (3, 2)
start_score = (0, 0)
create_score_graph(start_score, final_score, graph)