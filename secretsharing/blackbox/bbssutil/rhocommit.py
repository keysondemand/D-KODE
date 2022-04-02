import sys

sys.path += ['./', '../', '../../', '../../../']

import numpy as np
# from charm.toolbox.ecgroup   import ECGroup, ZR, G

from conf.groupparam import *
from secretsharing.blackbox.bbss import *

debug = 0


def DPRINT(*args, **kwargs):
    if debug:
        print(*args, **kwargs)


def rhoCommit(M, malicious=0):
    share_gen_start = time.process_time()

    S, RHO = bbssShareGen4DKG(M)  # RHO[0] is the random secret
    S_dash, RHO_dash = bbssShareGen4DKG(M)

    share_gen_end = time.process_time()

    share_gen_time = (share_gen_end - share_gen_start) * 1000

    DPRINT("In rhoCommit- shares gen time:", share_gen_time)

    rho_commits = []
    rho_commit_strings = []

    dlog_commits = []
    dlog_commit_strings = []

    exp_start = time.process_time()

    for i in range(len(RHO)):
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

    exp_end = time.process_time()
    exp_time = (exp_end - exp_start) * 1000

    DPRINT("total exp time:", exp_time)
    DPRINT("\n")

    return S, S_dash, rho_commits, rho_commit_strings, RHO, RHO_dash, dlog_commits, dlog_commit_strings


def rhoCommitPSS(M, share, share_dash, malicious=0):
    DPRINT("share and share_dash in rhoCommitPSS:", share, share_dash)

    S, RHO = bbssShareGen4PSS(M, share)  # RHO[0] is the random secret
    S_dash, RHO_dash = bbssShareGen4PSS(M, share_dash)

    rho_commits = []
    rho_commit_strings = []

    dlog_commits = []
    dlog_commit_strings = []

    for i in range(len(RHO)):
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
    return S, S_dash, rho_commits, rho_commit_strings, RHO, RHO_dash, dlog_commits, dlog_commit_strings


if __name__ == "__main__":
    M = np.loadtxt("M.txt", dtype=int)
    M = np.array(M)
    print("M:", M)
    # print(rhoCommit(M))

    print("group:", group)

    g = group.encode(decoded_g)
    h = group.encode(decoded_h)

    g_rand = group.random(G)
    zero = group.init(ZR, int(0))
    eight = group.init(ZR, int(8))

    S, S_dash, rho_commits, rho_commit_strings, RHO, RHO_dash, dlog_commits, dlog_commit_strings = rhoCommit(M)

    Verified = []
    NotVerified = []
    for i in range(len(S)):

        computed_share_commitment = (g ** S[i]) * (h ** S_dash[i])
        commitment_product = (g_rand ** eight) ** zero
        print("unity:", commitment_product)

        for j in range(len(M[i])):
            print("M[i][j]:", M[i][j])
            if M[i][j] == 1:
                b = group.init(ZR, int(M[i][j]))
                commitment_product = commitment_product * (rho_commits[j] ** b)

        print("computed_share_commitment:", computed_share_commitment, "\ncommitment_product", commitment_product)
        if (computed_share_commitment == commitment_product):
            Verified.append(i)
        else:
            NotVerified.append(i)

    print("Verified:", Verified)
    print("NotVerified:", NotVerified)

    '''

    g = group.random(G)

    a = group.random(ZR)
    b = group.random(ZR)

    c = a + b

    A = g ** a
    B = g ** b
    C1 = A * B
    C = g**c

    print("C1:", C1)
    print("C:", C)
    '''
