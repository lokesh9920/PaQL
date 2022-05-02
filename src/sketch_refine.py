import pandas as pd
import numpy as np
from src.direct import DirectAlgo
from sklearn.cluster import KMeans
from collections import defaultdict
import sys


class SketchRefine_Algo:
    def __init__(self, connection_string, clusters):
        direct_algo = DirectAlgo(connection_string)
        self.direct_algo = direct_algo
        self.connection = direct_algo.connection
        self.clusters = clusters

    def get_clusters(self, X, num_clusters):
        # returns K-means clusters
        clusters = KMeans(n_clusters=num_clusters, random_state=0).fit(X)
        return clusters

    def sketchrefine_wrapper(self, num_clusters, table_name, objective, objective_attribute, constraints, count_constraint, repeat):
        df = pd.read_sql("select * from tpch", self.connection)
        print('Initial Table Size: {}'.format(len(df)))
        try:
            if sys.argv[2] == 'local':
                df = df.head(int(round(len(df) * 0.5)))
                df.reset_index(inplace=True, drop=True)
        except Exception as e:
            print('Running on 100% data')
        print('Loaded the Table of Size: {}'.format(len(df)))
        X = np.array(df.values)
        k_means = self.get_clusters(X, num_clusters)
        centroids = k_means.cluster_centers_
        centroids_df = pd.DataFrame(centroids, columns=df.columns)
        cluster_entries = defaultdict(lambda: pd.DataFrame())
        row_cluster_labels = k_means.labels_
        row_cluster_labels_set = list(set(row_cluster_labels))
        row_cluster_labels_set.sort()
        for cluster in set(row_cluster_labels_set):
            cluster_entries[cluster] = pd.DataFrame(X[np.where(row_cluster_labels == cluster)], columns=df.columns).reset_index(drop=True)
        return self.implement(table_name, objective, objective_attribute, constraints, count_constraint, repeat, centroids_df, cluster_entries, k_means)

    def sr_algo_constraints(self, k_means):
        count = []
        centroids = k_means.cluster_centers_
        labels = k_means.labels_
        num_clusters = centroids.shape[0]
        for i in range(num_clusters):
            count.append(np.sum(labels == i))
        return count

    def implement(self, table_name, objective, objective_attribute, constraints, count_constraint, repeat, centroids_df, cluster_entries, k_means):
        sr_constraints = self.sr_algo_constraints(k_means=k_means)
        sketch_rows = self.direct_algo.implement(table_name, objective, objective_attribute, constraints, count_constraint, centroids_df, repeat,
                                                 sr_constraints)
        original_rows = []
        total = defaultdict(lambda: [])
        for constraint_attr in constraints:
            total[constraint_attr] = list(centroids_df[constraint_attr] * sketch_rows)
        total_count = sketch_rows
        for i in range(len(sketch_rows)):
            if sketch_rows[i] != 0:
                pi = cluster_entries[i]
                pi_constraints = {}
                for constraint_attr in constraints:
                    lower_bound, upper_bound = constraints[constraint_attr]
                    if lower_bound is not None:
                        lower_bound -= sum(total[constraint_attr]) - centroids_df[constraint_attr][i] * sketch_rows[i]
                    if upper_bound is not None:
                        upper_bound -= sum(total[constraint_attr]) - centroids_df[constraint_attr][i] * sketch_rows[i]
                    pi_constraints[constraint_attr] = (lower_bound, upper_bound)
                pi_count_constraint = (total_count[i], total_count[i])
                rows = self.direct_algo.implement(table_name, objective, objective_attribute, pi_constraints, pi_count_constraint, pi, repeat, [])
                for constraint_attr in constraints:  # Updating the Processed rows values
                    total[constraint_attr][i] = sum(list(pi[constraint_attr] * rows))
                # Adding The rows to the output
                row_indexes = []
                for row_index in range(len(rows)):
                    row_indexes.extend([row_index] * rows[row_index])
                original_rows.append(pi.iloc[row_indexes])
        return pd.concat(original_rows, ignore_index=True)
