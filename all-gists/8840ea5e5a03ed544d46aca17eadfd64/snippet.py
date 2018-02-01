import json
import numpy as np

from collections import OrderedDict


def generate_mdp(T, R, gamma=0.75):
    """Generate an MDP from the provided arrays and gamma value."""
    act1 = {"id": 0, "transitions": []}
    act2 = {"id": 1, "transitions": []}
    names = ("id", "probability", "reward", "to")
    init_vals = (0, 0, 0, 0)
    ids = [i for i in range(30)]
    mdp = OrderedDict()
    mdp["gamma"] = gamma
    mdp["states"] = [{
        "id": id_num,
        "actions": [
            OrderedDict(sorted(act1.items(), key=lambda t: t[0])),
            OrderedDict(sorted(act2.items(), key=lambda t: t[0]))
        ]
    } for id_num in ids]
    for i in range(30):
        mdp["states"][i]["actions"][0]["transitions"] = [
            OrderedDict(zip(names, init_vals)) for _ in range(30)
        ]
        mdp["states"][i]["actions"][1]["transitions"] = [
            OrderedDict(zip(names, init_vals)) for _ in range(30)
        ]
        for j in range(30):
            mdp["states"][i]["actions"][0]["transitions"][j]["id"] = j
            mdp["states"][i]["actions"][1]["transitions"][j]["id"] = j
            mdp["states"][i]["actions"][0]["transitions"][j]["probability"] = round(
                T[0, i, j], 2)
            mdp["states"][i]["actions"][1]["transitions"][j]["probability"] = round(
                T[1, i, j], 2)
            mdp["states"][i]["actions"][0]["transitions"][j]["reward"] = R[0, i, j]
            mdp["states"][i]["actions"][1]["transitions"][j]["reward"] = R[1, i, j]
            mdp["states"][i]["actions"][0]["transitions"][j]["to"] = j
            mdp["states"][i]["actions"][1]["transitions"][j]["to"] = j


    ans = json.dumps(mdp, separators=(',', ':'))
    return ans
    
def generate_arrays(states=30, actions=2):
    """Generate arrays to feed to the MDP parser."""
    T = np.zeros(shape=(actions, states, states))
    R = np.zeros(shape=(actions, states, states))

    # TODO: Your code to create an MDP that is difficult for PI

    return T, R


if __name__ == '__main__':
    T, R = generate_arrays()
    mdp_str = generate_mdp(T, R)
    print(mdp_str)