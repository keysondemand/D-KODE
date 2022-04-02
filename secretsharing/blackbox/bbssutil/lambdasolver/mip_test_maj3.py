from __future__ import print_function
from ortools.linear_solver import pywraplp

def main():
    # Create the mip solver with the CBC backend.
    solver = pywraplp.Solver('simple_mip_program',
                             pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    infinity = solver.infinity()
    # x and y are integer non-negative variables.
    x1 = solver.IntVar(-1, 1, 'x1')
    x2 = solver.IntVar(-1, 1, 'x2')
    x3 = solver.IntVar(-1, 1, 'x3')
    x4 = solver.IntVar(-1, 1, 'x4')
#    x5 = solver.IntVar(-1, 1, 'x5')
#    x6 = solver.IntVar(-1, 1, 'x6')

    print('Number of variables =', solver.NumVariables())

    #solver.Add(x1 + x7 * y == 6)
    solver.Add(x1 + x3 + x4  == 1)
    solver.Add(x1 + x2       == 0)
    solver.Add(x3        == 0)
    solver.Add(x4        == 0)
   # solver.Add(x3 + x4       == 0)
   # solver.Add(x5 + x6       == 0)


    print('Number of constraints =', solver.NumConstraints())

    # Maximize x + 10 * y.
    solver.Maximize(-1*(x1 + x2+ x3 + x4))

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print('Solution:')
        print('Objective value =', solver.Objective().Value())
        print('x1 =', x1.solution_value())
        print('x2 =', x2.solution_value())
        print('x3 =', x3.solution_value())
        print('x4 =', x4.solution_value())
        #print('x5 =', x5.solution_value())
        #print('x6 =', x6.solution_value())
    else:
        print('The problem does not have an optimal solution.')

    print('\nAdvanced usage:')
    print('Problem solved in %f milliseconds' % solver.wall_time())
    print('Problem solved in %d iterations' % solver.iterations())
    print('Problem solved in %d branch-and-bound nodes' % solver.nodes())


if __name__ == '__main__':
    main()
