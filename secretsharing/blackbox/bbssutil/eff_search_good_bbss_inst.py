#!/usr/bin/env python3


import numpy as np


import sys, math, json,  secrets, itertools 
sys.path += ['./', '../', '../../' , '../../../']

from datetime                      import datetime
#from charm.core.math.integer       import integer,bitsize, int2Bytes, randomBits
from lambdasolver.mip_solve_lambda import * 
from distmatrix.dist_matrix_gen    import *
from distmatrix.maj_index_list     import * 
from checkiter                     import * 
from bbss                          import * 

debug = 0


def search_for_phi(n):

    # dictionary to check if all the nodes have been assigned in the random process, if not re-run the instance

    while 1:
        Node_index= {k:[] for k in range(n)}
        rand_ind, m, N_M_map = generateLiterals(n)

        no_of_shares = {k:k for k in range(n)}

        for k in range(n):
            no_of_shares[k] = len(N_M_map[k])
        
        print("no_of_shares:", no_of_shares)

        sorted_no_of_shares = sorted(no_of_shares.items(), key=lambda x: x[1])



        print("sorted_no_of_shares:", sorted_no_of_shares)
        print("N_M_map:", N_M_map)

        if debug:
            print("N_M_map:", N_M_map)
            print("After generating literals--->n:",n,"  m:",m, "rand_ind:", rand_ind)
    
        M_filename = "matrices/m"+str(m)+".txt"
        M = np.loadtxt(M_filename, dtype=int)
    
        if debug:
            print("Matrix M loaded from file:\n", M)
            print("Dimensions of loaded Matrix M:", M.shape)
    
        row_node_indices = psiFunction(rand_ind, m)
        S = bbssShareGen(M)
        #print("S", S)
        assigned_shares, node_share_index = assignShares2Nodes(S,row_node_indices, n)
        if debug:
            print("Assigned shares:", assigned_shares)
            print("node_share_index:", node_share_index)
    
        all_nodes = [i for i in range(n)]
        ###########req_threshold = math.floor((2*n)/3) + 1
        ####req_threshold = (n//3) + 1
        req_threshold = ((2*n)//3) + 1
        print("req_threshold:", req_threshold)
        
        new_comb = []
        for i in range(req_threshold, n+1):
            threshold_sorted_tuples = sorted_no_of_shares[i-req_threshold:i]
            sliding_window_nodes = []
            for node_share_tuple in threshold_sorted_tuples:
                sliding_window_nodes.append(node_share_tuple[0])
            new_comb.append(tuple(sorted(sliding_window_nodes)))

        print("new_combs:", new_comb)

        #TODO: Add logic to include sliding window in sorted nodes list 

        '''
        threshold_sorted_tuples = sorted_no_of_shares[:req_threshold]
        print("threshold sorted tuples:", threshold_sorted_tuples)

        least_share_nodes = []
        for node_share_tuple in threshold_sorted_tuples:
            least_share_nodes.append(node_share_tuple[0])

        new_comb_tuple =  tuple(sorted(least_share_nodes)) 
        new_comb = []
        new_comb.append(new_comb_tuple)
        print("new_comb", new_comb)

        if (req_threshold <= n):
            threshold_combinations = list(itertools.combinations(all_nodes, req_threshold))

        if debug:
            print("Threshold combinations:", threshold_combinations)
        '''
        count = 0
        lambda_for_comb = {}
        #for comb in threshold_combinations:
        for comb in new_comb:
            print("comb:", comb)
            
            row_indices = []
            for node in comb:
                row_indices = row_indices + node_share_index[node]
            if debug:
                print("Row indices assigned to the threshold group:", row_indices)
            ma_t = np.transpose(M[row_indices])
            e  = np.zeros((len(ma_t),), dtype=int)
            e[0] = 1
    
            Sa = S[row_indices]
            Sa_t = np.transpose(np.array(Sa))
            
            lambda_a = solve_for_lambda(ma_t, e)     # Compute lambda solution 
            
            if lambda_a is None:
                break

            else:                
                lambda_for_comb[str(comb)] = lambda_a
                lambda_a = np.array(lambda_a, dtype=int)
                count += 1 
                if debug:
                    print("Sa_t:", Sa_t, "\nlambda_a:", lambda_a)
                    print("len(Sa_t):", len(Sa_t), "len(lambda_a):", len(lambda_a))
                #print("Sa_t.shape:", Sa_t.shape,"lambda_a.shape:", lambda_a.shape)
                #print("type(Sa_t[0])", type(Sa_t[0]),"type(lambda_a[0]):",type(lambda_a[0]) )
                secret = np.dot(Sa_t, lambda_a)
                if debug:
                    print("**************************************Reconstructed_secret:", secret)
    
            #if len(threshold_combinations) == count:
            if len(new_comb) == count:
                print("Yayy! Found the final combination")
                filename = "n="+str(n)+"--"
                filename = filename + datetime.now().strftime("%d-%m-%Y_%I-%M-%S_%p") 
                to_file_dict = {}
    
                to_file_dict['n'] = n
                to_file_dict['m'] = m
                to_file_dict['M.shape'] = M.shape
                to_file_dict['rand_ind'] = rand_ind
                to_file_dict['map'] = node_share_index
                to_file_dict['lambdas'] = lambda_for_comb
    
                with open(filename , 'w') as file:
                    file.write(json.dumps(to_file_dict))
                return 
if __name__ == "__main__":
    #finished till 11
    #for n in range(13,14):
    #    search_for_phi(n)
    description = """
    This program provides a Black box secret sharing for (n, 2n/3) threshold access structure
    """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-n", "--nodes", default=4, type=int, help="number of nodes"
    )
    args = parser.parse_args()

    if not args.nodes:
        raise RuntimeError("Please provide number of nodes using -n ")


    n = args.nodes  #Number of nodes
    search_for_phi(n)
