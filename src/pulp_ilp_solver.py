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

    def solve_ilp_using_pulp(self, table, table_name, objective, objective_attribute, constraints, count_constraint, repeat, sr_constraints=[]):
        # Finding the length if the db table
        # sr_constraints -> limit the  number of times an instance is allowed in solution; the length should be equal to number of rows in table
        L = len(table)

        # Creating the Row identifiers
        row_identifiers = ['row_' + str(i) for i in range(L)]
        row_indexes = [int(i.strip('row_')) for i in row_identifiers]  # TODO Can be Optimized

        # Adding Constrains to the variables
        rows = pulp.LpVariable.dicts("rows", indexs=row_identifiers, lowBound=0, upBound=1 + repeat, cat='Integer', indexStart=[])

        # Creating rows finder problem
        prob = pulp.LpProblem("rows finder", self.fetch_the_required_ilp_problem_type(objective))

        # Adding the objective function
        prob += pulp.lpSum([rows[row_identifiers[i]] * table[objective_attribute][i] for i in row_indexes])

        # Adding the sum constraints
        for constraint_attribute in constraints:
            if constraints[constraint_attribute][0] is not None and constraints[constraint_attribute][1] is not None:
                prob += constraints[constraint_attribute][0] <= pulp.lpSum(
                    [rows[row_identifiers[i]] * table[constraint_attribute][i] for i in row_indexes]) <= \
                        constraints[constraint_attribute][1]
            elif constraints[constraint_attribute][0] is not None:
                prob += constraints[constraint_attribute][0] <= pulp.lpSum(
                    [rows[row_identifiers[i]] * table[constraint_attribute][i] for i in row_indexes])
            elif constraints[constraint_attribute][1] is not None:
                prob += pulp.lpSum([rows[row_identifiers[i]] * table[constraint_attribute][i] for i in row_indexes]) <= constraints[constraint_attribute][
                    1]
            else:
                sys.exit('Stopping, the constraint attribute: {}, as there are no bounds'.format(constraint_attribute))

        # Adding the count constraints
        if count_constraint[0] is not None and count_constraint[1] is not None:
            prob += count_constraint[0] <= pulp.lpSum([rows[row_identifiers[i]] for i in row_indexes]) <= count_constraint[1]
        elif count_constraint[0] is not None:
            prob += count_constraint[0] <= pulp.lpSum([rows[row_identifiers[i]] for i in row_indexes])
        elif count_constraint[1] is not None:
            prob += pulp.lpSum([rows[row_identifiers[i]] for i in row_indexes]) <= count_constraint[1]
        else:
            sys.exit('Stopping, as there are no count bounds')

        # Adding The Repetition constraints
        for i in range(len(sr_constraints)):
            prob += rows[row_identifiers[i]] == sr_constraints[i]

        # Solving the problem
        prob.solve(pulp.PULP_CBC_CMD(timeLimit=3600, msg=False))  # TODO check which solver is being used

        package_rows = []
        all_rows = []
        for v in prob.variables():
            all_rows.append(v.varValue)
            if v.varValue == 1:
                package_rows.append(int(v.name.strip('rows_row_')) + 1)
        # print('Rows Vector: {}'.format(all_rows))

        # Returning the variables
        return prob.status, package_rows
