import sys
import time
import pandas as pd
from sqlalchemy import create_engine
import pulp

from src.pulp_ilp_solver import solve_ilp_using_pulp


def direct(table_name, objective, objective_attribute, constraints, count_constraint):
    # Direct Algorithm
    start_time = time.time()

    # connection_string = 'postgresql+psycopg2://{user}:{pwd}@127.0.0.1'.format(user='postgres', pwd='.123') # For Local
    connection_string = 'postgresql+psycopg2://cs645db.cs.umass.edu:7645'  # For Edlab
    alchemyEngine = create_engine(connection_string, pool_recycle=3600)
    connection = alchemyEngine.connect()
    df = pd.read_sql("select * from tpch", connection)

    status, package_rows = solve_ilp_using_pulp(df, table_name, objective, objective_attribute, constraints, count_constraint)
    print('Status: {}'.format(pulp.LpStatus[status]))
    if pulp.LpStatus[status] == 'Not Solved':
        sys.exit('Is the default setting before a problem has been solved')
    elif pulp.LpStatus[status] == 'Infeasible':
        sys.exit('The problem has no feasible solution')
    elif pulp.LpStatus[status] == 'Unbounded':
        sys.exit('The cost function is unbounded')
    elif pulp.LpStatus[status] == 'Undefined':
        sys.exit('Feasible solution hasn\'t been found (but may exist)')
    else:
        print('Found the optimal Solution\nPackage rows: {}'.format(package_rows))
    print('Execution time: {} s'.format(round(time.time() - start_time, 2)))
