import sys  
sys.path += ['./','../']

#from charm.toolbox.ecgroup   import ECGroup, ZR, G
from conf.groupparam         import *

def nizkpok_vec(dlog_commits, pedersen_commits, RHO, RHO_dash):
    # g^s g^s h^r RHO=s RHO_dash = r
    pi_vec = []
    
    neworder = int(group.order()) // 4 # Cofactor of 4, ZR actual order is /4
    #for i in range(len(dlog_commits)):

    #Need ZKP only for the first element 
    for i in range(1):
        v1 , v2 = group.random(ZR) % neworder , group.random(ZR) % neworder  
        #v1 , v2 = group.random(ZR) , group.random(ZR) 
        V1 = g ** v1 
        V2 = h ** v2 

        c = group.hash((g,h, dlog_commits[i], pedersen_commits[i],V1, V2), ZR) #TODO: Add commits to the hash 

        u1 = v1 - (c * RHO[i])
        u2 = v2 - (c * RHO_dash[i])
        #print("\n\nc:",c, "dlog_commit:", dlog_commits[i], "pedersen_commit:", pedersen_commits[i], "V1:", V1, "V2", V2)

        serialized_proof = [group.serialize(c), group.serialize(u1), group.serialize(u2)]
        #print("\nSender side proof:", [c, u1, u2])
        pi_vec.append(serialized_proof)
    return pi_vec

