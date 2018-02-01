import numpy as np
import sklearn.datasets
import sklearn.ensemble
import xgboost

N_TRAIN = 60000
NS_ITERATIONS = [2 ** k for k in range(8)]

MODELS = [
    ('RandomForestClassifier', sklearn.ensemble.RandomForestClassifier, {'n_jobs': -1}),
    ('ExtraTreesClassifier', sklearn.ensemble.ExtraTreesClassifier, {'n_jobs': -1}),
    ('XGBClassifier', xgboost.XGBClassifier, {}),
]

"""
MODELS = [
    ('XGBClassifier, max_depth={}'.format(d), xgboost.XGBClassifier, {'max_depth': d})
    for d in [4 ** e for e in range(4)]
]
"""


def doit(shuffled):
    mnist = sklearn.datasets.fetch_mldata('MNIST original', data_home=".")
    x, y = mnist.data, mnist.target

    x_train, x_test = x[:N_TRAIN], x[N_TRAIN:]
    y_train, y_test = y[:N_TRAIN], y[N_TRAIN:]
    if shuffled:
        y_train = np.random.permutation(y_train)
    
    result = []
    for model_name, model_class, model_kwargs in MODELS:
        score_train, score_test = [], []
        for n_iterations in NS_ITERATIONS:
            model_obj = model_class(n_estimators=n_iterations, **model_kwargs)
            model_obj.fit(x_train, y_train)
            score_train.append(model_obj.score(x_train, y_train))
            score_test.append(model_obj.score(x_test, y_test))
        result.append((model_name, score_train, score_test))

    return result


def main():
    import matplotlib as mpl
    mpl.use('Agg')
    import matplotlib.pyplot as plt
    import seaborn as sns
    fig, axs = plt.subplots(2, 1)
    cp = sns.color_palette()

    for shuffled in range(2):
        result = doit(shuffled)
        print(result)

        ax = axs[shuffled]
        ax.set_title(['Correct labels', 'Random labels'][shuffled])
        ax.set_ylabel('Accuracy')
        ax.set_xlabel('Number of trees')
        ax.set_xscale('log', basex=2)
        ax.set_ylim(0, 1)

        for i, row in enumerate(result):
            model_name, score_train, score_test = row
            ax.plot(NS_ITERATIONS, score_train, linestyle='solid', marker='o', color=cp[i], lw=2, label='{}, train'.format(model_name), alpha=0.8)
            ax.plot(NS_ITERATIONS, score_test, linestyle='dashed', marker='s', color=cp[i], lw=2, label='{}, test'.format(model_name), alpha=0.8)
        
        ax.legend(loc="upper right", frameon=False, bbox_to_anchor=(2, 1))

    plt.tight_layout()
    plt.suptitle('Fitting tree-based models to random labels on MNIST', fontsize=20)
    fig.subplots_adjust(right=0.5, top=0.85)
    fig.savefig('out.png', dpi=200)


if __name__ == '__main__':
    main()