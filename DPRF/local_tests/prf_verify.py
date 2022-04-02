import secrets, math, json, sys, argparse, ast, time  , csv
import numpy as np

sys.path += ['./', '../', '../../']

#import group parameters 
from conf.groupparam                                            import * 
from secretsharing.blackbox.bbssutil.checkiter                  import * 
from secretsharing.blackbox.bbssutil.distmatrix.dist_matrix_gen import *
from secretsharing.blackbox.bbssutil.distmatrix.maj_index_list  import * 

from secretsharing.blackbox.bbss import * 

from mip_solve_lambda  import *
from decimal import * 

def DPRINT ( *args , **kwargs ) : 
    if debug:
        print ( *args , **kwargs )

debug = 0

p = group256.order()
q = group283.order()

getcontext().prec = 512
pqratio = Decimal(int(p)) / Decimal(int(q))

u = 1024

def partial_eval(X, keytype, mykeyshare):
    global p, q, u
    par_eval = []
    keyvec = u * [mykeyshare]
    hash_vec = [group283.hash(X+str(i), target_type=ZR) for i in range(u)]
    dot_prod =  np.dot(hash_vec , keyvec)
    val = int(int(dot_prod) * pqratio)    #Rounding down
    par_sk = group256.init(ZR,val)
    return par_sk 


def partial_eval2(X, keytype, mykeyshares):
    global p, q, u
    
    evaluations = []
    for j in range(len(mykeyshares)):
        #X = "easwar"
        hash_vec = []
        keyvec = u * [mykeyshares[j]]
        hash_vec = [group283.hash(X+str(i), target_type=ZR) for i in range(u)]
        dot_prod =  np.dot(hash_vec , keyvec)
        val = int(int(dot_prod) * pqratio)    #Rounding down
        par_sk = group256.init(ZR,val)
        evaluations.append(par_sk)
    return evaluations 


if __name__ == "__main__":

    description = """
    This program provides a Black box secret sharing for (n, 2n/3) threshold access structure
    """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-n", "--nodes", default=4, type=int, help="number of nodes"
    )   
    args = parser.parse_args()

    n = args.nodes  #Number of nodes

    t_start = time.time()

    #------------------ PRF VERIFY -------------- # 
    u  = 8192
    X = "easwar"
    tau = group571.order()

    #------ Dlog verificaiton -------------#

    alpha  = [group283.random(ZR) for i in range(u)]
    beta   = [group283.random(ZR) for i in range(u)]
    hashval = [group283.hash(X+str(i), target_type=ZR) for i in range(u)]
    

    # ------------- Server computation ------------- # 
    #Commitments 
    g_alpha_i  = [g571 ** int(alpha[i]) for i in range(u)]

    # PRF computation 
    w = sum([alpha[i]* hashval[i] for i in range(u)])
    z = int(int(w) * pqratio)
    #r = int(p) * int(w) - int(q) * int(z)
    wptau = (int(w)*int(p)) % tau 
    qztau = (int(q) * int(z)) % tau 


    # Compute r and frack 
    rtau = wptau - qztau 
    big_value = sum([  int(alpha[i]) * int(hashval[i]) for i in range(u) ])  # sigma alpha_i . h_i in integer form 
    frack = (Decimal(big_value) - Decimal(int(w)))/Decimal(int(q)) # for correction to be applied by client 
    g_rtau = g571**rtau  # g**r 
    g_frack = g571 ** int(frack) 
    # Finally send [z, g**r , g ** frack ] --> [z, grtau, g_frack]

    # ---------- Client computation ---------------- # 
    g_alpha_h_i  = [g_alpha_i[i] ** int(hashval[i]) for i in range(u)]
    gw = g_alpha_h_i[0]
    for i in range(1,u):
        gw = gw * g_alpha_h_i[i]
    gw_client = gw 
    g_correction = g_frack  ** (-int(q))
    gw_hat = gw_client * g_correction 
    gqztau = g571**qztau 
    left = gw_hat ** int(p) 
    right = gqztau * g_rtau 

    if right == left:
        print("left = right, the PRF is verified!")
