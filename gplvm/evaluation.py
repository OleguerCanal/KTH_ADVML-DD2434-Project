import numpy as np
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from fast_gplvm import GPLVM
from sklearn.decomposition import PCA  # For X initialization
from matplotlib import pyplot as plt
from sklearn.metrics import confusion_matrix
from exp_digits import load_digit_dataset
from exp_mice import load_genes_dataset
from exp_oil import load_oil_dataset

class Evaluation:

    def __init__(self, pca_data, gplvm_data, labels):
        self.labels = labels
        self.N = pca_data.shape[0]
        self.unique_labels = np.unique(labels)
        self.n_classes = len(self.unique_labels)
        self.gp_vals = gplvm_data
        self.pca_vals = pca_data

    def cluster(self, algorithm):
        # Valid algorithms are 'kmeans' and 'gmm'
        # Compute K-means for GPLVM and PCA
        if algorithm == 'kmeans':
            gp_clustering = KMeans(n_clusters=self.n_classes).fit(self.gp_vals)
            pca_clustering = KMeans(n_clusters=self.n_classes).fit(self.pca_vals)
        elif algorithm == 'gmm':
            gp_clustering = GaussianMixture(n_components=self.n_classes).fit(self.gp_vals)
            pca_clustering = GaussianMixture(n_components=self.n_classes).fit(self.pca_vals)
        else:
            raise Exception('Unknown clustering algorithm: '+algorithm)

        self.gp_assignments = gp_clustering.predict(self.gp_vals)
        gp_clusters = self.__label_clusters(self.gp_assignments, self.labels)
        self.gp_assignments = np.array([gp_clusters[i] for i in self.gp_assignments]).astype(int)

        self.pca_assignments = pca_clustering.predict(self.pca_vals) 
        pca_clusters = self.__label_clusters(self.pca_assignments, self.labels)
        self.pca_assignments = np.array([pca_clusters[i] for i in self.pca_assignments]).astype(int)

    def __label_clusters(self, assigned_labels, true_lables):
        # Assign to each lable the cluster that contains the highest share of its points
        cluster_assignments = np.empty(self.n_classes)
        for k in range(self.n_classes):
            total = np.sum(np.where(assigned_labels == k, 1, 0))
            scores = np.zeros(self.n_classes)
            for i, label in enumerate(self.unique_labels):
                scores[i] = np.sum(np.where((assigned_labels == k) * (true_lables == label), 1, 0))
            if total != 0:
                scores /= total 
            cluster_assignments[k] = np.argmax(scores)
        return cluster_assignments

    def get_confusion_matrices(self):
        gp_confusion_matrix = confusion_matrix(labels, [self.unique_labels[i]
                                                        for i in self.gp_assignments])
        pca_confusion_matrix = confusion_matrix(labels, [self.unique_labels[i]
                                                         for i in self.pca_assignments])
        return gp_confusion_matrix, pca_confusion_matrix

    def compute_metrics(self):
        gp_confusion_matrix, pca_confusion_matrix = self.get_confusion_matrices()
        names = ['gplvm', 'pca']
        metrics_dict = {}
        for n, cm in enumerate([gp_confusion_matrix, pca_confusion_matrix]):
            precisions = np.zeros(self.n_classes)
            recalls = np.zeros(self.n_classes)
            for i, label in enumerate(self.unique_labels):
                weight = np.sum(np.where(self.labels == label, 1, 0)) / self.labels.shape[0]
                precisions[i] = cm[i, i] * weight / np.sum(cm[:, i]) if np.sum(cm[:, i]) != 0 else 0
                recalls[i] = cm[i, i] * weight / np.sum(cm[i, :]) if np.sum(cm[i, :]) != 0 else 0
            avg_precision = np.mean(precisions)
            avg_recall = np.mean(recalls)
            metrics_dict[names[n]] = {'avg_precision': avg_precision, 'avg_recall': avg_recall}
        return metrics_dict 
    
    def plot(self):
        colors = ["blue","red","green","black","yellow","pink","purple","orange","brown", "grey"]
        fig, axes = plt.subplots(2,2)

        # Plot pca and gplvm
        for i, label in enumerate(self.unique_labels):
            indices = np.array(self.labels == label)
            pca_points = self.pca_vals[indices]
            axes[0, 0].scatter(pca_points[:,0], pca_points[:,1], c=colors[i])
            axes[0, 0].set_title('PCA')

            gplvm_points = self.gp_vals[indices]
            axes[1, 0].scatter(gplvm_points[:, 0], gplvm_points[:, 1], c=colors[i])
            axes[1, 0].set_title('GPLVM')

        for k in range(len(self.unique_labels)):
            indices = np.array(self.pca_assignments == k)
            pca_k_points = self.pca_vals[indices]
            axes[0, 1].scatter(pca_k_points[:,0], pca_k_points[:,1], c=colors[k])
            axes[0, 1].set_title('Clustering reconstruction')

            indices = np.array(self.gp_assignments == k)
            gplvm_k_points = self.gp_vals[indices]
            axes[1, 1].scatter(gplvm_k_points[:,0], gplvm_k_points[:,1], c=colors[k])
            axes[1, 1].set_title('Clustering reconstruction') 
        plt.show()

    def plot_confusion_matrix():
        fig, axes = plt.subplots(1,2)
        confusion_matrices = self.get_confusion_matrices()
        for idx, cm in enumerate(confusion_matrices):
            axes[0,idx].imshow(cm,interpolation='none',cmap='Blues')
            for (i, j), z in np.ndenumerate(cm):
                axes[0, idx].text(j, i, z, ha='center', va='center')
            axes[0, idx].xlabel("kmeans label")
            axes[0, idx].ylabel("truth label")
            axes[0, idx].title(title)
        plt.show()
 
if __name__ == "__main__":
    np.random.seed(1)

    #N, n_classes, D, observations, labels = load_digit_dataset(500)
    #N, n_classes, D, observations, labels = load_genes_dataset(437, 48)
    #N, n_classes, D, observations, labels = load_oil_dataset(samples=200)
    #print('Number observations: ', observations.shape[0])
    #print('Number dimensions: ', D)

    faces_dict_pca = np.load('/home/fedetask/Desktop/Faces results-20200114T181752Z-001/Faces results/results_kernel_pca_poly.npy', allow_pickle=True).item()
    labels = faces_dict_pca['labels']
    pca_data = faces_dict_pca['data']

    faces_dict_gplvm = np.load('/home/fedetask/Desktop/Faces results-20200114T181752Z-001/Faces results/results_gplvm.npy', allow_pickle=True).item()
    gplvm_data = faces_dict_gplvm['data']
    
    #labels = np.array(labels).reshape(observations.shape[0])

    #pca_data = PCA(n_components=2).fit_transform(observations)
    #gplvm = GPLVM(active_set_size=None)
    #gplvm.load('/home/fedetask/Desktop/digits_250_results/digits_size_250_exp_2020-01-14_15:18:00.651877')
    #gplvm_data = np.load('/home/fedetask/Downloads/mice_full_dataset_final.npy')[:-3].reshape((437,2))
    evaluation = Evaluation(pca_data, gplvm_data, labels)
    #evaluation.load_gplvm('/home/fedetask/Downloads/oil_size_175_exp_2020-01-14_12_59_50.041882')
    #evaluation.gp_vals = np.load('/home/fedetask/Downloads/mice_full_dataset_final.npy')[-3:].reshape((437,2))
    #evaluation.load_gplvm('/home/fedetask/Desktop/digits_250_results/digits_size_250_exp_2020-01-14_15:18:00.651877')
    #evaluation.compute()
    evaluation.cluster(algorithm='gmm')
    evaluation.plot()

    metrics_dict = evaluation.compute_metrics()

    print(metrics_dict)
