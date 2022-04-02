import math, json, sys, argparse, itertools, time 
sys.path += ['./', '../', '../../']
from conf.groupparam import *

def DPRINT ( *args , **kwargs ) :
    if debug:
        print( *args , **kwargs )
debug = 0


def combinatorial_ss(n, t=None):

    if group == group192 or group == group256:
        neworder = group.order()
        secret_val = group.random(ZR)
    elif group == group283 or group == group571:
        neworder = int(group.order()) // 4 # Cofactor of chosen groups is 4 
        secret_val = (group.random(ZR)) % neworder 
    
    #secret_val = secrets.randbelow(100)

    if t is None:
        #t = n//3 
        t = n - ((n-1)//3) - 1
    nodes = [i for i in range(n)]
    node_comb = list(itertools.combinations(nodes , t))

    no_of_shares = len(node_comb)

    node_share_index = {k:[] for k in range(n)}
    node_shares      = {k:[] for k in range(n)}

    shares = []
    for i in range(no_of_shares-1):

        shares.append( (group.random(ZR)) % neworder  )
        #shares.append(secrets.randbelow(100))

    sum_shares_except_last = sum(shares)
    last_share = secret_val - sum_shares_except_last

    shares.append(last_share)

    for i in range(len(node_comb)):
        for node_id in range(n):
            if node_id not in node_comb[i]:
                node_share_index[node_id].append(i)
                node_shares[node_id].append(shares[i])

    DPRINT("(n,t): (",n,",",t,")" )
    DPRINT("secret_val:"      , secret_val)
    DPRINT("shares:"          , shares)
    DPRINT("no. of shares"    , len(shares))
    DPRINT("sum of shares:"   , sum(shares))
    DPRINT("node_share_index:", node_share_index)
    DPRINT("node_shares:"     , node_shares)

    json.dump(node_share_index, open("tmp/css_node_share_index.txt",'w'))
    
    #TODO: Uncomment to check reconstruction 
    '''
    
    list_of_nodes = [x for x in range(t+1)]
    shares_set = []
    for i in range(len(list_of_nodes)):
        node_shares_list  = node_shares[list_of_nodes[i]]
        # finding a union of the share elements
        for x in node_shares_list:
            if x not in shares_set:
                shares_set.append(x)
        #shares_set = shares_set.union(a)

    DPRINT(shares_set)
    reconstructed_secret = sum(list(shares_set))

    print("Reconstructed secret:", reconstructed_secret)

    if reconstructed_secret == secret_val:
        print("Yay, reconstructed correctly")
    '''


    return node_shares

def recon(node_shares, list_of_nodes):
    #node_shares should be a dictionary of node id and its corresponding shares 
    shares_set = []
    for i in range(len(list_of_nodes)):
        node_shares_list  = node_shares[list_of_nodes[i]]
        # finding a union of the share elements
        for x in node_shares_list:
            if x not in shares_set:
                shares_set.append(x)
        #shares_set = shares_set.union(a)

    DPRINT(shares_set)
    reconstructed_secret = sum(list(shares_set))

    return reconstructed_secretm 


if __name__ == "__main__":

    description = """
    This program provides a Black box secret sharing for (n, 2n/3) threshold access structure
    """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-n", "--nodes", default=4, type=int, help="number of nodes"
    )   
    parser.add_argument(
        "-t", "--threshold", default=None, type=int, help="number of nodes"
    )   
    args = parser.parse_args()

    n = args.nodes  #Number of nodes
    t = args.threshold


    sharing_start = time.process_time()
    shares = combinatorial_ss(n,t)
    sharing_end = time.process_time()

    sharing_time = (sharing_end - sharing_start)*1000

    filename = "tmp/timing_n_"+str(n)
    with open (filename,'a') as f:
        f.write(str(sharing_time)+"\n")


