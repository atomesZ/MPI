from init_data import *
import numpy as np


def isend_loop(rank: int, msg: str, tag_: int = SERVER_TAG):
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
        globals.TIME_OUT
        if "LOW" in data:
            globals.TIME_OUT = [450, 600]
        elif "MEDIUM" in data:
            globals.TIME_OUT = [300, 450]
        else:  # HIGH
            globals.TIME_OUT = [150, 300]
        print("--DEBUG Receive", data, "- new TIME_OUT", globals.TIME_OUT)
    
    elif "CRASH" in data:
        print("--DEBUG Receive CRASH")
        while True:
            data = comm.recv(source=REPL_UID)
            if "RECOVERY" in data:
                print("--DEBUG Receive RECOVERY")
                recover()
                break
                # TODO ask leader for summary

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


def election(rank_candidat: int, term: int):
    isend_loop(rank_candidat, "iwanttobecandidate_term=" + str(term))


def im_the_leader(rank_leader: int):
    isend_loop(rank_leader, "imtheleader")


def heartbeat_leader(rank_leader: int, term: int):
    isend_loop(rank_leader, "heartbeat_leader" + str(term))


def heartbeat_follower(rank_leader: int):
    comm.isend("heartbeat_follower", dest=rank_leader, tag=SERVER_TAG)


def vote(rank_candidat: int):
    comm.isend("vote", dest=rank_candidat, tag=SERVER_TAG)


def send_to_leader(rank_leader: int, msg: str, tag_: int = FOLLOWER_ACKNOWLEDGE_CHANGES):
    comm.isend(msg, dest=rank_leader, tag=tag_)


def recover():
    # Ask for recovery
    isend_loop(RANK, None, tag_=RECOVERY_TAG)

    committed_logs = comm.recv(source=MPI.ANY_SOURCE, tag=RECOVERY_TAG)

    if committed_logs:
        with open(f"log_server_{RANK}.txt", "w") as f:
            f.writelines([f"{line}\n" for line in committed_logs])
