import sys

sys.path += ['./', '../', '../../']

import util.node_functions as nf
from   util.node_functions import *

# from secretsharing.shamir.shamirsharing import *

nf.node_share_index = json.load(open("../../secretsharing/blackbox/tmp/node_share_index.txt"))

def node_thread(nid):

    DPRINT("Starting Node: ", nid)
    print("Starting Node: ", nid)
    MY_PORT = BASE_PORT + nid
    DPRF_PORT = MY_PORT + 1000
    # start server part of node to receive Hello

    DPRINT("PHASE0: Attempting handshake with all the nodes")

    node_server_thread = threading.Thread(target=serverSock, args=(MY_IP, MY_PORT, nid))
    node_server_thread.start()

    sleep(2)

    # start client part to send hello to all other peers
    node_client_thread = threading.Thread(target=sendId2peers, args=(nid,))
    node_client_thread.start()
    node_client_thread.join()

    DPRINT("PHASE0: Finished the first handshake with all the nodes")

    # temp - delete lines later
    print("Finished handshake with all the nodes")
    print("\nPHASE1: Sending shares to nodes")

    t_start = time.time()

    for i in range(1):
        sharing_start = time.process_time()
        # Read M from file

        share_send_thread = threading.Thread(target=sendShareCommits2Peers, args=(nf.M, nid))
        share_send_thread.daemon = False

        share_send_thread.start()
        share_send_thread.join()

        sharing_end = time.process_time()

        DPRINT("\nPHASE5: Broadcasting NIZKs")
        # Broadcast NIZK
        gen_nizk_start = time.process_time()

        broadcastDlogNizk_thread = threading.Thread(target=broadcastDLogNIZK, args=(nid,))
        broadcastDlogNizk_thread.daemon = False

        broadcastDlogNizk_thread.start()

        broadcastDlogNizk_thread.join()
        gen_nizk_end = time.process_time()

        # Wait till all shares, nizks  are received
        # while not ((len(nizks) == N_NODES-1 ) and (len(my_rcvd_shares) == N_NODES -1)) :
        #    sleep(0.5)
        # 60 and 180 for 15 nodes

        
        timeout_begin = time.process_time()

        timeout_check_start = time.time()
        max_limit = 60 * 1.5
        while time.time() - timeout_check_start < max_limit:
            if (len(nf.nizks) == nf.N_NODES - 1) and (len(nf.my_rcvd_shares) == nf.N_NODES - 1):
                print("All shares received, writing my share value to a file")
                break
            time.sleep(0.5)
        DPRINT("Received verified shares from: ", len(nf.my_rcvd_shares), " nodes")

        

    t_end = time.time()

    # To close the server socket, just making a temp connectioon
    node_server_thread.data_receive = False
    temp = socket.socket(socket.AF_INET,
                         socket.SOCK_STREAM).connect((MY_IP, MY_PORT))
    node_server_thread.join()
    timeout_end = time.process_time()


    #Write share to file 
    if nid != 0:
        my_secret_share = [0]*len(my_rcvd_shares[0])
    else:
        my_secret_share = [0]*len(my_rcvd_shares[1])   #Assuming atleast one other node exists

    for key in my_rcvd_shares.keys():
        if key not in DisqualifiedSet:
           my_secret_share = list(map(add, my_secret_share, my_rcvd_shares[key]))
           my_secret_share_dash = list(map(add, my_secret_share, my_rcvd_shares_dash[key]))

    DPRINT("my_secret_share", my_secret_share)
    my_share_strings = [str(group.serialize(share)) for share in my_secret_share]
    my_share_dash_strings = [str(group.serialize(share)) for share in my_secret_share]

    share_filename = "./tmp/node" + str(nid) + "share.txt"
    share_pss_filename = "../../PSS/bbss_pss/tmp/node"+ str(nid) + "share.txt"

    json.dump(str(my_share_strings), open(share_filename,'w'))
    json.dump(str(my_share_strings), open(share_pss_filename,'w'))

    share_dash_filename = "./tmp/node" + str(nid) + "share_dash.txt"
    share_dash_pss_filename = "../../PSS/bbss_pss/tmp/node" + str(nid) + "share_dash.txt"

    json.dump(str(my_share_dash_strings), open(share_dash_filename,'w'))
    json.dump(str(my_share_dash_strings), open(share_dash_pss_filename,'w'))

    sharing_time          = (sharing_end          - sharing_start)          * 1000
    gen_nizk_time         = (gen_nizk_end         - gen_nizk_start)         * 1000
    timeout_time          = timeout_end - timeout_begin
    total_time            = t_end - t_start  
    
    timing_output = [nf.N_NODES, sharing_time, gen_nizk_time, timeout_time, total_time]

    print( "sharing_time:", sharing_time)
    print( "nizk_time:", gen_nizk_time)
    print( "timeout_time:", timeout_time)
    print( "total_time:", total_time)

    timingfilename = "./tmp/bbss_dkgtiming_n_"+str(nf.N_NODES)+".csv"
    with open(timingfilename, "a") as f:
        writer = csv.writer(f)
        writer.writerow(timing_output)


if __name__ == "__main__":
    description = """ 
    This program provides a single node running the DKG instance using verifiable black-box secret sharing
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

    nf.SECRET_SHARING = "BBSS"

    nf.N_NODES = args.nodes
    nf.MALICIOUS = args.malicious

    if nf.N_NODES < 4:
        nf.M = np.loadtxt("../../secretsharing/blackbox/bbssutil/matrices/m3.txt", dtype=int)
    elif nf.N_NODES < 10: 
        nf.M = np.loadtxt("../../secretsharing/blackbox/bbssutil/matrices/m9.txt", dtype=int)
    elif nf.N_NODES < 28: 
        nf.M = np.loadtxt("../../secretsharing/blackbox/bbssutil/matrices/m27.txt", dtype=int)
    elif nf.N_NODES < 82: 
        nf.M = np.loadtxt("../../secretsharing/blackbox/bbssutil/matrices/m81.txt", dtype=int)
    nf.M = np.array(nf.M)

    node_thread(int(args.id))

    sys.exit(0)
    os.system("exit 0")
