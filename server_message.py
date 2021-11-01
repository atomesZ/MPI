from init_data import *
import numpy as np


def isend_loop(rank: int, msg, tag_: int = SERVER_TAG):
    """
        rank send msg to all other servers
    """
    for server in range(NB_CLIENT, NB_CLIENT + NB_SERVER):
        if server != rank:
            comm.isend(msg, dest=server, tag=tag_)


def isend_loop_client(msg: str, tag_: int = CLIENT_TAG):
    """
        rank send msg to all other clients
    """
    for client in range(NB_CLIENT):
        comm.isend(msg, dest=client, tag=tag_)


def listen_repl():
    data = comm.recv(source=REPL_UID)

    if "SPEED" in data:
        if "LOW" in data:
            globals.TIME_OUT = [450, 600]
        elif "MEDIUM" in data:
            globals.TIME_OUT = [300, 450]
        else:  # HIGH
            globals.TIME_OUT = [150, 300]
        print("--DEBUG Receive", data, "- new TIME_OUT", globals.TIME_OUT)
    
    elif "CRASH" in data:
        print(f"--DEBUG {RANK} Received a CRASH")
        while True:
            data = comm.recv(source=REPL_UID)
            if "RECOVERY" in data:
                print(f"--DEBUG {RANK} Received a RECOVERY")
                break

            elif "END" in data:
                exit(0)

    elif "RECOVERY" in data:
        print("--DEBUG Receive RECOVERY for a living process")
        pass  # process vivant

    elif "END" in data:
        exit(0)

    return data


def irecv_data():
    """
         receive a data for a server
    """
    st = MPI.Status()
    prb = comm.iprobe(source=MPI.ANY_SOURCE, status=st)
    server, data, tag = None, None, None
    if prb:
        server = st.source
        tag = st.tag
        if tag == REPL_TAG:
            data = listen_repl()
        else:
            data = comm.recv(source=server)

    return server, data, tag


def election(rank_candidat: int):
    isend_loop(rank_candidat, "iwanttobecandidate_term=" + str(globals.term))


def im_the_leader():
    isend_loop(globals.leader, "imtheleader")


def heartbeat_leader():
    isend_loop(globals.leader, "heartbeat_leader" + str(globals.term))


def heartbeat_follower():
    comm.isend(globals.len_commit_logs, dest=globals.leader, tag=HEARTBEAT_FOLLOWER)


def vote(rank_candidat: int):
    comm.isend("vote", dest=rank_candidat, tag=SERVER_TAG)


def send_to_leader(msg: str, tag_: int = FOLLOWER_ACKNOWLEDGE_CHANGES):
    comm.isend(msg, dest=globals.leader, tag=tag_)
