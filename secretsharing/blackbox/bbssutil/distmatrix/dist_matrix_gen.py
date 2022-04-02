import sys
import numpy as np

def m_and(A, B):

    '''      ___            ___ 
    M_AND = | C_a C_a R_a  0   |
            | 0   C_b  0   R_b |
            ---            ---
            C_a : first column of A
            R_a : Rest of the matrix of A - so no. of columns - 1

    '''
    rows = len(A) + len(B)
    cols = len(A[0]) + len(B[0])
    m_and = [[0]*cols]*rows
    for i in range(len(A)):
        m_and[i] =     [A[i][0]] + A[i] + [0]*(len(B[0])-1)
    for i in range(len(B)):
        m_and[i+len(A)] = [0] + [B[i][0]] + [0]*(len(A[0])-1) + B[i][1:]
    return m_and  

def m_or(A,B):

    '''      ___        ___ 
    M_OR =  | C_a R_a  0   |
            | C_b  0   R_b |
            ---         ---
            C_a : first column of A
            R_a : Rest of the matrix of A - so no. of columns - 1

    '''
    rows = len(A) + len(B)
    cols = len(A[0]) + len(B[0]) - 1
    m_or= [[0]*cols]*rows

    for i in range(len(A)):
        m_or[i] = A[i] + [0]*(len(B[0])-1)
    for i in range(len(B)):
        m_or[i+len(A)] = [B[i][0]] + [0]*(len(A[0])-1) + B[i][1:]
    return m_or



def Maj3(x,y,z):
    if not (0,0,0 <=x, y, z <= 1,1,1):
        print("Majority function takes only Booleans")
    return ((x*y)+(y*z)+(x*z))%2 


def Maj3_dist_mat(X, Y, Z):
    XY = m_and(X,Y)
    YZ = m_and(Y,Z)
    XZ = m_and(X,Z)
    return  m_or(XZ, m_or(XY,YZ))


def check_power_of_3(n):
    while (n % 3 == 0):
        n = n/3
    return n ==1 

def dist_matrix(y):
    # y are the literals after mapping x to y, y is m bit long where m is  n^2.71
    # this y should not be dependent on input x and should be all ones - literals 
    # TODO: Maintain a separate list for the mapping between x and y 
    if not (check_power_of_3(len(y))):
        print ("Error: Literal no. not a power of 3, not computing Distribution Matrix")
        return 

    matrices = [0]*len(y)
    for i in range(len(y)):
        matrices[i] = [[y[i]]]
    while len(matrices) > 1:
        for i in range(len(matrices)//3):
            temp  = Maj3_dist_mat(matrices[3*i], matrices[3*i+1], matrices[3*i+2])
            matrices[i] = temp
        del (matrices[len(matrices)//3+1:]) 
    matrices = matrices[0]
    return (np.array(matrices))


if __name__ == "__main__":

    y = [1 for x in range(0,27)]
    dist_matrix(y)
    A1 = [[1]]
    A2 = [[1]]
    A3 = [[1]]
    print(np.array(Maj3_dist_mat(Maj3_dist_mat(A1,A2,A3), Maj3_dist_mat(A1,A2,A3), Maj3_dist_mat(A1,A2,A3))))


    A1 = [[1]]
    A2 = [[0]]
    A3 = [[1]]
    print(np.array(Maj3_dist_mat(Maj3_dist_mat(A1,A2,A3), Maj3_dist_mat(A1,A2,A3), Maj3_dist_mat(A1,A2,A3))))

    sys.exit(0)

    A = [[1 ,1], [1, 1]]
    B = [[1, 1], [1, 1]]
    C = [[1, 1], [1, 1]]


    print(np.array(m_and(A1,A2)))
    print(np.array(m_or(A1,A2)))

    print(np.array(Maj3_dist_mat(A,B,C)))




