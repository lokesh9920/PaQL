import sys
import time
import pandas as pd
import pulp
from sqlalchemy import create_engine
from src.pulp_ilp_solver import ILPSolver
from collections import defaultdict


class DirectAlgo:
    def __init__(self, connection_string):
        alchemyEngine = create_engine(connection_string, pool_recycle=3600)
        connection = alchemyEngine.connect()
        ilp_solver = ILPSolver()
        self.connection = connection
        self.ilp_solver = ilp_solver
    '''
        TODO: changed the method signature of this method,
        Added df to the parameters
    '''
    def direct_wrapper(self, df, table_name, objective, objective_attribute, constraints, count_constraint, repeat, sr_constraints=[]):
        print('Initial Table Size: {}'.format(len(df)))
        try:
            if sys.argv[2] == 'local':
                df = df.head(int(round(len(df) * 0.5)))
                df.reset_index(inplace=True, drop=True)
        except Exception as e:
            print('Running on 100% data')
        print('Loaded the Table of Size: {}'.format(len(df)))
        rows = self.implement(table_name, objective, objective_attribute, constraints, count_constraint, df, repeat, sr_constraints)
        # Adding The rows to the output
        row_indexes = []
        for row_index in range(len(rows)):
            row_indexes.extend([row_index] * rows[row_index])
        return df.iloc[row_indexes].reset_index(drop=True)

    def implement(self, table_name, objective, objective_attribute, constraints, count_constraint, df, repeat, sr_constraints=[]):
        # Direct Algorithm

        # print('Called The ILP Solver')
        status, package_rows = self.ilp_solver.solve_ilp_using_pulp(df, table_name, objective, objective_attribute, constraints, count_constraint, repeat,
                                                                    sr_constraints)
        # print('ILP Solver Completed')
        # print('Status: {}'.format(pulp.LpStatus[status]))
        if pulp.LpStatus[status] == 'Not Solved':
            sys.exit('Is the default setting before a problem has been solved')
        elif pulp.LpStatus[status] == 'Infeasible':
            sys.exit('The problem has no feasible solution')
        elif pulp.LpStatus[status] == 'Unbounded':
            sys.exit('The cost function is unbounded')
        elif pulp.LpStatus[status] == 'Undefined':
            sys.exit('Feasible solution hasn\'t been found (but may exist)')
        else:
            pass
        return [int(i) for i in package_rows]
