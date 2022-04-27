import sys

from src.direct import DirectAlgo
from src.sketch_refine import SketchRefine_Algo

# connection_string = 'postgresql+psycopg2://{user}:{pwd}@127.0.0.1'.format(user='postgres', pwd='lokesh123')  # For Local
connection_string = 'postgresql+psycopg2://cs645db.cs.umass.edu:7645'  # For Edlab
num_clusters = 5

d = DirectAlgo(connection_string)

if __name__ == '__main__':
    table_name = 'tpch'
    direct_algo = DirectAlgo(connection_string)
    sketch_refine_algo = SketchRefine_Algo(connection_string)
    if sys.argv[1] == 'Q1':
        objective = 'MAX'
        objective_attribute = 'count_order'
        constraints = {'sum_base_price': (None, 15469853.7043), 'sum_disc_price': (None, 45279795.0584),
                       'sum_charge': (None, 95250227.7918), 'avg_qty': (None, 50.353948653), 'avg_price': (None, 68677.5852459),
                       'avg_disc': (None, 0.110243522496), 'sum_qty': (None, 77782.028739)}
        count_constraint = (1, None)
    else:
        sys.exit('Not a valid query')

    print(d.direct_wrapper(table_name, objective, objective_attribute, constraints, count_constraint))
    # sketch_refine_algo.sketchrefine_wrapper(num_clusters, table_name, objective, objective_attribute, constraints, count_constraint)
