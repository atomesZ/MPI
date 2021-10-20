# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

import sys

# ------------------ IMPORT ----------------------
from repl import *

# ------------------ MAIN ----------------------

NB_CLIENT = int(sys.argv[1])
NB_SERVER = int(sys.argv[2])

def main():
    if SIZE != NB_CLIENT + NB_SERVER + 1:
        print("PROBLEM NUMBER PROCESSUS AND CLIENT SERVER")
        exit(1)

    # Servers code
    if if_server:
        # init each server
        '''
        status (leader / candidate / follower)
        term (counter : nb of election)
        leader (of the term)
        '''
        # each server is a follower first
        status = "FOLLOWER"
        term = 0
        leader = -1
        #print("DEBUG - rank:", RANK, status, "term: ",term, "leader:",leader,"START")
        while True:
            leader, term, status = time_loop(leader, term, status)

            # if a server quit time_loop (no more heartbeat) so he want to be candidate
            if status != "LEADER":
                status = "CANDIDAT"
                term += 1
                election(RANK,term)

        #print("DEBUG - rank:" + str(rank) + status+ " term: "+str(term)+" leader: "+str(leader)+" FINISH\n")

    # Clients code
    elif if_client:
        while(True):
            #REPL Start:
            data = comm.recv(source=REPL_UID)
            if "START" in data:
                print("--DEBUG Client",RANK,"start")
                break

        # TODO étape 3, redemander qui est le leader frequemment (ou du moins écouter pour une nouvelle election)
        #while(True): #envoie plsrs msg
        # demande qui est le leader ?
        st = MPI.Status()
        data = comm.recv(source=MPI.ANY_SOURCE,status=st)
        leader = st.source

        # send data #change CLIENT_MESSAGE_SIZE if you want a larger tab
        data = [RANK]

        data = np.array([len(data)] + data, dtype='i')
        comm.Send(data, dest=leader, tag=CLIENT_TAG)

        print("--DEBUG Client",RANK,"sent data:", data)

    # REPL's code
    else:
        main_repl()

if __name__ == "__main__":
    main()