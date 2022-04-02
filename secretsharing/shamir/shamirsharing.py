import  secrets, math, json, sys, argparse, time  
sys.path += ['./', '../', '../../']

import numpy           as np
from   numpy           import prod 
from   conf.groupparam import *

if group == group192 or  group == group256:
    neworder = group.order()
elif group == group283 or group == group571:
    neworder = int(group.order()) // 4 # Cofactor of chosen groups is 4

g_rand = group.random(G)
zero = group.init(ZR, int(0))
unity = g_rand ** zero 

def DPRINT ( *args , **kwargs ) : 
    if debug:
        print ( *args , **kwargs )
debug = 0

def randVecZR(vec_len):
    return [group.random(ZR) for x in range(vec_len)]

def genShamirDistMatrix(n,t = None):
    if t is None:
        t = n - ((n-1)//3) - 1
    #t = n-th-1 
    M = []
    for r in range(1,n+1):
        row = [r**j for j in range(t+1)]
        M.append(row)
    return np.array(M)

def genShareMatrix(M,RHO):
    S = M.dot(RHO) # works well for sparse matrices
    DPRINT("\nSecret is RHO[0]", RHO[0], "\n")
    return S

def sssShareGen4DkgPss(M, share = None):

    #Usually shareGen should not return RHO, but we return here for DKG 

    d = len(M)
    e = len(M[0])
   
    if share is None:
        share = group.random(ZR) % neworder 

    secret = [share]
    #secret = secret.append(share)

    DPRINT("secret inside sssShareGen4PSS:", secret)

    rhos   = randVecZR(e-1)
    rhos   = [x % neworder for x in rhos]
    RHO = secret + rhos
    RHO = np.array(RHO)
    S = genShareMatrix(M, RHO)
    DPRINT("M:", M)
    DPRINT("S:", S)
    DPRINT("RHO:", RHO)
    return S, RHO

def shamirShares(n, t = None):
    if t is None:
        #t = n//3
        t = n - ((n-1)//3) - 1
    M =  genShamirDistMatrix(n,t)       
    print(M)
    S, RHO = sssShareGen4DkgPss(M)
    
    DPRINT("M:", M)
    DPRINT("S:",   S)
    DPRINT("RHO:", RHO)

    node_share_index = {k:[] for k in range(n)}
    node_shares      = {k:[] for k in range(n)}

    for node_id in range(n):
        node_share_index[node_id].append(node_id)
    
    DPRINT(node_share_index)
    json.dump(node_share_index, open("tmp/sss_node_share_index.txt",'w'))

    return S, RHO

def shamirShareGenCommit(n,malicious=0, t = None):

    if t is None:
        #t = n//3
        t = n - ((n-1)//3) - 1

    M = genShamirDistMatrix(n,t)
    DPRINT("M:", M)

    S , RHO     = sssShareGen4DkgPss(M) #[0] is the random secret 
    S_dash, RHO_dash  = sssShareGen4DkgPss(M) #[0] is the random secret 
    
    DPRINT("len of S:", len(S))
    DPRINT("len of RHO:", len(RHO))

    rho_commits = []
    rho_commit_strings = []

    dlog_commits = []
    dlog_commit_strings = []

    for i in range(len(RHO)):
        #commit_val = (g ** S[i]) * (h ** S_dash[i])
        #dlog_commit_val = (g ** S[i]) 

        if malicious:
            commit_val = group.random(G)
            dlog_commit_val = group.random(G)
        else:
            dlog_commit_val = (g ** RHO[i])
            commit_val = dlog_commit_val * (h ** RHO_dash[i])
        rho_commits.append(commit_val)
        rho_commit_strings.append(group.serialize(commit_val))

        dlog_commits.append(dlog_commit_val)
        dlog_commit_strings.append(group.serialize(dlog_commit_val))
    return S, S_dash, rho_commits, rho_commit_strings, RHO, RHO_dash,  dlog_commits, dlog_commit_strings


def recon (x_s, y_s):
    assert (len(x_s) == len(y_s))
    x_s = [group.init(ZR, i) for i in x_s]

    lambdaCoeffs =  []

    for i in range(len(x_s)):

        others = list(x_s)
        cur = others.pop(i)
        others_sub = [ x-cur  for x in others]

        num_prod = prod(others)
        den_prod = prod(others_sub)
        
        lambdaCoeffs.append(num_prod* (den_prod ** (-1)))
    
    DPRINT("lambdas:",lambdaCoeffs)
    DPRINT("y_s:",y_s)
    return  sum([ y_s[i] * lambdaCoeffs[i]  for i in range(len(x_s)) ])

if __name__ == "__main__":
    description = """ 
    This program provides shamir secret sharing 
    """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-n", "--nodes", default=4, type=int, help="number of nodes"
    )   
    parser.add_argument(
        "-t", "--threshold", default=None, type=int, help="number of nodes"
    )   
    args = parser.parse_args()
    n = args.nodes
    t = args.threshold

    sharing_start = time.process_time()

    #if threshold is not defined, a default of n//3 is taken 
    S, RHO = shamirShares(n,t)
    sharing_end = time.process_time()

    sharing_time = (sharing_end - sharing_start)*1000 
    print("sharing_time:", sharing_time)

    filename = "tmp/timing_n_"+str(n)
    with open (filename,'a') as f:
        f.write(str(sharing_time)+"\n")

    '''
    x_s = [i for i in range(1,n+1)]
    y_s = S


    x_s = [1,2,3]
    y_s = S[:3]
    print("Reconstructed secret:", recon (x_s, y_s))
    t = n - ((n-1)//3) - 1
    M = genShamirDistMatrix(n,t)

    print("M:", M)

    S, S_dash, rho_commits , rho_commit_strings,  RHO, RHO_dash, dlog_commits, dlog_commit_strings = shamirShareGenCommit(n)
    for i in range(len(S)):
        computed_share_commitment = (g ** S[i]) * ( h ** S_dash[i])
        commitment_product = unity 
        for j in range(len(M[i])):
            b = group.init(ZR, int(M[i][j]))
            commitment_product = commitment_product * (rho_commits[j] ** b)

        print("computed_share_commitment:", computed_share_commitment, "\ncommitment_product", commitment_product)
        if (computed_share_commitment == commitment_product):
            print("Share[",i,"] Verified")
        else:
            print("Share[",i,"] Not Verified")


    '''


    '''

    for index in range(5):
        order = group.order()
        neworder = int(order) // 4 
        g1 = group.random(G) ** group.init(ZR, int(8))
        h1 = group.random(G) ** group.init(ZR, int(8))

        g_dec = group.decode(g)
        g_enc = group.encode(g_dec) ** group.init(ZR, int(4))
        
        h_dec = group.decode(h)
        h_enc = group.encode(h_dec) ** group.init(ZR, int(4))

        g = g_enc
        h = h_enc

        #print("g:", g)
        #print("g_enc:", g_enc)
        if g == g_enc:
            print("enc and dec works")

        n = 6
        t = n - ((n-1)//3) - 1
        M = genShamirDistMatrix(n,t)
        M = np.array(M)
        #print("M:", M)

        #M = np.array([[1,1,1],[1,2,4], [1,3,9]])
        #M = np.array([[1,1,1],[1,2,4]])
        #M = np.loadtxt("M.txt", dtype=int)
        #M = np.array(M)
        #print(M)
        #print("group:", group)
    
        R       = [group.random(ZR) % neworder for i in range(len(M[0]))]
        R_dash  = [group.random(ZR) % neworder for i in range(len(M[0]))]
    
        S      = M.dot(R)
        S_dash = M.dot(R_dash)
    
        C = []
        for i in range(len(R)):
            c      = (g ** R[i] )  * (h ** R_dash[i])
            C.append(c)


        V  = []
        NV = []
        for i in range(len(S)):
    
            csc = (g ** S[i]) * (h ** S_dash[i])
            cp = unity 
    
            for j in range(len(M[i])):
                b = group.init(ZR, int(M[i][j])) 
                cp = cp * (C[j] ** b) 
    
            if (csc == cp):
                V.append(i)
            else:
                NV.append(i)
    
        print("V:", V)
        print("NV:", NV)
    '''











