
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import AgglomerativeClustering, KMeans, OPTICS, cluster_optics_dbscan
import scipy.cluster.hierarchy as sch
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn import metrics
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.cm as cm
from mpl_toolkits.mplot3d.axes3d import get_test_data
# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D


def normalize(X):
    min_max_scaler = MinMaxScaler()
    X_normalized = min_max_scaler.fit_transform(X)

    return X_normalized

def standardize(X):
    standard_scaler = StandardScaler()
    X_standardized = standard_scaler.fit_transform(X)

    return X_standardized

def pca_find_features(X, feature_threshold, variance_threshold, n_components=1):
    pca_model = PCA(n_components=n_components)
    X_fit = pca_model.fit(X)
    X_transformed = pca_model.fit_transform(X)
    X_explained = X_fit.explained_variance_ratio_[0:n_components].sum()

    if X_explained < variance_threshold and n_components < feature_threshold:
        return pca_find_features(X, feature_threshold, variance_threshold, n_components=n_components + 1)
    else:
        print('Starting Features: ' + str(X.shape[1]))
        print('Remaining Features: ' + str(n_components))
        print('Variance Explained: ' + str(X_explained))
        return X_transformed

def pca_transform_array(X, feature_threshold, variance_threshold, scaler='normalize'):
    if scaler == 'normalize':
        X = normalize(X)
    elif scaler == 'standardize':
        X = standardize(X)
    else:
        print('PLEASE PICK AN APPROPRIATE SCALER')
    X_transformed = pca_find_features(X, feature_threshold, variance_threshold)
    return X_transformed


def compute_inertia(a, X):
    W = [np.mean(metrics.pairwise_distances(X[a == c, :])) for c in np.unique(a)]
    return np.mean(W)

def graph_elbow_gap(data, clustering, title, k_max=5, n_references=5):
    if len(data.shape) == 1:
        data = data.reshape(-1, 1)
    reference = np.random.rand(*data.shape)
    reference_inertia = []
    for k in range(1, k_max+1):
        local_inertia = []
        for _ in range(n_references):
            clustering.n_clusters = k
            assignments = clustering.fit_predict(reference)
            local_inertia.append(compute_inertia(assignments, reference))
        reference_inertia.append(np.mean(local_inertia))
    
    ondata_inertia = []
    for k in range(1, k_max+1):
        clustering.n_clusters = k
        assignments = clustering.fit_predict(data)
        ondata_inertia.append(compute_inertia(assignments, data))
        
    gap = np.log(reference_inertia)-np.log(ondata_inertia)
    # return gap, np.log(reference_inertia), np.log(ondata_inertia)

    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig.set_size_inches(18, 7)
    ax1.plot(range(1, k_max+1), reference_inertia,
         '-o', label='reference')
    ax1.plot(range(1, k_max+1), ondata_inertia,
            '-o', label='data')
    ax1.set_xlabel('k')
    ax1.set_ylabel('log(inertia)')

    ax2.plot(range(1, k_max+1), gap, '-o')
    ax2.set_ylabel('gap')
    ax2.set_xlabel('k')
    plt.suptitle(title, fontsize=14, fontweight='bold')
    plt.show()


def kmeans_silhouette(X, clusters_list, title):

    for n_clusters in clusters_list:
        # Create a subplot with 1 row and 2 columns
        if X.shape[1] < 3:
            fig, (ax1, ax2) = plt.subplots(1, 2)
            fig.set_size_inches(18, 7)
        else:
            fig = plt.figure(figsize=[18, 7])
            ax1 = fig.add_subplot(121)
            ax2 = fig.add_subplot(122, projection='3d')


        # The 1st subplot is the silhouette plot
        # The silhouette coefficient can range from -1, 1 but in this example all
        # lie within [-0.1, 1]
        ax1.set_xlim([-0.1, 1])
        # The (n_clusters+1)*10 is for inserting blank space between silhouette
        # plots of individual clusters, to demarcate them clearly.
        ax1.set_ylim([0, len(X) + (n_clusters + 1) * 10])

        # Initialize the clusterer with n_clusters value and a random generator
        # seed of 10 for reproducibility.
        clusterer = KMeans(n_clusters=n_clusters, random_state=10)
        cluster_labels = clusterer.fit_predict(X)

        # The silhouette_score gives the average value for all the samples.
        # This gives a perspective into the density and separation of the formed
        # clusters
        silhouette_avg = silhouette_score(X, cluster_labels)
        print("For n_clusters =", n_clusters,
            "The average silhouette_score is :", silhouette_avg)

        # Compute the silhouette scores for each sample
        sample_silhouette_values = silhouette_samples(X, cluster_labels)

        y_lower = 10
        for i in range(n_clusters):
            # Aggregate the silhouette scores for samples belonging to
            # cluster i, and sort them
            ith_cluster_silhouette_values = \
                sample_silhouette_values[cluster_labels == i]

            ith_cluster_silhouette_values.sort()

            size_cluster_i = ith_cluster_silhouette_values.shape[0]
            y_upper = y_lower + size_cluster_i

            color = cm.nipy_spectral(float(i) / n_clusters)
            ax1.fill_betweenx(np.arange(y_lower, y_upper),
                            0, ith_cluster_silhouette_values,
                            facecolor=color, edgecolor=color, alpha=0.7)

            # Label the silhouette plots with their cluster numbers at the middle
            ax1.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))

            # Compute the new y_lower for next plot
            y_lower = y_upper + 10  # 10 for the 0 samples

        ax1.set_title("The silhouette plot for the various clusters.")
        ax1.set_xlabel("The silhouette coefficient values")
        ax1.set_ylabel("Cluster label")

        # The vertical line for average silhouette score of all the values
        ax1.axvline(x=silhouette_avg, color="red", linestyle="--")

        ax1.set_ylim([0, len(X) + (n_clusters + 1) * 10])

        # 2nd Plot showing the actual clusters formed
        colors = cm.nipy_spectral(cluster_labels.astype(float) / n_clusters)
        if X.shape[1] < 3:
            ax2.scatter(X[:, 0], X[:, 1], marker='.', s=30, lw=0, alpha=0.7,
                        c=colors, edgecolor='k')
        else:
            ax2.scatter(X[:, 0], X[:, 1],  X[:, 2], marker='.', s=30, lw=0, alpha=0.7,
                        c=colors, edgecolor='k')

        # Labeling the clusters
        centers = clusterer.cluster_centers_
        # Draw white circles at cluster centers
        if X.shape[1] < 3:
            ax2.scatter(centers[:, 0], centers[:, 1], marker='o',
                        c="white", alpha=1, s=200, edgecolor='k')

            for i, c in enumerate(centers):
                ax2.scatter(c[0], c[1], marker='$%d$' % i, alpha=1,
                            s=50, edgecolor='k')
        else:
            ax2.scatter(centers[:, 0], centers[:, 1], centers[:, 2],marker='o',
                        c="white", alpha=1, s=200, edgecolor='k')

            for i, c in enumerate(centers):
                ax2.scatter(c[0]-.05, c[1]-.05, c[2]-.05, marker='$%d$' % i, alpha=1,
                            s=50, edgecolor='k')

        ax2.set_title("The visualization of the clustered data.")
        ax2.set_xlabel("Feature space for the 1st feature")
        ax2.set_ylabel("Feature space for the 2nd feature")
        if X.shape[1] > 2:
            ax2.set_zlabel("Feature space for the 3rd feature")

        plt.suptitle(("Silhouette analysis for KMeans clustering on " + title +
                    " data with n_clusters = " + str(n_clusters)),
                    fontsize=14, fontweight='bold')

    plt.show()

def graph_optics_neighborhoods(X):
    clust = OPTICS(min_samples=50, xi=.05, min_cluster_size=.05)
    clust.fit(X)

    labels_050 = cluster_optics_dbscan(reachability=clust.reachability_,
                                   core_distances=clust.core_distances_,
                                   ordering=clust.ordering_, eps=0.5)
    labels_200 = cluster_optics_dbscan(reachability=clust.reachability_,
                                    core_distances=clust.core_distances_,
                                    ordering=clust.ordering_, eps=2)

    space = np.arange(len(X))
    reachability = clust.reachability_[clust.ordering_]
    labels = clust.labels_[clust.ordering_]

    plt.figure(figsize=(10, 7))
    G = gridspec.GridSpec(2, 3)
    ax1 = plt.subplot(G[0, :])
    ax2 = plt.subplot(G[1, 0])
    ax3 = plt.subplot(G[1, 1])
    ax4 = plt.subplot(G[1, 2])

    # Reachability plot
    colors = ['g.', 'r.', 'b.', 'y.', 'c.']
    for klass, color in zip(range(0, 5), colors):
        Xk = space[labels == klass]
        Rk = reachability[labels == klass]
        ax1.plot(Xk, Rk, color, alpha=0.3)
    ax1.plot(space[labels == -1], reachability[labels == -1], 'k.', alpha=0.3)
    ax1.plot(space, np.full_like(space, 2., dtype=float), 'k-', alpha=0.5)
    ax1.plot(space, np.full_like(space, 0.5, dtype=float), 'k-.', alpha=0.5)
    ax1.set_ylabel('Reachability (epsilon distance)')
    ax1.set_title('Reachability Plot')

    # OPTICS
    colors = ['g.', 'r.', 'b.', 'y.', 'c.']
    for klass, color in zip(range(0, 5), colors):
        Xk = X[clust.labels_ == klass]
        ax2.plot(Xk[:, 0], Xk[:, 1], color, alpha=0.3)
    ax2.plot(X[clust.labels_ == -1, 0], X[clust.labels_ == -1, 1], 'k+', alpha=0.1)
    ax2.set_title('Automatic Clustering\nOPTICS')

    # DBSCAN at 0.5
    colors = ['g', 'greenyellow', 'olive', 'r', 'b', 'c']
    for klass, color in zip(range(0, 6), colors):
        Xk = X[labels_050 == klass]
        ax3.plot(Xk[:, 0], Xk[:, 1], color, alpha=0.3, marker='.')
    ax3.plot(X[labels_050 == -1, 0], X[labels_050 == -1, 1], 'k+', alpha=0.1)
    ax3.set_title('Clustering at 0.5 epsilon cut\nDBSCAN')

    # DBSCAN at 2.
    colors = ['g.', 'm.', 'y.', 'c.']
    for klass, color in zip(range(0, 4), colors):
        Xk = X[labels_200 == klass]
        ax4.plot(Xk[:, 0], Xk[:, 1], color, alpha=0.3)
    ax4.plot(X[labels_200 == -1, 0], X[labels_200 == -1, 1], 'k+', alpha=0.1)
    ax4.set_title('Clustering at 2.0 epsilon cut\nDBSCAN')

    plt.tight_layout()
    plt.show()

def graph_hierarchical_dendorgram(X, title, color_split=.6):
    Z = sch.linkage(X, method='ward')
    color_threshold = color_split*max(Z[:,2])
    dendrogram = sch.dendrogram(Z, color_threshold=color_threshold)
    plt.title(title)
    plt.show()

def add_kmeans(clusters_list, group, X, results_df):
    for clusters in clusters_list:
        km = KMeans(n_clusters=clusters, random_state=0, n_init=10, algorithm='auto', n_jobs=-1)
        y_km_transform = km.fit_transform(X)
        y_km_labels = km.labels_

        results_df[group + ' ' + str(clusters) + ' K-Means'] = y_km_labels

    return results_df

def add_agglomerative_hierarchical(clusters_list, group, X, results_df):
    
    for idx, clusters in enumerate(clusters_list):
        ah = AgglomerativeClustering(n_clusters=clusters, affinity = 'euclidean', linkage = 'ward')
        
        y_ah_predicted = ah.fit_predict(X)
        y_ah_labels = ah.labels_

        results_df[group + ' ' + str(clusters) + ' Hierarchical'] = y_ah_labels
        
    return results_df


def density_scan(clusters, X, title):


    # create dendrogram
    dendrogram = sch.dendrogram(sch.linkage(X, method='ward'))
    plt.show()
    # create clusters
    ah = AgglomerativeClustering(n_clusters=clusters, affinity = 'euclidean', linkage = 'ward')
    # save clusters for chart
    y_ah_predicted = ah.fit_predict(X)
    y_ah_labels = ah.labels_
    # print('CLUSTERS FOUND:')
    # print(ah.n_clusters_)

    plt.title(title)
    plt.scatter(X[y_ah_predicted ==0,0], X[y_ah_predicted == 0,1], s=100, c='black')
    plt.scatter(X[y_ah_predicted==1,0], X[y_ah_predicted == 1,1], s=100, c='red')
    plt.scatter(X[y_ah_predicted ==2,0], X[y_ah_predicted == 2,1], s=100, c='blue')
    plt.scatter(X[y_ah_predicted ==3,0], X[y_ah_predicted == 3,1], s=100, c='cyan')
    plt.scatter(X[y_ah_predicted ==4,0], X[y_ah_predicted == 4,1], s=100, c='orange')
    plt.scatter(X[y_ah_predicted ==5,0], X[y_ah_predicted == 5,1], s=100, c='green')
    plt.scatter(X[y_ah_predicted ==6,0], X[y_ah_predicted == 6,1], s=100, c='magenta')
    plt.scatter(X[y_ah_predicted ==7,0], X[y_ah_predicted == 7,1], s=100, c='yellow')
    plt.show()

    return y_ah_labels