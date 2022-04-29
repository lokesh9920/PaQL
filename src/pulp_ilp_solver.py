import sys
import pulp


class ILPSolver:
    def __init__(self):
        pass

    def fetch_the_required_ilp_problem_type(self, objective):
        if objective == 'MIN':
            return pulp.LpMinimize
        elif objective == 'MAX':
            return pulp.LpMaximize
        else:
            sys.exit('Unknown Objective: {} in fetch_the_required_ilp_problem_type of pulp_ilp_solver'.format(objective))

    def solve_ilp_using_pulp(self, table, table_name, objective, objective_attribute, constraints, count_constraint, repeat, sr_constraints):
        # Finding the length if the db table
        # sr_constraints -> limit the  number of times an instance is allowed in solution; the length should be equal to number of rows in table
        L = len(table)

        # Creating the Row identifiers
        row_identifiers = ['row_' + str(i) for i in range(L)]
        row_indexes = [int(i.strip('row_')) for i in row_identifiers]  # TODO Can be Optimized

        # Calculating The Upper Bound
        if len(sr_constraints) == 0:  # Original Package
            upBound = 1 + repeat
        else:  # Sketch Package
            upBound = max(sr_constraints) * (1 + repeat)
        # Adding Constrains to the variables
        rows = pulp.LpVariable.dicts("rows", indexs=row_identifiers, lowBound=0, upBound=upBound, cat='Integer', indexStart=[])

        # Creating rows finder problem
        prob = pulp.LpProblem("rows finder", self.fetch_the_required_ilp_problem_type(objective))

        # Adding the objective function
        prob += pulp.lpSum([rows[row_identifiers[i]] * table[objective_attribute][i] for i in row_indexes])

        # Adding the sum constraints
        for constraint_attribute in constraints:
            if constraints[constraint_attribute][0] is not None:
                prob += pulp.lpSum([rows[row_identifiers[i]] * table[constraint_attribute][i] for i in row_indexes]) >= constraints[constraint_attribute][
                    0]
            if constraints[constraint_attribute][1] is not None:
                prob += pulp.lpSum([rows[row_identifiers[i]] * table[constraint_attribute][i] for i in row_indexes]) <= constraints[constraint_attribute][
                    1]

        # Adding the count constraints
        if count_constraint[0] is not None:
            prob += pulp.lpSum([rows[row_identifiers[i]] for i in row_indexes]) >= count_constraint[0]
        if count_constraint[1] is not None:
            prob += pulp.lpSum([rows[row_identifiers[i]] for i in row_indexes]) <= count_constraint[1]

        # Adding The Repetition constraints
        for i in range(len(sr_constraints)):
            prob += rows[row_identifiers[i]] <= sr_constraints[i] * (1 + repeat)

        # Solving the problem
        prob.solve(pulp.PULP_CBC_CMD(timeLimit=3600, msg=False))  # TODO check which solver is being used

        variables = prob.variables()
        all_rows = [0] * len(variables)
        for v in variables:
            all_rows[int(str(v).strip('rows_row_'))] = v.varValue
        # print('Rows Vector: {}'.format(all_rows))

        # Returning the variables
        return prob.status, all_rows
