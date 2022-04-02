import sys , json, re , time, csv   
import os, threading, socket, ast
import numpy as np 

sys.path += ['./','../','../../']

from charm.core.engine.util     import *
from charm.core.math.integer    import *
from OpenSSL                    import SSL, crypto

from sys       import argv 
from time      import sleep
from operator  import add

from conf.connectionconfig       import *
from conf.groupparam             import *
from util.connectionutils        import *
from util.awstransactionbroadcast   import *
from util.nizk                   import *
from secretsharing.shamir.shamirsharing import *

#from dprf              import partial_eval


debug = 0
BASE_PORT = 6566
#MY_IP = "127.0.0.1"
MY_IP = ((requests.get('http://checkip.amazonaws.com')).text).strip()

MALICIOUS = 0

broadcast_counter = 0

peers                       = {}
connections                 = {}

my_rcvd_shares              = {}
my_rcvd_shares_dash         = {}
my_rcvd_shares_strings      = {}
my_rcvd_shares_dash_strings = {}

peer_share_commits          = {}
peer_dlog_commits           = {}

generated_shares            = {}

complaints                  = {}
records                     = {}
nizks                       = {}

accused_nodes               = []
nodes_verification_failed   = []

QualifiedSet                = []
DisqualifiedSet             = []

tx_count = 0
epoch = 0

node_share_index = json.load(open("../../secretsharing/shamir/tmp/sss_node_share_index.txt"))    

def DPRINT ( *args , **kwargs ) :
    if debug:
        print ( *args , **kwargs )

def deserializeElements(objects):
    object_byte_strings = re.findall(r"'(.*?)'", objects , re.DOTALL)
    object_strings  = [ str.encode(a) for a in object_byte_strings]
    elements = [group.deserialize(a) for a in object_strings]
    return elements


def verifyConnection(conn, cert, errnum, depth, ok):
    #print("Got Certificate from ", str(conn))
    return ok

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


def serverSock(MY_IP, MY_PORT):
    ctx = initSSLContext()
    s  = SSL.Connection( ctx , socket.socket ( socket.AF_INET , socket.SOCK_STREAM ))
    s.bind ( ( '', MY_PORT ) )
    s.listen ( N_NODES)
    for peer in range ( N_NODES-1 ) : 
        peer_con , peer_addr = s.accept ( ) 
        pid = recvInt ( peer_con)    #TODO: change this from int to data directly 
        print ( "Received Hello from the node " , pid , " at " , str ( peer_addr ) ) 
        peers[ pid ] = peer_con 
        #TODO: add acknowledgement 
    



def sendId2peers(nid ):
    ctx = initSSLContext ( ) 

    print("N_NODES,", N_NODES)
    for node_index in range ( N_NODES) :
        if (MY_IP != NODE_IP[node_index]):
        #if 1:
            if  (node_index != nid) :
                DPRINT("Attempting to send Hello to Node", node_index)
                try:

                    connection_retries = 30
                    while connection_retries > 0:
                        try:
                            s = SSL.Connection ( ctx , socket.socket ( socket.AF_INET , socket.SOCK_STREAM ))
                            s.connect ( ( NODE_IP[node_index], BASE_PORT+ node_index ) ) 
                            #s.connect ( ( "127.0.0.1", BASE_PORT+ node_index ) )
                        except Exception as e:
                            print("Retry connecto id:", node_index, "with exception", e)
                            sleep(1)
                            connection_retries -= 1

                        else:
                    #s.connect ( ( "127.0.0.1" , BASE_PORT+ node_index ) )
                            connections [node_index] = s 
                            print ( "Sending Hello to PORT" , BASE_PORT + node_index , " of Node" , node_index )
                            sendInt ( s , nid )
                            break 
                except Exception as e: print("Error while sending hello to node_id:", node_index, e)






'''
def sendId2peers(id ):
    ctx = initSSLContext ( )

    for node_index in range ( N_NODES) :
        if (MY_IP != NODE_IP[node_index]):
            if  (node_index != id) :
                DPRINT("Attempting to send Hello to Node", node_index)
                s = SSL.Connection ( ctx , socket.socket ( socket.AF_INET , socket.SOCK_STREAM ))
                #s.connect ( ( "127.0.0.1" , BASE_PORT+ node_index ) )
                s.connect ( ( NODE_IP[node_index], BASE_PORT+ node_index ) )
                connections [node_index] = s
                DPRINT ( "Sending Hello to PORT" , BASE_PORT + node_index , " of Node" , node_index )
                sendInt ( s , id )
'''


def sendShareCommits2Peers(M, nid):
    global tx_count 
    global epoch 
    tx_count = tx_count + 1

    ctx = initSSLContext ( )
    #S, S_dash , rho_commits, rho_commit_strings, RHO, RHO_dash, dlog_commits, dlog_commit_strings  = rhoCommit(M)

    t = None 
    if MALICIOUS:
        S, S_dash , rho_commits, rho_commit_strings, RHO, RHO_dash, dlog_commits, dlog_commit_strings  = shamirShareGenCommit(N_NODES, MALICIOUS, t)
    else:
        S, S_dash , rho_commits, rho_commit_strings, RHO, RHO_dash, dlog_commits, dlog_commit_strings  = shamirShareGenCommit(N_NODES)

    querykey = "ID"+str(nid)+"tx_count"+str(tx_count)+"epoch"+str(epoch) + str(time.strftime("%Y-%m-%d-%H-%M"))
    print(querykey)

    RHO_strings = []
    RHO_dash_strings = []
    for i in range(len(RHO)):
        RHO_strings.append(group.serialize(RHO[i]))
        RHO_dash_strings.append(group.serialize(RHO_dash[i]))



    #Save random shares generated by self 
    generated_shares['S']                      = str(S)
    generated_shares['S_dash']                 = str(S_dash)
    generated_shares['PedersenCommits']        = str(rho_commits)
    generated_shares['PedersenCommitStrings']  = str(rho_commit_strings)
    generated_shares['RHOStrings']             = str(RHO_strings)
    generated_shares['RHODashStrings']         = str(RHO_dash_strings)
    generated_shares['DlogCommits']            = str(dlog_commits)
    generated_shares['DlogCommitStrings']      = str(dlog_commit_strings)

    ############# Broadcast using Tendermint #####################
    tobdx= {'my_id':nid, 'BroadcastCommit':str(rho_commit_strings), 'epoch': 0} 
    broadcast(tobdx, querykey)
    
    DPRINT(S)
    DPRINT(rho_commits)
    DPRINT(RHO)
    #either send to the stored PID or just send to the node list 
    #here sending to each stored node in the peer list 

    DPRINT("printing peer list", peers)

    
    DPRINT("node_share_index", node_share_index)
    DPRINT("node_share_index.keys()", node_share_index.keys())

    
    for pid in list(connections.keys()):
        records[pid] = {}

        #converting elements to strings before sending 
        DPRINT("pid:", pid)
        DPRINT("node_share_index[pid]", node_share_index[str(pid)])
        

        shares = []
        shares_dash = []

        shares_strings  = []
        shares_dash_strings  = []

        for index in node_share_index[str(pid)]:
            shares.append(S[index])
            shares_dash.append(S_dash[index])

            shares_strings.append(group.serialize(S[index]))
            shares_dash_strings.append(group.serialize(S_dash[index]))

        #shares = S[node_share_index[str(pid)]]
        DPRINT(shares)

        #data_to_send = {'my_id':id, 'rho_commits': str(rho_commits), 'share':shares }
        data_to_send = {'msg_type':"SHARES", 
                        'my_id':nid, 
                        #'rho_commits': str(rho_commits), 
                        'share':str(shares), 
                        'share_strings':str(shares_strings), 
                        'share_dash_strings':str(shares_dash_strings), 
                        'key':querykey}
        #data_to_send = {'my_id':id, 'rho_commits': str(rho_commits), 'share':str(S[pid])}
        data_to_send = json.dumps(data_to_send)

        #Store what is being sent for later usage during complaints
        records[pid]['SENT_SHARES'] = data_to_send
        
        DPRINT (data_to_send)
        send_data(connections[pid], data_to_send)


def receive_shares():
    #TODO: Add time-out 

    for pid in peers.keys():
        share_commits_rcvd = recv_data(peers[pid])
        share_rcvd = json.loads(share_commits_rcvd)
        
        DPRINT ("\nReceived something:\n", share_rcvd)

        #my_rcvd_shares[pid]= ast.literal_eval(share_rcvd['share'])[0][0]
        my_rcvd_shares[pid]= ast.literal_eval(share_rcvd['share'])
        DPRINT("My received shares", my_rcvd_shares)
        '''
        peer_share_commits[pid]= ast.literal_eval(share_rcvd['rho_commits'])
        '''
        
        #Store in strings from for complaint phase
        my_rcvd_shares_strings[pid] = share_rcvd['share_strings']
        my_rcvd_shares_dash_strings[pid]= share_rcvd['share_dash_strings']

        #Deserialize to obtain the values
        my_rcvd_shares[pid]= deserializeElements(share_rcvd['share_strings'])
        my_rcvd_shares_dash[pid]= deserializeElements(share_rcvd['share_dash_strings'])
        DPRINT("My received shares", my_rcvd_shares)

        query_key = share_rcvd['key'] 
        #############Query from Tendermint############
        
        queried_result = query(query_key)
        DPRINT("queried_result", queried_result)
        
        commits = queried_result['BroadcastCommit']
        final_commits = deserializeElements(commits)
        DPRINT(final_commits)


        DPRINT("\nExtracted the share", my_rcvd_shares[pid])
        peer_share_commits[pid] = final_commits 


def add_received_shares():
    return

def verify_received_shares(M, nid):
    #M = np.loadtxt("m3.txt", dtype=int)             #TODO: Change the filename to variable 
    node_share_index = json.load(open("../../secretsharing/shamir/tmp/sss_node_share_index.txt"))
    M_row_index_for_pid = node_share_index[str(nid)]  
    M_my_rows = M[node_share_index[str(nid)]]
    DPRINT("My M rows:", M_my_rows)
    

    for pid in peers.keys():
        peer_rho_commits =  peer_share_commits[pid]
        shares_rcvd      =  my_rcvd_shares[pid]
        shares_dash_rcvd =  my_rcvd_shares_dash[pid]

        if len(M_my_rows) != len(shares_rcvd):
            print("Eroor!: The number of nodes' rows in M and number of shares received are not same")

        '''
        com(s_i) = (C_i)**(m_{i,1}) * (C_i)**(m_{i,2}) ... * (C_i)**(m_{i,e})
        '''
        #g = group.encode(decoded_g, True)
        #h = group.encode(decoded_h, True)

        DPRINT("shares_rcvd", shares_rcvd)
        DPRINT("shares_dash_rcvd", shares_dash_rcvd)

        verified_shares_counter = 0

        #Check each received share
        for i in range(len(shares_rcvd)):
            DPRINT("M_my_rows[",i,"]:", M_my_rows[i])
            DPRINT("peer_rho_commits", peer_rho_commits)
            computed_share_commitment = (g ** shares_rcvd[i]) * ( h ** shares_dash_rcvd[i])

            commitment_product = g_rand ** zero  #Initialize to unity element  
            
            for j in range(len(M_my_rows[i])) :
                b = group.init(ZR, int(M_my_rows[i][j]))
                commitment_product = commitment_product * (peer_rho_commits[j] ** b)
            
            DPRINT("computed_share_commitment:", computed_share_commitment, "commitment_product", commitment_product)
            if (computed_share_commitment == commitment_product):
                DPRINT("Share[",i,"] Verified")
                verified_shares_counter += 1
            
        if(verified_shares_counter == len(shares_rcvd)):
            print("Great, all shares verified for peer ID:",pid )
        else:
            print("Something looks fishy, raising a complaint against peer ID:", pid)
            nodes_verification_failed.append(pid)         
        
def broadcastFailedNodeList(nid):

    print("Broadcasting accusations now")

    global tx_count
    global epoch
    tx_count = tx_count + 1
    accusation_query_key = ""

    total_accusations = []
    for pid in nodes_verification_failed:
        accusation = {}
        accusation['node_id']= pid
        accusation['shares'] = my_rcvd_shares_strings[pid]
        accusation['shares_dash'] = my_rcvd_shares_dash_strings[pid]
        total_accusations.append(accusation)
    accusations_string = json.dumps(total_accusations)

    complaint = {'msg_type':"COMPLAINT",
                 'my_id':nid,
                 'accusation': accusations_string
                 #'accusation': total_accusations
                 }
    complaint = dict(complaint)
    accusation_querykey = "AccusationFromID"+str(nid)+"tx_count"+str(tx_count)+"epoch"+str(epoch) + str(time.strftime("%Y-%m-%d-%H-%M"))

    ######### Broadcast the complaint using Tendermint 
    broadcast(complaint, accusation_querykey)


    ########## Send indication to all nodes 
    for pid in list(connections.keys()):

        yesorno = ""
        if pid in nodes_verification_failed:
            yesorno = "yes"
        else:
            yesorno = "no"

        data_to_send = {'msg_type'    :"COMPLAINT_INDICATION",
                        'my_id'       :nid,
                        'key'         :accusation_querykey,
                        'accusing_you': yesorno }
        #data_to_send = {'my_id':id, 'rho_commits': str(rho_commits), 'share':str(S[pid])}
        data_to_send = json.dumps(data_to_send)
        DPRINT (data_to_send)
        send_data(connections[pid], data_to_send)

def handleBrocastComplaints(M,nid):
     
    for pid in peers.keys():
        try :
            broadcastedComplaint = recv_data(peers[pid])
        except:
            print("Exception in handling broadcast complaints for node id:", pid)
            continue

        else:    
            broadcastedComplaint = json.loads(broadcastedComplaint)

            if (broadcastedComplaint['msg_type'] == "COMPLAINT_INDICATION"):
                am_I_accused = broadcastedComplaint['accusing_you']
                if (am_I_accused == "yes"):
                    accused_by_id = broadcastedComplaint['my_id'] 
                    #Now broadcast shares sent to the node of accused_by_id 

                    global tx_count
                    global epoch
                    tx_count = tx_count + 1

                    broadcast_sent_shares = records[accused_by_id]['SENT_SHARES']
                    tobdx= {'my_id':nid, 'Reply2Complaint_SentShares':broadcast_sent_shares, 'epoch': 0, 'accused_by_id':accused_by_id}
                    replykey = "From"+str(nid)+"Reply2AccusationBy"+str(accused_by_id)+"tx_count"+str(tx_count)+"epoch"+str(epoch) + str(time.strftime("%Y-%m-%d-%H-%M"))

                    ############ Tendermint Broadcast#########
                    broadcast(tobdx, replykey)

                    # Again send this to everyone 

                    data_to_send = {'msg_type'    :"REPLY2COMPLAINT",
                                    'my_id'       :nid,
                                    'key'         :replykey,
                                    'accused_by_id'  : accused_by_id
                                    }
                    #data_to_send = {'my_id':id, 'rho_commits': str(rho_commits), 'share':str(S[pid])}
                    data_to_send = json.dumps(data_to_send)
                    DPRINT (data_to_send)
                    send_data(connections[pid], data_to_send)

                # Check validity of the accusation                 

                accusation_querykey = broadcastedComplaint['key']
                ###### query from Tendermint  
                complaints[pid] = query(accusation_querykey)

                DPRINT(complaints[pid])

                complaintVerify(complaints[pid], M, nid)

                #TODO: This part can be modular - can reuse code from verifying shares 


def complaintVerify(complaints, M, nid):

    accuser_nid = complaints['my_id'] #Node that raised a complaint, we need to use his rows 
    accusations = complaints['accusation']
    accusations = json.loads(accusations) #List of dictionaries - Many nodes against whom accuser sends a complaint 

    node_share_index = json.load(open("../../secretsharing/shamir/tmp/sss_node_share_index.txt"))
    M_rows = M[node_share_index[str(accuser_nid)]]



    for accstn in accusations:
        DPRINT("accstn:",accstn)
        accused_nid = accstn['node_id']

        #Global record of all accused nodes 
        accused_nodes.append(accused_nid)


        #********************
        return 

        #*******************

        if (accused_nid == nid):
            continue 
        accuser_shares = deserializeElements(accstn['shares'])
        accuser_shares_dash  = deserializeElements(accstn['shares_dash'])

        peer_rho_commits =  peer_share_commits[accused_nid]    

        g_rand = group.random(G)
        #g = group.encode(decoded_g, True)
        #h = group.encode(decoded_h, True)

        #g = group.encode(decoded_g)
        #h = group.encode(decoded_h)

        verified_shares_counter = 0

        #Check each received share
        for i in range(len(accuser_shares)):
            DPRINT("M_rows[",i,"]:", M_rows[i])
            computed_share_commitment = (g ** accuser_shares[i]) * ( h ** accuser_shares_dash[i])

            commitment_product = unity 

            for j in range(len(M_rows[i])) :
                b = group.init(ZR, int(M_rows[i][j]))
                commitment_product = commitment_product * (peer_rho_commits[j] ** b)

            DPRINT("computed_share_commitment:", computed_share_commitment, "commitment_product", commitment_product) 
            if (computed_share_commitment == commitment_product):
                print("Share[",i,"] Verified")
                verified_shares_counter += 1

        if(verified_shares_counter == len(accuser_shares)):
            print("Great, all shares verified for peer ID:",accused_nid )
            print("Its a wrong accusation!!")
            global QualifiedSet, DisqualifiedSet
            QualifiedSet.append(accused_nid)
            #DisqualifiedSet.append(accuser_nid)
        else:
            DisqualifiedSet.append(accused_nid)



def handleBrocastReplies(M,nid):
    print("Handling Broadcast Replies")
    #print("accused_nodes", accused_nodes)
    for pid in peers.keys():
        if pid in set(accused_nodes):
            try :
                broadcastedReply = recv_data(peers[pid])
                DPRINT("broadcastedReply:", broadcastedReply)
            except:
                print("Exception in handling broadcast replies to complaints at peer id:", pid)
                continue

            else:
                broadcastedReply = json.loads(broadcastedReply)


                if (broadcastedReply['msg_type'] == "REPLY2COMPLAINT"):

                    querykey = broadcastedReply['key']

                    reply2complaint = query(querykey)

                    accuser_nid = reply2complaint['accused_by_id']
                    accused_nid  = reply2complaint['my_id']

                    accuser_shares_sent = json.loads(reply2complaint['Reply2Complaint_SentShares'])

                    DPRINT("accuser_shares_sent:",accuser_shares_sent)

                    accuser_shares      = deserializeElements(accuser_shares_sent['share_strings'])
                    accuser_shares_dash = deserializeElements(accuser_shares_sent['share_dash_strings'])

                    peer_rho_commits =  peer_share_commits[accused_nid]

                    node_share_index = json.load(open("../../secretsharing/shamir/tmp/sss_node_share_index.txt"))
                    M_rows = M[node_share_index[str(accuser_nid)]]

                    verified_shares_counter = 0

                    #Check each received share
                    for i in range(len(accuser_shares)):
                        DPRINT("M_rows[",i,"]:", M_rows[i])
                        computed_share_commitment = (g ** accuser_shares[i]) * ( h ** accuser_shares_dash[i])

                        commitment_product = unity

                        for j in range(len(M_rows[i])) :
                            b = group.init(ZR, int(M_rows[i][j]))
                            commitment_product = commitment_product * (peer_rho_commits[j] ** b)

                        DPRINT("computed_share_commitment:", computed_share_commitment, "commitment_product", commitment_product)
                        if (computed_share_commitment == commitment_product):
                            DPRINT("Share[",i,"] Verified")
                            verified_shares_counter += 1

                    if(verified_shares_counter == len(accuser_shares)):
                        print("Great, all shares verified for peer ID:",accused_nid )
                        print("Its a wrong accusation!!")
                        global QualifiedSet, DisqualifiedSet
                        QualifiedSet.append(accused_nid)
                        DisqualifiedSet.append(accuser_nid)
                    else:
                        print("Node "+ str(accused_nid)+ " is indeed malicious!")
                        DisqualifiedSet.append(accused_nid)

def broadcastDLogNIZK(nid):

    dlog_commit_strings     = generated_shares['DlogCommitStrings']
    pedersen_commit_strings = generated_shares['PedersenCommitStrings']
    RHO_strings             = generated_shares['RHOStrings']
    RHO_dash_strings        = generated_shares['RHODashStrings']

    dlog_commits     = deserializeElements(dlog_commit_strings)
    pedersen_commits = deserializeElements(pedersen_commit_strings)
    RHO              = deserializeElements(RHO_strings)
    RHO_dash         = deserializeElements(RHO_dash_strings)

    zkp_vec = nizkpok_vec(dlog_commits, pedersen_commits, RHO, RHO_dash)

    tobdx   = {
            'msg_type'    : 'DLOGNIZK',
            'my_id'       : nid,
            'DLogStrings' : str(dlog_commit_strings),
            'NIZK'        : str(zkp_vec)
            }

    global tx_count
    global epoch
    tx_count = tx_count + 1
    querykey = "NIZKID" + str(nid) + "tx_count" + str(tx_count) + "epoch" + str(epoch) + str(time.strftime("%Y-%m-%d-%H-%M"))
    
    #Tendermint broadcast 
    broadcast(tobdx, querykey)

    data_to_send = {
            'msg_type': 'DLogNizkKey',
            'my_id'   : nid,
            'key'     : querykey
            }
    data_to_send = json.dumps(data_to_send)

    #Individual key send 
    for pid in list(connections.keys()):
        send_data(connections[pid], data_to_send)

def handleDlogNizk(nid):

    DPRINT("Handling DLog NIZK")

    for pid in peers.keys():
        try :
            broadcastedDlogNizk= recv_data(peers[pid])
        except:
            print("Exception: Have not received NIZK from node:", pid)
            continue

        else:
            broadcastedDlogNizk= json.loads(broadcastedDlogNizk)

            if (broadcastedDlogNizk['msg_type'] == "DLogNizkKey"):
                nizk_nid      = broadcastedDlogNizk['my_id']
                nizk_querykey = broadcastedDlogNizk['key'] 

                ###### query from Tendermint  
                nizks[pid] = query(nizk_querykey)

                verifyDlogNizk(nizks[pid], pid)
    return 

def verifyDlogNizk(nizks, pid):
    if (nizks['msg_type'] == "DLOGNIZK" ):
        print("The received message is dlognizk")
    DPRINT("nizks received:", nizks)
    nizk_nid     = nizks['my_id']
    dlog_strings = nizks['DLogStrings']
    nizk_vec     = nizks['NIZK']

    #print("nizk_vec",nizk_vec,"type(nizk_vec):", type(nizk_vec), "nizk_vec[0]", nizk_vec[0])

    nizk_vec =         deserializeElements(nizk_vec)
    dlog_commits =     deserializeElements(dlog_strings)
    pedersen_commits = peer_share_commits[pid]

    #Add the first dlog commitment as public key share needed 
    peer_dlog_commits[pid] = dlog_commits[0] 

    #g = group.encode(decoded_g, True)
    #h = group.encode(decoded_h, True) 

    DPRINT("Len of pedersen commits:", len(pedersen_commits))
    DPRINT("Len of dlog     commits:", len(dlog_commits))
    DPRINT("Len of nizk_vec:", len(nizk_vec))

    proofs = []
    for i in range(len(nizk_vec)//3):
        c = nizk_vec[3*i]
        u1 = nizk_vec[(3*i)+1]
        u2 = nizk_vec[(3*i)+2]
        DPRINT("\n\nsent proof:", [c, u1, u2])
        proofs.append([c,u1,u2]) #Putting them back as lists, not sure if it is needed

        V1_dash = (g ** u1) * (dlog_commits[i] ** c)

        dlog_commits_inv = dlog_commits[i] ** (-1)
        V2_dash = (h ** u2) * ((pedersen_commits[i] * dlog_commits_inv )**c)

        c_dash = group.hash((g,h,dlog_commits[i],pedersen_commits[i], V1_dash, V2_dash), ZR)

        #print("c_dash:",c_dash, "dlog_commit:", dlog_commits[i], "pedersen_commit:", pedersen_commits[i], "V1_dash:", V1_dash, "V2_dash", V2_dash)
        if (c == c_dash):
            print("The NIZK proof is verified")
        else:
            global DisqualifiedSet
            DisqualifiedSet.append(pid)



def dprf_mode(nid, DPRF_PORT):
    ctx = initSSLContext()
    s  = SSL.Connection(ctx,socket.socket(socket.AF_INET,socket.SOCK_STREAM))
    s.bind (( '',DPRF_PORT))
    s.listen (N_NODES + 1) #TODO: Make it just one 

    client_con , client_addr = s.accept ( )
    request = recv_data(client_con)    
    print ( "Received request from the client at " , str ( client_addr ) )
    
    request = json.loads(request)
    DPRINT(request)
    X = request['publicstring'] 
    keytype = request['keytype']

    #par_key will be a list 
    par_key = partial_eval(nid, X, keytype )
    serial_par_key = [group.serialize(key) for key in par_key]
    print("serial_par_key:", serial_par_key)
    
    data_to_send= {
            'my_id':nid,
            'partialEval': str(serial_par_key)
            }

    data_to_send = json.dumps(data_to_send)
    #data_to_send = "Server"+ str(nid) + "Says: hi"
    #oclient_con.sendall("Server Says:hi"+str(nid))
    send_data(client_con, data_to_send)

def computePubKey(nid):

    publicKey = group.random(G)
    publicKey = publicKey/publicKey # just make it unity 

    for pid in peers.keys():
        if pid not in DisqualifiedSet:
            publicKey = publicKey * peer_dlog_commits[pid]

    return publicKey 

def node_thread(nid):
    DPRINT("Starting Node: ", nid)
    MY_PORT = BASE_PORT + nid
    DPRF_PORT = MY_PORT + 1000
    #start server part of node to receive Hello


    node_server_thread = threading.Thread(target = serverSock, args = (MY_IP, MY_PORT))
    node_server_thread.daemon = False 
    node_server_thread.start()

    sleep_time = (N_NODES - int(args.id))
    sleep(sleep_time)

    #start client part to send hello to all other peers 
    node_client_thread = threading.Thread(target = sendId2peers, args = (nid, ))
    node_client_thread.daemon = False

    node_client_thread.start()

    node_server_thread.join()
    node_client_thread.join()
    
    DPRINT("Finished the first handshake with all the nodes")
    sleep(1) 



    t_start =time.time()


    print("\nPHASE1: Sending shares to nodes")
    sharing_start = time.process_time()


    #Read M from file 

    M = genShamirDistMatrix(N_NODES)


    #M = np.loadtxt("./temp/m27.txt", dtype=int)    #TODO: Change this to dynamic file path 
    #M = np.loadtxt("M.txt", dtype=int)
    M = np.array(M)


    t_start2 = time.time()

    share_send_thread = threading.Thread(target=sendShareCommits2Peers, args=(M,nid ))
    share_send_thread.daemon = False

    share_send_thread.start()
    share_send_thread.join()

    sharing_end = time.process_time()


    #Receive shares
    print("PHASE1: Receiving shares from nodes")

    receive_start = time.process_time()
    share_receive_thread= threading.Thread(target=receive_shares, args=( ))
    share_receive_thread.daemon = False

    share_receive_thread.start()

    share_send_thread.join()
    share_receive_thread.join()

    receive_end = time.process_time()

    #Verify commitments 
    print("\nPHASE2: Verifying received commitments ")
    verify_start = time.process_time()

    share_verify_thread = threading.Thread(target=verify_received_shares, args=(M,nid ))
    share_verify_thread.daemon = False

    share_verify_thread.start()
    share_verify_thread.join()
    verify_end = time.process_time()

    '''
    #Broadcast complaints
    print("\nPHASE3: Broadcasting complaints")
    complaint_start = time.process_time()

    share_verify_thread = threading.Thread(target=broadcastFailedNodeList, args=(id,))
    share_verify_thread.daemon = False

    share_verify_thread.start()
    share_verify_thread.join()

    complaint_end = time.process_time()

    #Handle all complaints (including on self)
    if not MALICIOUS:
        sleep(0.5)
    print("\nPHASE4: Verifying received complaints")
    handle_complaint_start = time.process_time()

    handleComplaint_thread = threading.Thread(target=handleBrocastComplaints, args=(M, id ))
    handleComplaint_thread.daemon = False

    handleComplaint_thread.start()
    handleComplaint_thread .join() 

    handle_complaint_end = time.process_time()

    print("\nPHASE4: Verifying replies received  against complaints")

    handle_reply_start = time.process_time()

    handleReply_thread = threading.Thread(target=handleBrocastReplies, args=(M, id ))
    handleReply_thread.daemon = False

    handleReply_thread.start()
    handleReply_thread.join()

    handle_reply_end = time.process_time()



    # Compute own share from qualified set
    if id != 0:
        my_secret_share = [0]*len(my_rcvd_shares[0])
    else:
        my_secret_share = [0]*len(my_rcvd_shares[1])   #Assuming atleast one other node exists 


    for key in my_rcvd_shares.keys():
        if key not in DisqualifiedSet:
           my_secret_share = list(map(add, my_secret_share, my_rcvd_shares[key])) 
           my_secret_share_dash = list(map(add, my_secret_share, my_rcvd_shares_dash[key])) 

    print("my_secret_share", my_secret_share)
    my_share_strings = [str(group.serialize(share)) for share in my_secret_share] 
    my_share_dash_strings = [str(group.serialize(share)) for share in my_secret_share] 
    
    #Write secret share to a file 
    share_filename = "./tmp/node" + str(id) + "share.txt"
    json.dump(my_share_strings, open(share_filename,'w'))
    share_dash_filename = "./tmp/node" + str(id) + "share_dash.txt"
    json.dump(my_share_dash_strings, open(share_dash_filename,'w'))
    '''


    #Broadcast NIZK 
    print("\nPHASE5: Broadcasting NIZKs")
    gen_nizk_start = time.process_time()

    broadcastDlogNizk_thread   = threading.Thread(target=broadcastDLogNIZK, args=(nid,))
    broadcastDlogNizk_thread.daemon = False

    broadcastDlogNizk_thread.start()
    broadcastDlogNizk_thread.join()

    gen_nizk_end = time.process_time()    

    #Handle nizk
    print("\nPHASE6: Verifying received NIZKs")
    verify_nizk_start = time.process_time()

    handleNizk_thread  = threading.Thread(target=handleDlogNizk, args=(nid,))
    handleNizk_thread.daemon = False

    handleNizk_thread.start()
    handleNizk_thread.join()
    
    verify_nizk_end = time.process_time()

    '''
    #Run DPRF   
    share_verify_thread = threading.Thread(target=dprf_mode, args=(id,DPRF_PORT ))
    share_verify_thread.daemon = False

    share_verify_thread.start()
    share_verify_thread.join()
    '''

    t_end = time.time()


    t_end2 = time.time()

    '''
    print("Writing my share value to a file")
    nid = id
    if id != 0:
        my_secret_share = [0]*len(my_rcvd_shares[0])
    else:
        my_secret_share = [0]*len(my_rcvd_shares[1])   #Assuming atleast one other node exists 


    for key in my_rcvd_shares.keys():
        if key not in DisqualifiedSet:
           my_secret_share = list(map(add, my_secret_share, my_rcvd_shares[key])) 
           my_secret_share_dash = list(map(add, my_secret_share, my_rcvd_shares_dash[key])) 

    #print("my_secret_share", my_secret_share)
    my_share_strings = [str(group.serialize(share)) for share in my_secret_share] 
    my_share_dash_strings = [str(group.serialize(share)) for share in my_secret_share] 
    
    #Write secret share to a file 
    share_filename = "./tmp/node" + str(nid) + "share.txt"
    json.dump(str(my_share_strings), open(share_filename,'w+'))
    share_dash_filename = "./tmp/node" + str(nid) + "share_dash.txt"
    json.dump(str(my_share_dash_strings), open(share_dash_filename,'w+'))
    '''





    sharing_time          = (sharing_end          - sharing_start)          * 1000
    receive_time          = (receive_end          - receive_start)          * 1000
    verify_commit_time    = (verify_end           - verify_start)           * 1000
    #complaint_time        = (complaint_end        - complaint_start)        * 1000
    #complaint_handle_time = (handle_complaint_end - handle_complaint_start) * 1000
    #reply_handle_time     = (handle_reply_end     - handle_reply_start)     * 1000
    gen_nizk_time         = (gen_nizk_end         - gen_nizk_start)         * 1000
    verify_nizk_time      = (verify_nizk_end      - verify_nizk_start)      * 1000

    print("\n")
    print( "sharing_time:",          sharing_time)
    print( "receive_time:",          receive_time)
    print( "verify_commit_time:",    verify_commit_time)
    #print( "complaint_time:",        complaint_time)
    #print( "complaint_handle_time:", complaint_handle_time)
    #print( "reply_handle_time:",     reply_handle_time)
    print( "gen_nizk_time:",         gen_nizk_time)
    print( "verify_nizk_time:",      verify_nizk_time)
    print("\n")

    timing_output = [sharing_time, receive_time, verify_commit_time, gen_nizk_time, verify_nizk_time]

    total_process_time = sum(timing_output)
    total_clock_time = t_end - t_start
    total_clock_time2 = t_end2 - t_start2

    total_time = [total_process_time, total_clock_time, total_clock_time2]
    print("total time:", total_time)


    if group == group192:
        bits = 192
    elif group == group256:
        bits = 256
    elif group == group283:
        bits = 283
    elif group == group571:
        bits = 571

    if MALICIOUS:
        timingfilename = "./tmp/sss_dkgtiming_malicious_"+str(bits)+"bit_n_"+str(N_NODES)+".csv"
    else:
        timingfilename = "./tmp/sss_non_mal_dkgtiming"+str(bits)+"_n_"+str(N_NODES)+".csv"



    #out = open(timingfilename, 'a')
    #for column in timing_output:
    #    out.write('%d;' % column)
    #    out.write('\n')
    #out.close()

    with open(timingfilename, "a+") as f:
        writer = csv.writer(f)
        writer.writerow(timing_output)


if __name__ == "__main__" :


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
    N_NODES = args.nodes

    MALICIOUS = args.malicious


    node_thread( int(args.id))

    sys.exit(0)
    




