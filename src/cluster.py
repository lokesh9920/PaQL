from sklearn.cluster import KMeans
import numpy as np

class cluster:
    def __init__(self):
        pass
    def debug_print(self, clusters):
        labels = clusters.labels_
        centroids = clusters.cluster_centers_
        num_clusters = centroids.shape[0]
        count_list = []
        for i in range(num_clusters):
            count_list.append(np.sum(labels == i))
        return count_list

    def get_clusters(self, X, num_clusters, num_elements_per_cluster):
        ## returns K-means clusters
        clusters = KMeans(n_clusters=num_clusters, random_state=0).fit(X[:, 1:])
        #print('Length of each cluster BEFORE reshuffling: {}' .format(self.debug_print(clusters)))

        clusters = self.reshuffle_tuples(X[:, 1:], clusters, num_elements_per_cluster) #gives custom clusters

        #print('Length of each cluster AFTER reshuffling: {}'.format(self.debug_print(clusters)))
        return clusters

    def reshuffle_tuples(self, X, clusters, num_elements_per_clusters):
        #num_elements_per_clusters is the threshold per cluster
        centroids = clusters.cluster_centers_   #np array
        num_clusters, columns = centroids.shape
        labels = clusters.labels_
        per_cluster = []
        out_of_range_clusters_index = []
        exact_range_clusters_index = []
        under_range_clusters_index = []
        all_clusters = []
        for i in range(num_clusters):
            current_elements = np.sum(labels == i)
            per_cluster.append(current_elements)
            if current_elements == num_elements_per_clusters:
                exact_range_clusters_index.append(i)
            elif current_elements < num_elements_per_clusters:
                under_range_clusters_index.append(i)
            else:
                out_of_range_clusters_index.append(i)
            all_clusters.append(X[labels == i])
        for current_exceeded_cluster in out_of_range_clusters_index:
            num_excess = per_cluster[current_exceeded_cluster] - num_elements_per_clusters

            current_centroid = centroids[current_exceeded_cluster, :]
            for i in range(num_excess):
                cluster_tuples = all_clusters[current_exceeded_cluster]
                element_to_move = self.get_least_relevant(current_centroid, cluster_tuples)
                element_moving = cluster_tuples[element_to_move]
                true_new_centroid_index = -1
                if len(under_range_clusters_index) != 0:
                    closest_open_cluster = self.get_closest(centroids[under_range_clusters_index], cluster_tuples[element_to_move])
                    true_new_centroid_index = np.where(np.sum(centroids[under_range_clusters_index][closest_open_cluster] - centroids, axis = 1) == 0)[0][0]
                    all_clusters[current_exceeded_cluster] = np.vstack((all_clusters[current_exceeded_cluster][0:element_to_move], all_clusters[current_exceeded_cluster][element_to_move + 1:]))
                    all_clusters[true_new_centroid_index] = np.vstack((all_clusters[true_new_centroid_index], element_moving))

                    if all_clusters[true_new_centroid_index].shape[0] == num_elements_per_clusters:
                        #The cluster to which we moved got full, then don't consider for next shuffling/movement
                        under_range_clusters_index.remove(true_new_centroid_index)
                        exact_range_clusters_index.append(true_new_centroid_index)
                    #Update the label of the moved tuple
                    true_tuple_index = np.where(np.sum(X - element_moving, axis = 1) == 0)[0][0]
                    labels[true_tuple_index] = true_new_centroid_index
                else:
                    # create_new_cluster
                    all_clusters[current_exceeded_cluster] = np.vstack((all_clusters[current_exceeded_cluster][0:element_to_move], all_clusters[current_exceeded_cluster][element_to_move + 1:]))
                    all_clusters.append(element_moving.reshape(1, -1))
                    if all_clusters[-1].shape[0] < num_elements_per_clusters:
                        under_range_clusters_index.append(len(all_clusters) - 1) # NEW CLUSTER HAS LESS NUMBER OF ELEMENTS
                    #updating the label of the moved element
                    true_tuple_index = np.where(np.sum(X - element_moving, axis = 1) == 0)[0][0]
                    labels[true_tuple_index] = len(all_clusters) - 1

                centroids = self.recompute_centroids(all_clusters)
        clusters = Custom_Clusters(all_clusters, centroids, labels, X, num_elements_per_clusters)
        return clusters



    def get_least_relevant(self, centroid, tuples):
        #farthest from the given centroid
        diff = tuples - centroid
        squared_diff = diff * diff
        distance = np.sum(squared_diff, axis = 1)   #column vector
        least_relevant_index = np.argmax(distance)
        return least_relevant_index

    def get_closest(self, centroids, tuple):
        diff = centroids - tuple
        squared_diff = diff * diff
        distance = np.sum(squared_diff, axis = 1)
        closest_index = np.argmin(distance)
        return closest_index

    def recompute_centroids(self, all_clusters):
        centroids = np.array([[]])
        for cluster in all_clusters:
            centroids = np.append(centroids, np.mean(cluster, axis = 0, keepdims=True)).reshape(-1, cluster.shape[1])
        return centroids



class Custom_Clusters:
    ##Need custom clusters because, after reshuffling the k-means clusters, we no more can use methods of k-means returned clusters
    ## they don't give the reshuffled data
    def __init__(self, all_clusters, centroids, labels, X, num_elements_per_cluster_threshold):
        self.list_of_all_cluster_tuples = all_clusters #list of np arrays
        self.cluster_centers_ = centroids ##np array
        self.labels_ = labels.reshape(-1, 1)   #1d- np array of itnegers
        self.all_tuples_ = X
        self.num_elements_per_clusters_threshold = num_elements_per_cluster_threshold


        ## For internal computations
        num_clusters = len(all_clusters)
        self.exact_range_clusters_index = []
        self.under_range_clusters_index = []
        for i in range(num_clusters):
            current_elements = np.sum(labels == i)
            if current_elements == num_elements_per_cluster_threshold:
                self.exact_range_clusters_index.append(i)
            elif current_elements < num_elements_per_cluster_threshold:
                self.under_range_clusters_index.append(i)

    def insert_tuple(self, tuple):
        #The tuple is a list here eg: [1,2,3], size = num of columns
        tuple_array = np.array([tuple])
        if len(self.under_range_clusters_index) == 0:
            #create new cluster
            #Adding new cluster element to list of all clusters
            self.list_of_all_cluster_tuples.append(tuple_array)
            #Adding new centroid
            self.cluster_centers_ = np.vstack((self.cluster_centers_, tuple_array))
            #Adding new label correspondin to the new tuple inserted
            self.labels_ = np.vstack((self.labels_, np.array([[len(self.list_of_all_cluster_tuples) - 1]])))
            #Adding new tuple to all tuples
            self.all_tuples_ = np.vstack((self.all_tuples_, tuple_array))

            #Making this new cluster available for next addition
            if self.list_of_all_cluster_tuples[-1].shape[0] < self.num_elements_per_clusters_threshold:
                self.under_range_clusters_index.append(len(self.list_of_all_cluster_tuples) - 1)  # NEW CLUSTER HAS LESS NUMBER OF ELEMENTS
            pass
        else:
            available_cluster_centroids = self.cluster_centers_[self.under_range_clusters_index]
            nearest_cluster_index = self.get_closest(available_cluster_centroids, tuple_array)
            nearest_cluster_true_index = np.where(np.sum(self.cluster_centers_ - self.cluster_centers_[self.under_range_clusters_index][nearest_cluster_index], axis = 1) == 0)[0][0]
            #add element to the cluster
            self.list_of_all_cluster_tuples[nearest_cluster_true_index] = np.vstack((self.list_of_all_cluster_tuples[nearest_cluster_true_index], tuple_array))
            #update the centroid of this cluster
            self.cluster_centers_[nearest_cluster_true_index, :] = np.mean(self.list_of_all_cluster_tuples[nearest_cluster_true_index], axis = 0)
            #Adding the tuple to the all tuples
            self.all_tuples_ = np.vstack((self.all_tuples_, tuple_array))
            #Adding the label for the newly added element
            self.labels_ = np.vstack((self.labels_, np.array([[nearest_cluster_true_index]])))

            #if cluster is filled, do not consider it for further addition
            if self.list_of_all_cluster_tuples[nearest_cluster_true_index].shape[0] == self.num_elements_per_clusters_threshold:
                self.under_range_clusters_index.remove(nearest_cluster_true_index)
                self.exact_range_clusters_index.append(nearest_cluster_index)

    def get_closest(self, centroids, tuple):
        diff = centroids - tuple
        squared_diff = diff * diff
        distance = np.sum(squared_diff, axis = 1)
        closest_index = np.argmin(distance)
        return closest_index
    #Util functions
    def get_count_of_tuples_per_cluster(self):
        labels = self.labels_
        centroids = self.cluster_centers_
        num_clusters = centroids.shape[0]
        count_list = []
        for i in range(num_clusters):
            count_list.append(np.sum(labels == i))
        return count_list

    def get_label_from_tuple(self, tuple):
        # Tuples is expencted to be a np array of shape(1, num_columns)
        index = np.where(np.sum(self.all_tuples_ - tuple, axis = 1) == 0)
        if index[0].size == 0:
            return -1;      #Tuple does not exist
        true_tuple_index = index[0][0]
        return self.labels_[true_tuple_index]
    ##Getter Methods
    def get_tuples_in_cluster(self, i):
        return self.list_of_all_cluster_tuples[i]
    def get_centroids(self):
        return self.cluster_centers_
    def get_labels(self):
        return self.labels_
    def get_elements_from_cluster_id(self, id):
        if id >= len(self.list_of_all_cluster_tuples):
            return None
        return self.list_of_all_cluster_tuples[id]

