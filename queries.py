import sys

from src.direct import DirectAlgo
from src.sketch_refine import SketchRefine_Algo
from src.cluster import cluster
import pandas as pd


try:
    env = sys.argv[2]
except Exception as e:
    env = ''

if env == 'local':
    connection_string = 'postgresql+psycopg2://{user}:{pwd}@127.0.0.1'.format(user='postgres', pwd='lokesh123')  # For Local
else:
    connection_string = 'postgresql+psycopg2://cs645db.cs.umass.edu:7645'  # For Edlab
num_clusters = 10
num_elements_per_cluster = 16
d = DirectAlgo(connection_string)

##getting clusters
df = pd.read_sql("select * from tpch", d.connection)
X = df.values
k_means_obj = cluster()
custom_clusters = k_means_obj.get_clusters(X, num_clusters, num_elements_per_cluster)
print(custom_clusters.labels_.shape)
centroids = custom_clusters.cluster_centers_
centroids_df = pd.DataFrame(centroids, columns=df.columns)

if __name__ == '__main__':
    table_name = 'tpch'
    direct_algo = DirectAlgo(connection_string)
    sketch_refine_algo = SketchRefine_Algo(connection_string, custom_clusters)
    if sys.argv[1] == 'Q1':
        objective = 'MAX'
        objective_attribute = 'count_order'
        constraints = {'sum_base_price': (None, 15469853.7043), 'sum_disc_price': (None, 45279795.0584),
                       'sum_charge': (None, 95250227.7918), 'avg_qty': (None, 50.353948653), 'avg_price': (None, 68677.5852459),
                       'avg_disc': (None, 0.110243522496), 'sum_qty': (None, 77782.028739)}
        count_constraint = (1, None)
        repeat = 0
    elif sys.argv[1] == 'Q2':
        objective = 'MIN'
        objective_attribute = 'ps_min_supplycost'
        constraints = {'p_size': (None, 8)}
        count_constraint = (1, None)
        repeat = 0
    elif sys.argv[1] == 'Q3':
        objective = 'MIN'
        objective_attribute = 'id'
        constraints = {'revenue': (413930.849506, None)}
        count_constraint = (1, None)
        repeat = 0
    elif sys.argv[1] == 'Q4':
        objective = 'MIN'
        objective_attribute = 'id'
        constraints = {'o_totalprice': (None, 453998.242103), 'o_shippriority': (3, None)}
        count_constraint = (1, None)
        repeat = 0
    elif sys.argv[1]  == 'Q5':
        ## Extension idea for inserting tuples into the tables
        new_entry = [151, 85583909.21, 83454171.7561, 95125389.070932, 25.7614, 36483.3744582004,
                     0.5646945476383244, 54252, 2988, 28, 140.86, 11603.69, 77515.77, 0]
        custom_clusters.insert_tuple(new_entry)
        # print(custom_clusters.all_tuples_.shape)
        # print(custom_clusters.get_count_of_tuples_per_cluster())

        #insert into table and df also
        # pd.sqldf("insert into df values{}".format(tuple(new_entry)))
        sys.exit(0)
    else:
        sys.exit('Not a valid query')

    print(d.direct_wrapper(df, table_name, objective, objective_attribute, constraints, count_constraint, repeat))
    # sketch_refine_algo.sketchrefine_wrapper(num_clusters, table_name, objective, objective_attribute, constraints, count_constraint)
