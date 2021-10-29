
# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

import sys
import time

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
        globals.status = "FOLLOWER"
        globals.term = 0
        globals.leader = -1
        #print("DEBUG - rank:", RANK, status, "term: ",term, "leader:",leader,"START")
        while True:
            time_loop()

            # if a server quit time_loop (no more heartbeat) so he want to be candidate
            if globals.status != "LEADER":
                globals.status = "CANDIDAT"
                globals.term += 1
                election(RANK)

        #print("DEBUG - rank:" + str(rank) + status+ " term: "+str(term)+" leader: "+str(leader)+" FINISH\n")

    # Clients code
    elif if_client:
        while True:
            # REPL Start:
            data = comm.recv(source=REPL_UID)
            if "START" in data:
                print("--DEBUG Client", RANK, "start")
                break
            elif "END" in data:
                exit(0)

        # TODO étape 3, redemander qui est le leader frequemment (ou du moins écouter pour une nouvelle election)
        #while(True): #envoie plsrs msg
        # demande qui est le leader ?
        st = MPI.Status()

        with open(f"client_input_{RANK}.txt") as f:

            comm.recv(source=MPI.ANY_SOURCE, status=st)
            globals.leader = st.source

            for send_data in f.readlines():
                send_data = send_data.strip('\n')

                comm.send(send_data, dest=globals.leader, tag=CLIENT_TAG)

                is_data_committed = False
                n_heartbeats_waited = 0

                while not is_data_committed:
                    time_start = now()
                    time_out = random.randint(globals.TIME_OUT[0], globals.TIME_OUT[1])

                    while True:  # now() - time_start < time_out:
                        server, data, tag = irecv_data()

                        if tag == CLIENT_COMMIT_CONFIRMATION:
                            is_data_committed = True
                            break

                        # Ask for leader and resend info
                        elif n_heartbeats_waited > 10:
                            # Ask for leader
                            isend_loop(RANK, None, tag_=ASKING_LEADER)

                            st = MPI.Status()
                            comm.recv(source=MPI.ANY_SOURCE, tag=ASKING_LEADER, status=st)
                            globals.leader = st.source

                            comm.send(send_data, dest=globals.leader, tag=CLIENT_TAG)

                            n_heartbeats_waited = 0
                            break

                        n_heartbeats_waited += 1
                        time.sleep(time_out / 1000)

                print("--DEBUG Client", RANK, "sent data:", send_data, "to leader:", globals.leader)
                time.sleep(3)

    # REPL's code
    else:
        main_repl()


if __name__ == "__main__":
    main()
