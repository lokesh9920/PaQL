import sys

from src.direct import direct

if __name__ == '__main__':
    table_name = 'tpch'
    if sys.argv[1] == 'Q1':
        objective = 'MAX'
        objective_attribute = 'count_order'
        constraints = {'sum_base_price': (None, 15469853.7043), 'sum_disc_price': (None, 45279795.0584),
                       'sum_charge': (None, 95250227.7918), 'avg_qty': (None, 50.353948653), 'avg_price': (None, 68677.5852459),
                       'avg_disc': (None, 0.110243522496), 'sum_qty': (None, 77782.028739)}
        count_constraint = (1, None)
    else:
        sys.exit('Not a valid query')
    direct(table_name, objective, objective_attribute, constraints, count_constraint)
