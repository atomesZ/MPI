from init_data import *

def isend_loop(rank, msg):
    '''
        rank send msg to all other servers
    '''
    for server in range(NB_CLIENT, NB_SERVER):
        if server != rank:
            comm.isend(msg, dest=server, tag=SERVER_TAG)

def irecv_data():
    '''
         receive a data for a server
    '''
    st = MPI.Status()
    prb = comm.iprobe(source=MPI.ANY_SOURCE, status=st)
    server, data = None, None
    if prb:
        server = st.source
        req = comm.irecv(source=server)
        data = req.wait()
    return server, data


def election(rank_candidat, term):
    #comm.bcast("iwanttobecandidate", root=rank_candidat)
    isend_loop(rank_candidat, "iwanttobecandidate_term=" + str(term))

def im_the_leader(rank_leader):
    #print("BCAST SENT")
    #BCAST = comm.bcast("imtheleader", root=rank_leader)#, tag=SERVER_TAG) #bcast has no tag
    #print("BCAST :", BCAST, " rank_leader:", rank_leader)
    isend_loop(rank_leader, "imtheleader")

def heartbeat_leader(rank_leader,term):
    #comm.bcast("heartbeat_leader", root=leader)#, tag=SERVER_TAG)
    isend_loop(rank_leader, "heartbeat_leader"+str(term))

def heartbeat_follower(rank_leader):
    comm.isend("heartbeat_follower", dest=rank_leader, tag=SERVER_TAG)

def vote(rank_candidat):
    comm.isend("vote", dest=rank_candidat, tag=SERVER_TAG)