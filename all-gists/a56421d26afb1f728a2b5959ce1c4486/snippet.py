#!/usr/bin/python3

from cnn import cnn
import hyperopt


def objective(args):

    params = cnn.ExperimentParameters()

    params.c1_size_filter = args['c1_size_filter']
    params.c1_num_features = args['c1_num_features']
    params.c2_size_filter = args['c2_size_filter']
    params.c2_num_features = args['c2_num_features']
   
    loss = cnn.train(params)
    
    return loss


def optimize():

    space = {
        'c1_size_filter': hyperopt.hp.choice('c1_size_filter', [3, 5, 7]),
        'c2_size_filter': hyperopt.hp.choice('c2_size_filter', [3, 5, 7]),
        'c1_num_features': hyperopt.hp.choice('c1_num_features', [4, 8, 16, 32]),
        'c2_num_features': hyperopt.hp.choice('c2_num_features', [4, 8, 16, 32])
    }

    best_model = hyperopt.fmin(objective, space, algo=hyperopt.tpe.suggest, max_evals=150)

    print(best_model)
    print(hyperopt.space_eval(space, best_model))

    
if __name__ == '__main__':
    optimize()