# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
import sys

# ------------------ IMPORT ----------------------
import mpi4py.MPI

from server_status_loop import *

# ------------------ MAIN ----------------------

if SIZE != NB_CLIENT + NB_SERVER:
    print("PROBLEM NUMBER PROCESSUS AND CLIENT SERVER")
    exit(1)

# Servers code
if if_server:
    #init each server
    '''
    status (leader / candidate / follower)
    term (counter : nb of election)
    leader (of the term)
    '''
    #each server is a follower first
    status = "FOLLOWER"
    term = 0
    leader = -1
    print("DEBUG - rank:", RANK, status, "term: ",term, "leader:",leader,"START")
    while(True):
        leader, term, status = time_loop(leader, term, status)

        # if a server quit time_loop (no more heartbeat) so he want to be candidate
        if status != "LEADER":
            status = "CANDIDAT"
            term += 1
            election(RANK,term)

    print("DEBUG - rank:" + str(rank) + status+ " term: "+str(term)+" leader: "+str(leader)+" FINISH\n")

# Clients code
else:
    # TODO étape 3, redemander qui est le leader frequemment (ou du moins écouter pour une nouvelle election)
    #while(True):
    #demande qui est le leader ?
    st = MPI.Status()
    data = comm.recv(source=MPI.ANY_SOURCE,status=st)
    leader = st.source

    #send data
    data = np.array([RANK], dtype='i')
    comm.Send([data, MPI.INT], dest=leader, tag=CLIENT_TAG)

    print("Client sent data.")
