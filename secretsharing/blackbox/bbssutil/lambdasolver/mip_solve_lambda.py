
from __future__ import print_function
import sys
import math
#from ortools.linear_solver import pywraplp
from ortools.linear_solver import pywraplp

import numpy as np 


def create_data_model(ma_t, e):
    data = {}
    num_constrs, num_var = ma_t.shape
    e  = np.zeros((num_constrs,), dtype=int)
    e[0] = 1
    coeffs = [1]*len(ma_t[0])
    
    data['constraint_coeffs'] = ma_t 
    data['bounds']            = e
    data['obj_coeffs']        = coeffs 
    data['num_vars']          = len(ma_t[0])
    data['num_constraints']   = num_constrs
    return data 

def solve_for_lambda(ma_t, e):
    data = create_data_model(ma_t, e)
    # Create the mip solver with the CBC backend.
    solver = pywraplp.Solver('simple_mip_program', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
    #solver = pywraplp.Solver('simple_mip_program', pywraplp.Solver.GUROBI_MIXED_INTEGER_PROGRAMMING)
    #solver = pywraplp.Solver('SolveIntegerProblem', pywraplp.Solver.GUROBI_MIXED_INTEGER_PROGRAMMING)
    infinity = solver.infinity()
    x = {}
    for j in range(data['num_vars']):
       x[j] = solver.IntVar(-1, 1, 'x[%i]' % j)
    print('Number of variables =', solver.NumVariables())

    for i in range(data['num_constraints']):
        constraint_expr = [data['constraint_coeffs'][i][j] * x[j] for j in range(data['num_vars'])]
        solver.Add(sum(constraint_expr) == data['bounds'][i])

    objective = solver.Objective()
    for j in range(data['num_vars']):
        objective.SetCoefficient(x[j], data['obj_coeffs'][j])
    #objective.SetMaximization()
    objective.SetMinimization()
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print('Objective value =', solver.Objective().Value())

        lambda_vec = []
        for j in range(data['num_vars']):
            #print(x[j].name(), ' = ', x[j].solution_value())
            lambda_vec.append(x[j].solution_value())
        '''
        print()
        print('Problem solved in %f milliseconds' % solver.wall_time())
        print('Problem solved in %d iterations' % solver.iterations())
        print('Problem solved in %d branch-and-bound nodes' % solver.nodes())
        '''
        return lambda_vec
    else:
        print('The problem does not have an optimal solution.')
        return None

if __name__ == '__main__':
    filename = "m81.txt"
    #print(solve_for_lambda(filename)) 


