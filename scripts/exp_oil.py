import numpy as np
from matplotlib import pyplot as plt
from matplotlib import collections
from sklearn.decomposition import PCA, KernelPCA  # For X initialization
import pandas as pd
from algorithms.simple_gplvm import simple_gplvm
from algorithms.fast_gplvm import GPLVM
import time

np.random.seed(1)

def load_oil_dataset(samples):
    path = 'data/oil.txt'
    f = open(path, 'r')
    labels = list()
    observations = list()
    j = 0
    for line in f:
        data = line.split(" ")
        labels.append(int(data[0]))
        observations.append(np.zeros(12))
        for i, p in enumerate(data[1:-1]):
            _, t = p.split(":")
            observations[j][i] = t
        j += 1

    Y = np.asarray(observations)
    idx = np.random.randint(Y.shape[0], size=samples)

    return Y.shape[0], 3, 12, Y[idx, :], np.asarray(labels)[idx]

def z(x,y):
    return x**2 + y**2

def plot(pca, gp_vals, labels=None, name=""):
    ''' Simple scatter of 2d data in same figure
    '''
    fig, ax = plt.subplots(nrows=1, ncols=2,figsize=(8,6),sharex=True, sharey=True) 
    if labels is not None:
        colors = ["blue","red","green","black","yellow","pink","purple","orange","brown", "darkred"]
        for i, label in enumerate(np.unique(labels)):
            pca_i = pca[labels == label]
            gp_i = gp_vals[labels == label]
            ax[0].scatter(pca_i[:, 0], pca_i[:, 1], c=colors[i], label=label, zorder=1)
            ax[1].scatter(gp_i[:, 0], gp_i[:, 1], c=colors[i], label=label, zorder=1)
    else:
        ax[0].scatter(pca[:, 0], pca[:, 1])
        ax[1].scatter(gp_vals[:, 0], gp_vals[:, 1])
    ax[0].grid()
    ax[0].set_title("PCA oil data")
    ax[1].grid()
    ax[1].set_title("GPLVM oil data")
    xmin, xmax, ymin, ymax = plt.axis()
    x= np.linspace(xmin,xmax,1000)
    y = np.linspace(ymin,ymax,1000)
    X, Y = np.meshgrid(x, y)
    Z = z(X, Y)
    # ax[0].contourf(X,Y,Z,300, cmap='Greys', zorder=0)
    fig.legend(np.unique(labels))
    fig.savefig("figures/oil/" + name + "_result_" + str(time.time()) + ".png")
    # plt.show()

if __name__ == "__main__":
    N, n_classes, D, observations, labels = load_oil_dataset(samples=200)

    # Simple
    # gp_vals = simple_gplvm(Y=observations, experiment_name="simple_oil")  # Compute values
    # pca = PCA(n_components=2).fit_transform(observations)
    # plot(pca, gp_vals, labels, name="simple_oil")

    # Fast
    for active_set_size in [175, 200]:
        name = "oil_size_" + str(active_set_size) + "_exp"
        gplvm = GPLVM(active_set_size=active_set_size, name=name)
        gp_vals = gplvm.fit_transform(observations, iterations=300, save=True)
        pca = PCA(n_compone100, E
