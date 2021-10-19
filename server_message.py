from init_data import *
import numpy as np


def isend_loop(rank, msg, tag_=SERVER_TAG):
    '''
        rank send msg to all other servers
    '''
    if tag_ == CHANGES_TO_COMMIT:
        assert type(msg) == list
        msg = np.array([len(msg)] + msg, dtype='i')

        send_function = comm.Isend
    else:
        send_function = comm.isend

    for server in range(NB_CLIENT, NB_CLIENT + NB_SERVER):
        if server != rank:
            send_function(msg, dest=server, tag=tag_)


def isend_loop_client(msg, tag_=CLIENT_TAG):
    '''
        rank send msg to all other clients
    '''
    for client in range(NB_CLIENT):
        comm.isend(msg, dest=client, tag=tag_)


def irecv_data():
    '''
         receive a data for a server
    '''
    st = MPI.Status()
    prb = comm.iprobe(source=MPI.ANY_SOURCE, status=st)
    server, data, tag = None, None, None
    if prb:
        server = st.source
        tag = st.tag
        # Special case if the data comes from the client since the data is in a buffer and not a string
        if tag == CLIENT_TAG or tag == FOLLOWER_ACKNOWLEDGE_CHANGES or tag == CHANGES_TO_COMMIT:
            buffer = np.empty(50, dtype='i')
            comm.Irecv(buffer, source=server)
            len_data = buffer[0]
            data = buffer[1:len_data + 1]
        else:
            data = comm.recv(source=server)

    return server, data, tag


def election(rank_candidat, term):
    isend_loop(rank_candidat, "iwanttobecandidate_term=" + str(term))


def im_the_leader(rank_leader):
    isend_loop(rank_leader, "imtheleader")


def heartbeat_leader(rank_leader,term):
    isend_loop(rank_leader, "heartbeat_leader"+str(term))


def heartbeat_follower(rank_leader):
    comm.isend("heartbeat_follower", dest=rank_leader, tag=SERVER_TAG)


def vote(rank_candidat):
    comm.isend("vote", dest=rank_candidat, tag=SERVER_TAG)


def send_to_leader(rank_leader, msg: list, tag_=FOLLOWER_ACKNOWLEDGE_CHANGES):
    msg = np.array([len(msg)] + msg, dtype="i")
    comm.Isend(msg, dest=rank_leader, tag=tag_)
