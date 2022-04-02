import sys , json, re , time, csv
import os, threading, socket, ast
import numpy as np


from OpenSSL                    import SSL, crypto
from sys                        import argv
from time                       import sleep
from operator                   import add

from charm.core.engine.util     import *
from charm.core.math.integer    import *


from operator  import add

sys.path += ['./','../']
from conf.connectionconfig                      import *
from conf.groupparam                            import *
from util.connectionutils                       import *
from mip_solve_lambda  import *
#from BBSS             import*

from dprf              import partial_eval

BASE_PORT   = 6566 + 1000
MY_IP       = "127.0.0.1"
CLIENT_PORT = 8566


shares = {}

def deserializeElements(objects):
    object_byte_strings = re.findall(r"'(.*?)'", objects , re.DOTALL)
    object_strings  = [ str.encode(a) for a in object_byte_strings]
    ####### check this 
    elements = [group256.deserialize(a) for a in object_strings]
    return elements



def initSSLContext():
    ctx = SSL.Context(SSL.SSLv23_METHOD)
    ctx.set_options(SSL.OP_NO_SSLv2)
    ctx.set_options(SSL.OP_NO_SSLv3)
    ctx.set_verify(
            SSL.VERIFY_PEER, verifyConnection
    ) # Demand a Certificate
    ctx.use_privatekey_file(CLIENT_PVT_KEY_FILE)
    ctx.use_certificate_file(CLIENT_CERT_FILE)
    ctx.load_verify_locations(CA_FILE)
    return ctx


def sendPublcStringnodes(X, keytype):
    ctx = initSSLContext ( )
    M_row_index  = []
    #M = np.loadtxt("./tmp/m3.txt", dtype=int)
    #N_M_map = json.load(open("./temp/N_M_map.txt"))
    #node_share_index = json.load(open("./temp/node_share_index.txt"))

    M = np.loadtxt("../secretsharing/blackbox/bbssutil/matrices/m9.txt", dtype=int)
    N_M_map          = json.load(open("../secretsharing/blackbox/tmp/N_M_map.txt"))
    node_share_index = json.load(open("../secretsharing/blackbox/tmp/node_share_index.txt"))

    shares_vec= []

    for node_index in range (N_NODES) :
        s = SSL.Connection ( ctx , socket.socket ( socket.AF_INET , socket.SOCK_STREAM ))
        s.connect ( ( "127.0.0.1" , BASE_PORT+ node_index ) )
        #s.bind ( ( '', CLIENT_PORT ) )
        #DPRINT ( "Sending",X, "to PORT" , BASE_PORT + node_index , " of Node" , node_index )

        request = {'keytype':keytype, 'publicstring':X}
        request = json.dumps(request)
        send_data(s ,request)

        try:
            data = recv_data(s)
            data = json.loads(data)
            #print("data received:", data)
        except:
            print("No data from node:", node_index)
        else:
            nid = data['my_id']
            #print("data[partialEval]:", data['partialEval'])
            partial_eval = deserializeElements(data['partialEval'])
            #print("partial_eval:", partial_eval)


            shares_vec = shares_vec + partial_eval 
            #Store shares in a dictionary         
            shares[nid] = str(partial_eval)

            M_row_index = M_row_index + node_share_index[str(nid)]
            
    ma_t = np.transpose(M[M_row_index])
    e  = np.zeros((len(ma_t),), dtype=int)
    e[0] = 1
    lambda_a = np.array(solve_for_lambda(ma_t, e), dtype=int) 
    print(lambda_a)

    shares_vec = np.array(shares_vec)

    #print(len(lambda_a))
    #print(len(shares_vec))

    lambda_zr = [group256.init(ZR,int(x)) for x in lambda_a]
   
    rand = group256.random(G)
    pubkey = rand/rand #Initialize to unity 

    if (len(lambda_a) == len(shares_vec)):
        if (keytype == "pub"):
            for i in range(len(lambda_a)):
                pubkey = pubkey * (shares_vec[i] ** lambda_zr[i])
            key = pubkey
        else: 
            secretkey = np.dot(shares_vec, lambda_zr)
            key = secretkey
    else:
        print("The vector lengths do not match ")

    print("Final key:", key)

if __name__ == "__main__":



    '''
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
    '''

    global N_NODES
    N_NODES = 4


    start_time = time.time()
    request_start = time.process_time()

    sendPublcStringnodes("easwar", "pub")

    request_end = time.process_time()

    end_time = time.time()

    total_request_time = ( request_end - request_start ) * 1000
    total_sys_time = end_time - start_time 

    print("total time for request and computation:", total_request_time)
    print("total time-time for request and computation:", total_sys_time)





