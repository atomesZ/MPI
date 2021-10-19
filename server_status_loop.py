from server_message import *

import time
import numpy as np
import random

#time now
def now():
    return round(time.time() * 1000)

def candidat_loop(leader, status, term, time_out = random.randint(300,500)):
    '''
        A candidate can receive:
        "vote" ==> one follower voted for him
        "imtheleader" or "heartbeat_leader ==> an other candidate was elected before him
        "iwanttobecandidat" ==> a candidat ask him to vote for him

    '''
    #print("DEBUG - rank:" + str(rank) + status+ "term: "+str(term)+"leader:"+str(leader)+"candidat_loop START"+"\n")
    time_now = now()
    #votes counter, init with 1 (vote for himself)
    cpt = 1 #choose counter and not array, we dont know who votes for him
    while now() - time_now < time_out:
        server, data, tag = irecv_data()

        if data is not None:
            print("candidat_loop - rank", RANK, " data: " , data, " from: ", server)
            #if there is a leader ==> become follower
            if "imtheleader" in data or "heartbeat" in data:  # Si un autre candidat est devenu leader avant lui :sad:
                status = "FOLLOWER"
                leader = server
                return leader, term, status
            #count votes received
            elif "vote" in data:
                cpt = cpt + 1
            #else -> iwanttobecandidate -> skip

    #if majory ==> he becomes leader
    if cpt > np.floor(NB_SERVER / 2):
        status = "LEADER"
        leader = RANK
        im_the_leader(RANK)
        print("DEBUG - rank:" + str(RANK) + status+ ", term: "+str(term)+", leader:"+str(leader)+", candidat_loop devient un leader nb_vote:"+str(cpt)+"\n")

    return leader, term, status


# 3 possibilités de recv : heartbeat, imtheleader, iwanttobecandidate
def follower_loop(leader, term, time_out=random.randint(300, 500)):
    '''
        A follower can receive:
        "imtheleader" ==> save who is the leader
        "heartbeat_leader ==> response to the leader (send heartbeat_follower)
        "iwanttobecandidat" ==> a candidat ask him to vote for him, vote for him (if possible)
        a follower votes once per term
    '''
    committed_logs = []
    time_now = now()
    while now() - time_now < time_out:
        server, data, tag = irecv_data()

        if data is not None:

            # log part
            if tag == CHANGES_TO_COMMIT:
                uncommitted_logs = data.tolist()
                send_to_leader(leader, uncommitted_logs)

            elif tag == LEADER_COMMIT:
                committed_logs += data #fix?
                # Write down to disk the log file
                print("tag == LEADER_COMMIT committed_logs:",committed_logs, "committed_logs[0]:",committed_logs[0])
                with open(f"log_server_{RANK}.txt", "w+") as f:
                    f.writelines([f"{line}\n" for line in committed_logs])

            #president election
            else:
                if "heartbeat_leader" in data:
                    #check if heartbeat send by current leader (and not by old leader who dead)
                    if int(server) == leader:
                        heartbeat_follower(leader)
                elif "imtheleader" in data:
                    print("DEBUG - rank:" + str(RANK) + ", term: "+str(term)+", leader:"+str(leader) + ", follower_loop imtheleader server: "+str(server)+"\n")
                    leader = server
                elif "iwanttobecandidate" in data:  # leader == -1: #todo - + si leader est mort check le heartbeat
                    # vote once per term
                    term_candidate = int(data.split('=')[1])
                    if term < term_candidate:
                        vote(server)
                        term += 1
                        print("DEBUG - rank:" + str(RANK) + "term: "+str(term)+"leader:"+str(leader)+"follower_loop a vote"+str(server)+"\n")

            time_now = now()
    return leader, term


# Heartbeat + Leader death
def leader_loop(term, time_heartbeat=random.randint(150, 300)):
    '''
        A leader can receive:
        "heartbeat_follower" ==> we stocked who answered
            if data is empty :
                the leader was dead and resuscitated -> he becomes follower again
            if data is not full (we don't count the leader) :
                one or more servers didn't answer
        data of the clients ==>
            CLIENT_TAG : get data client and send to all server
            FOLLOWER_ACKNOWLEDGE_CHANGES : good receive by followers -> write logs
    '''
    isend_loop_client("imtheleader")

    committed_logs = []
    committed_logs_clients_uid = []
    uncommitted_logs = []
    uncommitted_logs_clients_uid = []
    list_followers_uncommitted_logs_internal = [[]] * NB_SERVER
    have_logs = False

    # while pour eviter les appels recursifs
    while True:
        heartbeat_leader(RANK, term)
        time_now = now()
        data = [0] * NB_SERVER
        while now() - time_now < time_heartbeat:
            server, recv, tag = irecv_data()
            if recv is not None:
                #print("leader_loop rank: ", RANK, " data: ",recv, "from ", server)

                if tag == CLIENT_TAG:
                    client_rank = server
                    # We put the client_uid in uncommitted logs
                    uncommitted_logs += recv.tolist()
                    uncommitted_logs_clients_uid += [client_rank]
                    print(f"Leader received a data from client: {client_rank}")
                    # Send logs to followers
                    isend_loop(RANK, uncommitted_logs, CHANGES_TO_COMMIT)  # check

                    committed_logs += uncommitted_logs
                    uncommitted_logs = []
                    have_logs = True

                elif tag == FOLLOWER_ACKNOWLEDGE_CHANGES:
                    list_followers_uncommitted_logs_internal[server - NB_CLIENT] = recv.tolist()  # recv tableau de uncommited
                    have_logs = True

                elif "heartbeat_follower" in recv:
                    data[server - NB_CLIENT] = 1

        if sum(data) == 0:
            break

        elif len(data) -1 != sum(data):
            print("leader:",RANK,"serveur mort?",data)

        # Logs
        if have_logs:
            max_len = 0
            num_ppl_agreeing = 0

            while num_ppl_agreeing < NB_SERVER / 2:
                max_len += 1

                # We count the num_ppl_agreeing
                num_ppl_agreeing = 0
                for sub_lists in list_followers_uncommitted_logs_internal:
                    if len(sub_lists) >= max_len:
                        num_ppl_agreeing += 1

            max_len -= 1
            # max len logs

            committed_logs += uncommitted_logs[:max_len]
            committed_logs_clients_uid += uncommitted_logs_clients_uid[:max_len]

            uncommitted_logs = uncommitted_logs[max_len:]
            uncommitted_logs_clients_uid = uncommitted_logs_clients_uid[max_len:]

            isend_loop(RANK, committed_logs, LEADER_COMMIT)

            # Write down to disk the log file
            with open(f"log_server_{RANK}.txt", "w+") as f:
                f.writelines([f"{line}\n" for line in committed_logs])

            # Send confirmation of commit to the sending client
            for client_rank in committed_logs_clients_uid:
                comm.isend("commit_confirmation", dest=client_rank)

            have_logs = False

    status = "FOLLOWER"
    return term, status

def time_loop(leader, term, status):
    '''
        A proccess can be: candidat leader or follower
        A candidat and a leader can be a follower in their loop so we use if not else for the follower status
    '''
    if status == "CANDIDAT":
        leader, term, status = candidat_loop(leader, status, term)

    elif status == "LEADER":
        term, status = leader_loop(term)

    if status == "FOLLOWER":
        leader, term = follower_loop(leader, term)

    return leader, term, status
