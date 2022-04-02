import sys, json, re, time, csv
import os, threading, socket, ast
import numpy as np
from random import randint


sys.path += ['./', '../', '../../']

from OpenSSL import SSL, crypto
from sys import argv
from time import sleep
from operator import add
from collections import defaultdict

from charm.core.engine.util import *


# KODE related configs and utils
from conf.connectionconfig import *
from conf.groupparam import *
from util.connectionutils import *
from util.transactionbroadcast import *
from util.nizk import *
from secretsharing.blackbox.bbssutil.rhocommit import *


debug = 0

MALICIOUS = 0

broadcast_counter = 0

peers = {}
connections = {}

my_rcvd_shares = defaultdict(dict)
my_rcvd_shares_dash = defaultdict(dict)
my_rcvd_shares_strings = defaultdict(dict)
my_rcvd_shares_dash_strings = defaultdict(dict)

peer_share_commits = defaultdict(dict)
peer_dlog_commits = defaultdict(dict)

generated_shares = defaultdict(dict)

complaints = defaultdict(dict)
records = defaultdict(lambda: defaultdict(dict))
nizks = defaultdict(lambda: defaultdict(dict))
# nizks                        = defaultdict(dict)

node_indices_not_verified = defaultdict(dict)

nodes_verification_failed = set()
QualifiedSet = set()
DisqualifiedSet = set()

nizk_count = 0
rcvd_share_count = 0

tx_count = 0
epoch = 0

node_share_index = json.load(open("../../secretsharing/blackbox/tmp/node_share_index.txt"))
# N_M_map = json.load(open("../../secretsharing/blackbox/tmp/N_M_map.txt"))


def DPRINT(*args, **kwargs):
    if debug:
        print(*args, **kwargs)


def deserializeElements(objects):
    object_byte_strings = re.findall(r"'(.*?)'", objects, re.DOTALL)
    object_strings = [str.encode(a) for a in object_byte_strings]
    elements = [group.deserialize(a) for a in object_strings]
    return elements


def serverSock(MY_IP, MY_PORT, nid):
    print("server socket")
    print("N_NODES", N_NODES)
    all_client_threads = []
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', MY_PORT))
    s.listen(N_NODES)

    t = threading.currentThread()
    while getattr(t, "data_receive", True):
        try:
            peer_con, peer_addr = s.accept()

            handle_peer_thread = threading.Thread(target=handle_peer, args=(peer_con, nid))
            handle_peer_thread.start()

            all_client_threads.append(handle_peer_thread)

        except KeyboardInterrupt:
            print("[!] Keyboard Interrupted!")
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            for thread in all_client_threads:
                thread.join()
                break
        except Exception as e:
            print(e)

    DPRINT("***Exiting the loop")

    for thread in all_client_threads:
        thread.join()
    return


def handle_peer(peer_con, nid):
    data_received = recv_data(peer_con)

    if not data_received:
        return

    # Send ACK
    peer_con.sendall(b"ACK")
    peer_con.close()

    data_received = json.loads(data_received)
    pid = data_received["my_id"]

    if data_received["msg_type"] == "HELLO":
        DPRINT("Hello received from:", pid)

    if data_received["msg_type"] == "SHARES":
        DPRINT("Received Shares")
        receive_shares(nid, pid, data_received)

    if data_received["msg_type"] == "DLogNizkKey":
        DPRINT("DLogNizk")
        handleDlogNizk(pid, data_received)
    return


def sendId2peers(nid):
    data_to_send = {'msg_type': "HELLO",
                    'my_id': nid
                    }
    data_to_send = json.dumps(data_to_send)

    for pid in range(N_NODES):
        if nid != pid:
            print("Sending Hello to:", pid)
            DPRINT("Sending Hello to:", pid)
            send2Node(nid, pid, data_to_send)


def sendShareCommits2Peers(M, nid):
    global tx_count
    global epoch

    share_filename = "./tmp/node" + str(nid) + "share.txt"
    share_dash_filename = "./tmp/node" + str(nid) + "share_dash.txt"

    f = open(share_filename)
    fdash = open(share_dash_filename)

    keystrings = f.readlines()
    keydashstrings = fdash.readlines()

    DPRINT("key strings:", keystrings)
    DPRINT("key dash  strings:", keydashstrings)

    keystrings = keystrings[0]
    keydashstrings = keydashstrings[0]

    my_shares = deserializeElements(keystrings)
    my_shares_dash = deserializeElements(keydashstrings)

    DPRINT("my shares:", my_shares)
    DPRINT("my shares dash:", my_shares_dash)

    #####
    # node_share_index = json.load(open("../../secretsharing/blackbox/tmp/node_share_index.txt"))
    # node_share_index = json.load(open("./tmp/node_share_index.txt"))
    my_share_indices = node_share_index[str(nid)]

    DPRINT("my_share_indices:", my_share_indices)

    DPRINT("my node share index:", node_share_index[str(nid)])
    DPRINT("my_shares length:", len(my_shares))

    DPRINT("node_share_index", node_share_index)
    DPRINT("node_share_index.keys()", node_share_index.keys())

    '''
    for i in range(len(node_share_index.keys())):
        print("node_share_index[",i,"]", node_share_index[str(i)])
    '''

    for sindex in range(len(my_share_indices)):

        tx_count = tx_count + 1

        DPRINT("my_shares[sindex]:", my_shares[sindex])
        DPRINT("my_shares_dash[sindex]:", my_shares_dash[sindex])

        S, S_dash, rho_commits, rho_commit_strings, RHO, RHO_dash, dlog_commits, dlog_commit_strings = rhoCommitPSS(
            M, my_shares[sindex], my_shares_dash[sindex])

        querykey = "ID" + str(nid) + "tx_count" + str(tx_count) + "epoch" + str(epoch) + str(
            time.strftime("%Y-%m-%d-%H-%M-%S"))

        RHO_strings = []
        RHO_dash_strings = []
        for i in range(len(RHO)):
            RHO_strings.append(group.serialize(RHO[i]))
            RHO_dash_strings.append(group.serialize(RHO_dash[i]))

        rindex = my_share_indices[sindex]
        # Save random shares generated by self
        generated_shares[str(rindex)]['S'] = str(S)
        generated_shares[str(rindex)]['S_dash'] = str(S_dash)
        generated_shares[str(rindex)]['PedersenCommits'] = str(rho_commits)
        generated_shares[str(rindex)]['PedersenCommitStrings'] = str(rho_commit_strings)
        generated_shares[str(rindex)]['RHOStrings'] = str(RHO_strings)
        generated_shares[str(rindex)]['RHODashStrings'] = str(RHO_dash_strings)
        generated_shares[str(rindex)]['DlogCommits'] = str(dlog_commits)
        generated_shares[str(rindex)]['DlogCommitStrings'] = str(dlog_commit_strings)

        generated_shares[str(rindex)]['DlogCom'] = dlog_commits
        generated_shares[str(rindex)]['RHO'] = RHO
        generated_shares[str(rindex)]['RHODash'] = RHO_dash
        generated_shares[str(rindex)]['PederCom'] = rho_commits

        # Broadcast using Tendermint
        tobdx = {'my_id': nid, 'BroadcastCommit': str(rho_commit_strings), 'epoch': 0}
        broadcast(tobdx, querykey)

        DPRINT("S:", S)
        DPRINT("rho_commits:", rho_commits)
        DPRINT("RHO:", RHO)
        # either send to the stored PID or just send to the node list
        # here sending to each stored node in the peer list

        # N_M_map = json.load(open("./tmp/N_M_map.txt"))
        # node_share_index = json.load(open("./tmp/node_share_index.txt"))

        # for pid in list(connections.keys()):
        #     # records[pid] = defaultdict(dict)

        for pid in range(N_NODES):
            if nid == pid:
                continue

            # converting elements to strings before sending
            DPRINT("pid:", pid)
            DPRINT("node_share_index[pid]", node_share_index[str(pid)])

            shares = []
            shares_dash = []

            shares_strings = []
            shares_dash_strings = []

            for index in node_share_index[str(pid)]:
                shares.append(S[index])
                shares_dash.append(S_dash[index])

                shares_strings.append(group.serialize(S[index]))
                shares_dash_strings.append(group.serialize(S_dash[index]))

            data_to_send = {'msg_type': "SHARES",
                            'my_id': nid,
                            'my_share_id': str(rindex),
                            'sindex': str(sindex),
                            'share_strings': str(shares_strings),
                            'share_dash_strings': str(shares_dash_strings),
                            'key': querykey}

            data_to_send = json.dumps(data_to_send)

            # Store what is being sent for later usage during complaints

            records[pid][str(sindex)] = data_to_send

            try:
                DPRINT("Sending shares to node nid:", pid)
                send2Node(nid, pid, data_to_send)

            except Exception as err:
                print("Exception while sending shares:", err)


def receive_shares(nid, pid, share_rcvd):
    rindex = share_rcvd["my_share_id"]

    try:

        try:
            rindex = share_rcvd["my_share_id"]
            my_rcvd_shares_strings[pid][str(rindex)] = share_rcvd['share_strings']
            my_rcvd_shares_dash_strings[pid][str(rindex)] = share_rcvd['share_dash_strings']

            # Deserialize to obtain the values
            my_rcvd_shares[pid][str(rindex)] = deserializeElements(share_rcvd['share_strings'])
            my_rcvd_shares_dash[pid][str(rindex)] = deserializeElements(share_rcvd['share_dash_strings'])

        except:
            print("something is wrong")


        query_key = share_rcvd['key']
        # Query from Tendermint

        # queried_result = query(query_key)
        # print("queried_result", queried_result)

        query_retries = 0
        while query_retries < 10:
            try:
                queried_result = query(query_key)
            except:
                print("exception in query")
                sleep(random.uniform(1.0,3.0))
                #sleep(1)
                query_retries += 1
            else:
                break
        DPRINT("queried_result:", queried_result)


        commits = queried_result['BroadcastCommit']
        final_commits = deserializeElements(commits)
            # DPRINT("final_commits:", final_commits)


        # DPRINT("\nExtracted the share", my_rcvd_shares[pid][str(rindex)])
        # DPRINT(type(my_rcvd_shares[pid][str(0)]))
        #print("final_commits", final_commits)

        peer_share_commits[pid][str(rindex)] = final_commits

    except Exception as err:
        print("Exception in dumping data:", err)

    verify_received_shares(pid, nid, rindex)


def verify_received_shares(pid, nid, rindex):
    M_my_rows = M[node_share_index[str(nid)]]
    DPRINT("My M rows:", M_my_rows)

    try:

        share_not_verified = 1 
        # if share is not verified on the other thread yet
        while share_not_verified:
            try:
                #pedersen_commits = peer_share_commits[pid]
                peer_rho_commits = peer_share_commits[pid][str(rindex)]
                shares_rcvd = my_rcvd_shares[pid][str(rindex)]
                shares_dash_rcvd = my_rcvd_shares_dash[pid][str(rindex)]
            except:
                sleep(1)
            else:
                share_not_verified = 0 

        DPRINT("shares_rcvd", shares_rcvd)
        DPRINT("shares_dash_rcvd", shares_dash_rcvd)

        verified_shares_counter = 0

        # Check each received share
        for i in range(len(shares_rcvd)):
            DPRINT("M_my_rows[", i, "]:", M_my_rows[i])
            # DPRINT("peer_rho_commits", peer_rho_commits)
            computed_share_commitment = (g ** shares_rcvd[i]) * (h ** shares_dash_rcvd[i])

            commitment_product = unity
            DPRINT("Initial commitment product", commitment_product)

            for j in range(len(M_my_rows[i])):
                if M_my_rows[i][j] == 1:
                    commitment_product = commitment_product * peer_rho_commits[j]

            if computed_share_commitment == commitment_product:
                DPRINT("Share[", i, "] Verified")
                verified_shares_counter += 1

        if verified_shares_counter == len(shares_rcvd):
            DPRINT("Great, share verified for peer ID:", pid, "and rindex", rindex)
        else:
            print("Something looks fishy, raising a complaint against peer ID:", pid)
            # nodes_verification_failed.append(pid)
            nodes_verification_failed.add(pid)
            node_indices_not_verified[pid].append(rindex)

    except Exception as err:
        print("Error during verification of shares:", err)


def broadcastDLogNIZK(nid):
    # node_share_index = json.load(open("../../secretsharing/blackbox/tmp/node_share_index.txt"))
    my_share_indices = node_share_index[str(nid)]

    for sindex in range(len(node_share_index[str(nid)])):
        rindex = my_share_indices[sindex]
        #
        share_not_generated = 1
        while share_not_generated:
            try:
                dlog_commit_strings = generated_shares[str(rindex)]['DlogCommitStrings']
                dlog_commits = generated_shares[str(rindex)]['DlogCom']
            except:
                sleep(0.2)
            else:
                share_not_generated = 0

        #dlog_commit_strings = generated_shares[str(rindex)]['DlogCommitStrings']
        # pedersen_commit_strings = generated_shares[str(rindex)]['PedersenCommitStrings']
        # RHO_strings = generated_shares[str(rindex)]['RHOStrings']
        # RHO_dash_strings = generated_shares[str(rindex)]['RHODashStrings']

        #dlog_commits = generated_shares[str(rindex)]['DlogCom']
        RHO = generated_shares[str(rindex)]['RHO']
        RHO_dash = generated_shares[str(rindex)]['RHODash']
        pedersen_commits = generated_shares[str(rindex)]['PederCom']

        # dlog_commits = deserializeElements(dlog_commit_strings)
        # pedersen_commits = deserializeElements(pedersen_commit_strings)
        # RHO = deserializeElements(RHO_strings)
        # RHO_dash = deserializeElements(RHO_dash_strings)

        zkp_vec = nizkpok_vec(dlog_commits, pedersen_commits, RHO, RHO_dash)

        tobdx = {
            'msg_type': 'DLOGNIZK',
            'my_id': nid,
            'DLogStrings': str(dlog_commit_strings),
            # 'PederStrings': str(pedersen_commit_strings),
            'NIZK': str(zkp_vec),
            'sindex': sindex,
            'rindex': rindex
        }

        global tx_count
        global epoch
        tx_count = tx_count + 1
        querykey = "NIZKID" + str(nid) + "tx_count" + str(tx_count) + "epoch" + str(epoch) + str(
            time.strftime("%Y-%m-%d-%H-%M-%S"))

        # Tendermint broadcast
        broadcast(tobdx, querykey)

        data_to_send = {
            'msg_type': 'DLogNizkKey',
            'my_id': nid,
            'key': querykey
        }
        data_to_send = json.dumps(data_to_send)

        for pid in range(N_NODES):
            if pid == nid:
                continue
            try:
                DPRINT("Sending Nizk query key to node nid:", pid)
                send2Node(nid, pid, data_to_send)
            except Exception as e:
                print("Error in sending DLogNizk Query Key to node-", pid, e)


def handleDlogNizk(pid, broadcastedDlogNizk):
    
    global nizk_count
    nizk_count += 1


    
    nizk_querykey = broadcastedDlogNizk['key']

    # query from Tendermint
    query_retries = 0 
    while query_retries < 10: 
        try:
            #queried_result = query(query_key)
            nizks[pid] = query(nizk_querykey)
        except:
            print("exception in query")
            sleep(random.uniform(1.0,3.0))
            query_retries += 1
        else:
            break
    DPRINT("queried_result:", queried_result)

    #nizks[pid] = query(nizk_querykey)

    verifyDlogNizk(nizks[pid], pid)
    return


def verifyDlogNizk(nizks, pid):

    dlog_strings = nizks['DLogStrings']
    nizk_vec = nizks['NIZK']
    # There seems to be some abuse in notation
    recv_rindex = nizks['rindex']

    # print("nizk_vec",nizk_vec,"type(nizk_vec):", type(nizk_vec), "nizk_vec[0]", nizk_vec[0])

    nizk_vec = deserializeElements(nizk_vec)
    dlog_commits = deserializeElements(dlog_strings)

    share_not_verified = 1
    while share_not_verified:
        try:
            pedersen_commits = peer_share_commits[pid][str(recv_rindex)]
        except:
            sleep(1)
        else:
            share_not_verified = 0

    #pedersen_commits = peer_share_commits[pid][str(recv_rindex)]

    # Add the first dlog commitment as public key share needed
    peer_dlog_commits[pid] = dlog_commits[0]

    '''
    print("Len of pedersen commits:", len(pedersen_commits))
    print("Len of dlog     commits:", len(dlog_commits))
    print("Len of nizk_vec:", len(nizk_vec))
    '''

    proofs = []
    for i in range(len(nizk_vec) // 3):
        c = nizk_vec[3 * i]
        u1 = nizk_vec[(3 * i) + 1]
        u2 = nizk_vec[(3 * i) + 2]
        # print("\n\nsent proof:", [c, u1, u2])
        proofs.append([c, u1, u2])  # Putting them back as lists, not sure if it is needed

        V1_dash = (g ** u1) * (dlog_commits[i] ** c)
        dlog_commit_inv = dlog_commits[i] ** (-1)

        V2_dash = (h ** u2) * ((pedersen_commits[i] * dlog_commit_inv) ** c)

        c_dash = group.hash((g, h, dlog_commits[i], pedersen_commits[i], V1_dash, V2_dash), ZR)

        c_str = str(c)
        c_str = c_str[:len(c_str) - 30]
        c_dash_str = str(c_dash)
        c_dash_str = c_dash_str[:len(c_dash_str) - 30]

        global DisqualifiedSet

        # TODO: This is a temporary fix , change charm code
        if group == group571:
            if c_str == c_dash_str:
                DPRINT("The NIZK proof is verified")
            else:
                DisqualifiedSet.add(pid)
        else:
            if (c == c_dash):
                DPRINT("The NIZK proof is verified")
            else:
                DisqualifiedSet.add(pid)

        '''
        if (c == c_dash):
            print("The NIZK proof is verified")
        else:
            global DisqualifiedSet
            DisqualifiedSet.add(pid)
        '''

def node_thread(nid):

    DPRINT("Starting Node: ", nid)
    print("Starting Node: ", nid)
    MY_PORT = BASE_PORT + nid
    DPRF_PORT = MY_PORT + 1000
    # start server part of node to receive Hello

    DPRINT("PHASE0: Attempting handshake with all the nodes")

    node_server_thread = threading.Thread(target=serverSock, args=(MY_IP, MY_PORT, nid))
    node_server_thread.start()

    sleep(60)

    # start client part to send hello to all other peers
    node_client_thread = threading.Thread(target=sendId2peers, args=(nid,))
    node_client_thread.start()
    node_client_thread.join()

    DPRINT("PHASE0: Finished the first handshake with all the nodes")

    # temp - delete lines later
    print("Finished handshake with all the nodes")

    '''
    node_server_thread.data_receive = False
    temp = socket.socket(socket.AF_INET,
                  socket.SOCK_STREAM).connect( (MY_IP, MY_PORT))
    node_server_thread.join()

    nf.M = genShamirDistMatrix(N_NODES)
    '''

    print("\nPHASE1: Sending shares to nodes")
    sharing_start = time.process_time()

    t_start = time.time()
    # Read M from file

    share_send_thread = threading.Thread(target=sendShareCommits2Peers, args=(M, nid))
    share_send_thread.daemon = False

    share_send_thread.start()
    share_send_thread.join()

    sharing_end = time.process_time()
    #
    # DPRINT("\nPHASE5: Broadcasting NIZKs")
    # # Broadcast NIZK
    gen_nizk_start = time.process_time()

    sleep(20)

    print("Sending DLog NIZK")
    broadcastDlogNizk_thread = threading.Thread(target=broadcastDLogNIZK, args=(nid,))
    broadcastDlogNizk_thread.daemon = False

    broadcastDlogNizk_thread.start()

    broadcastDlogNizk_thread.join()

    gen_nizk_end = time.process_time()


    print("len of my_rcvd_shares:", len(my_rcvd_shares)) 

    total_nizks = 0
    total_shares = len(node_share_index.keys())* len(node_share_index[str(nid)]) 

    for node_id in node_share_index.keys():
        total_nizks = total_nizks + len(node_share_index[node_id])
    total_nizks_expected = total_nizks - len(node_share_index[str(nid)])
    
    # Wait till all shares, nizks  are received
    #while not ((len(nizks) == N_NODES-1 ) and (len(my_rcvd_shares) == N_NODES -1)) :
    #    sleep(0.5)
    # 60 and 180 for 15 nodes

    print("total_nizks_expected:", total_nizks_expected)
    print("nizk_count:", nizk_count)

    timeout_check_start = time.time()
    max_limit = 60 * 20
    while time.time() - timeout_check_start < max_limit:
        #if (len(nf.nizks) == nf.N_NODES - 1) and (len(nf.my_rcvd_shares) == nf.N_NODES - 1):
        if (total_nizks_expected == nizk_count):
            print("All shares received, writing my share value to a file")
            break
        time.sleep(0.25)
    print("Received verified shares from: ", len(my_rcvd_shares), " nodes")



    timeout_begin = time.process_time()


    # To close the server socket, just making a temp connectioon
    node_server_thread.data_receive = False
    temp = socket.socket(socket.AF_INET,
                         socket.SOCK_STREAM).connect((MY_IP, MY_PORT))
    node_server_thread.join()


    t_end = time.time()

    timeout_end = time.process_time()


    sharing_time          = (sharing_end          - sharing_start)          * 1000
    gen_nizk_time         = (gen_nizk_end         - gen_nizk_start)         * 1000
    timeout_time          = timeout_end - timeout_begin
    total_time            = t_end - t_start  
    
    timing_output = [N_NODES, sharing_time, gen_nizk_time, timeout_time, total_time]

    print( "sharing_time:", sharing_time)
    print( "nizk_time:", gen_nizk_time)
    print( "timeout_time:", timeout_time)
    print( "total_time:", total_time)

    timingfilename = "./tmp/bbss_dkgtiming_n_"+str(N_NODES)+".csv"
    with open(timingfilename, "a") as f:
        writer = csv.writer(f)
        writer.writerow(timing_output)


if __name__ == "__main__":

    description = """
    This program provides a single node running the DKG instance
    """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-i", "--id", default=0, type=int, help="node id "
    )

    parser.add_argument(
        "-n", "--nodes", default=4, type=int, help="number of nodes in DKG"
    )

    parser.add_argument(
        "-m", "--malicious", default=0, type=int, help="is the node malicious"
    )

    args = parser.parse_args()

    global N_NODES
    global M

    N_NODES = args.nodes

    if N_NODES < 4:
        M = np.loadtxt("../../secretsharing/blackbox/bbssutil/matrices/m3.txt", dtype=int)
    elif N_NODES < 10:
        M = np.loadtxt("../../secretsharing/blackbox/bbssutil/matrices/m9.txt", dtype=int)
    elif N_NODES < 28:
        M = np.loadtxt("../../secretsharing/blackbox/bbssutil/matrices/m27.txt", dtype=int)
    elif N_NODES < 82:
        M = np.loadtxt("../../secretsharing/blackbox/bbssutil/matrices/m81.txt", dtype=int)
    M = np.array(M)

    node_thread(int(args.id))

    sys.exit(0)
    os.system("exit 0")
