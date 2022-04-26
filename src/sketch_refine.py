import pandas as pd
import numpy as np
from src.direct import DirectAlgo
from sklearn.cluster import KMeans

class SketchRefine_Algo:
    def __init__(self, connection_string):
        direct_algo = DirectAlgo(connection_string)
        self.direct_algo = direct_algo
        self.connection = direct_algo.connection


    def get_clusters(self, X, num_clusters):
        ## returns K-means clusters
        clusters = KMeans(n_clusters = num_clusters, random_state = 0).fit(X)
        return clusters


    def sketchrefine_wrapper(self, num_clusters, table_name, objective, objective_attribute, constraints, count_constraint):
        df = pd.read_sql("select * from tpch", self.connection)
        X = df.values
        k_means = self.get_clusters(X, num_clusters)
        centroids = k_means.cluster_centers_
        centroids_df = pd.DataFrame(centroids, columns = df.columns)
        self.implement(table_name, objective, objective_attribute, constraints, count_constraint, centroids_df, df, k_means)

    def sr_algo_constraints(self, k_means):
        count = []
        centroids = k_means.cluster_centers_
        labels = k_means.labels_
        num_clusters = centroids.shape[0]
        for i in range(num_clusters):
            count.append(np.sum(num_clusters == i))
        return count


    def implement(self, table_name, objective, objective_attribute, constraints, count_constraint, centroids_df, df, k_means):
        sr_constraints = self.sr_algo_constraints(k_means = k_means)
        self.direct_algo.implement(table_name, objective, objective_attribute, constraints, count_constraint, centroids_df, sr_constraints)
        return