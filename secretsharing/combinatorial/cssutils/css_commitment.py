import math, json, sys, argparse, itertools

sys.path += ['./', '../', '../../', '../../../']

import numpy as np

from conf.groupparam import *
from secretsharing.combinatorial.css import *

if group == group192 or group == group256:
    neworder = group.order()
elif group == group283 or group == group571:
    neworder = int(group.order()) // 4  # Cofactor of 4

'''
g_rand = group.random(G)
zero = group.init(ZR, int(0))
unity = g_rand ** zero
'''


def cssShareGen4DKG(n, t=None):
    secret_val = group.random(ZR) % neworder
    # secret_val = secrets.randbelow(100)

    # t = n//3
    if t is None:
        t = n - (n // 3) - 1

    nodes = [i for i in range(n)]
    node_comb = list(itertools.combinations(nodes, t))

    # TODO: Can load from file for higher n

    no_of_shares = len(node_comb)

    node_share_index = {k: [] for k in range(n)}
    node_shares = {k: [] for k in range(n)}

    shares = []
    for i in range(no_of_shares - 1):
        shares.append(group.random(ZR) % neworder)
        # shares.append(secrets.randbelow(100))
    sum_shares_except_last = sum(shares)
    last_share = secret_val - sum_shares_except_last

    shares.append(last_share)

    for i in range(len(node_comb)):
        for node_id in range(n):
            if node_id not in node_comb[i]:
                node_share_index[node_id].append(i)
                node_shares[node_id].append(shares[i])

    DPRINT("(n,t): (", n, ",", t, ")")
    DPRINT("secret_val:", secret_val)
    DPRINT("shares:", shares)
    DPRINT("no. of shares", len(shares))
    DPRINT("sum of shares:", sum(shares))
    DPRINT("node_share_index:", node_share_index)
    DPRINT("node_shares:", node_shares)

    # json.dump(node_share_index, open("../temp/css_node_share_index.txt",'w'))
    # json.dump(node_share_index, open("../tmp/css_node_share_index.txt",'w'))
    # json.dump(node_share_index, open("tmp/css_node_share_index.txt",'w'))

    return shares


def cssCommit(n, malicious=0):
    S = cssShareGen4DKG(n)  # RHO[0] is the random secret
    S_dash = cssShareGen4DKG(n)

    rho_commits = []
    rho_commit_strings = []

    dlog_commits = []
    dlog_commit_strings = []

    # Importing g and h from common parameters now 
    # g = group.encode(decoded_g)
    # h = group.encode(decoded_h)

    for i in range(len(S)):
        commit_val = (g ** S[i]) * (h ** S_dash[i])
        dlog_commit_val = (g ** S[i])

        if malicious:
            commit_val = group.random(G)
            dlog_commit_val = group.random(G)

        rho_commits.append(commit_val)
        rho_commit_strings.append(group.serialize(commit_val))

        dlog_commits.append(dlog_commit_val)
        dlog_commit_strings.append(group.serialize(dlog_commit_val))

    RHO = []
    RHO_dash = []

    return S, S_dash, rho_commits, rho_commit_strings, RHO, RHO_dash, dlog_commits, dlog_commit_strings
