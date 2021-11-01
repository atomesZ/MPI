from server_message import *

import time
import numpy as np
import random


# time now
def now():
    return round(time.time() * 1000)


def candidat_loop():
    """
        A candidate can receive:
        "vote" ==> one follower voted for him
        "imtheleader" or "heartbeat_leader ==> an other candidate was elected before him
        "iwanttobecandidat" ==> a candidat ask him to vote for him

    """
    print("--DEBUG CANDIDAT", RANK, "TIME_OUT:", globals.TIME_OUT)
    #print("DEBUG - rank:" + str(rank) + status+ "term: "+str(term)+"leader:"+str(leader)+"candidat_loop START"+"\n")
    time_now = now()
    time_out = random.randint(globals.TIME_OUT[0], globals.TIME_OUT[1])
    # votes counter, init with 1 (vote for himself)
    cpt = 1  # choose counter and not array, we don't know who votes for him
    while now() - time_now < time_out:
        server, data, tag = irecv_data()

        if data is not None:
            #print("candidat_loop - rank", RANK, " data: " , data, " from: ", server)
            # if there is a leader ==> become follower
            if "imtheleader" in data or "heartbeat" in data:  # Si un autre candidat est devenu leader avant lui :sad:
                globals.status = "FOLLOWER"
                globals.leader = server
                return
            # count votes received
            elif "vote" in data:
                cpt = cpt + 1
            # else -> iwanttobecandidate -> skip

    # if majority ==> he becomes leader
    # TODO
    if cpt > np.floor(NB_SERVER / 2):  # NB_SERVER - NB_DEATHS
        globals.status = "LEADER"
        globals.leader = RANK
        im_the_leader()
        #print("DEBUG - rank:" + str(RANK) + status+ ", term: "+str(term)+", leader:"+str(leader)+", candidat_loop devient un leader nb_vote:"+str(cpt)+"\n")


# 3 possibilités de recv : heartbeat, imtheleader, iwanttobecandidate
def follower_loop():
    """
        A follower can receive:
        "imtheleader" ==> save who is the leader
        "heartbeat_leader ==> response to the leader (send heartbeat_follower)
        "iwanttobecandidat" ==> a candidat ask him to vote for him, vote for him (if possible)
        a follower votes once per term
    """
    print("--DEBUG FOLLOWER", RANK, "TIME_OUT:", globals.TIME_OUT)
    uncommitted_logs = []
    cpt_heartbeat_skip = 0
    while cpt_heartbeat_skip < MAX_HEARTBEAT_SKIP:
        time_now = now()
        time_out2 = random.randint(globals.TIME_OUT[0], globals.TIME_OUT[1])
        while now() - time_now < time_out2:
            server, data, tag = irecv_data()

            if data is not None:
                # log part
                if server == globals.leader and tag == CHANGES_TO_COMMIT:
                    uncommitted_logs.append(data)
                    send_to_leader(data)

                elif server == globals.leader and tag == LEADER_COMMIT:
                    globals.committed_logs += data
                    # Write down to disk the log file
                    with open(f"log_server_{RANK}.txt", "a") as f:
                        f.writelines([f"{line}\n" for line in data])

                # president election
                elif "imtheleader" in data:
                    globals.leader = server
                elif "iwanttobecandidate" in data:  # leader == -1: #todo - + si leader est mort check le heartbeat
                    # vote once per term
                    term_candidate = int(data.split('=')[1])
                    if globals.term < term_candidate:
                        vote(server)
                        globals.term += 1
                elif server == globals.leader and "heartbeat_leader" in data:
                    # check if heartbeat send by current leader (and not by an old leader who was dead)
                    heartbeat_follower()
                    cpt_heartbeat_skip = 0

                time_now = now()
                time_out2 = random.randint(globals.TIME_OUT[0], globals.TIME_OUT[1])

        #no heartbeat
        cpt_heartbeat_skip += 1
        #if cpt_heartbeat_skip > 2:
            #print("cpt_heartbeat_skip of",RANK,"=",cpt_heartbeat_skip)


# Heartbeat + Leader death
def leader_loop():
    """
        A leader can receive:
        "heartbeat_follower" ==> we stocked who answered
            if data is empty :
                the leader was dead and resuscitated -> he becomes follower again
            if data is not full (we don't count the leader) :
                one or more servers didn't answer
        data of the clients ==>
            CLIENT_TAG : get data client and send to all server
            FOLLOWER_ACKNOWLEDGE_CHANGES : good receive by followers -> write logs
    """
    print("--DEBUG LEADER_LOOP ", RANK, "TIME_OUT:", globals.TIME_OUT)
    isend_loop_client("imtheleader")

    committed_logs_clients_uid = []
    uncommitted_logs = []
    uncommitted_logs_clients_uid = []
    list_followers_uncommitted_logs_internal = [[]] * NB_SERVER
    have_logs = False

    # while loop to avoid recursive calls
    while True:
        time_now = now()
        time_out = random.randint(globals.TIME_OUT[0], globals.TIME_OUT[1])
        heartbeat_leader()
        data = [0] * NB_SERVER
        while now() - time_now < time_out:
            server, recv, tag = irecv_data()
            if recv is not None:

                if tag == CLIENT_TAG:
                    client_rank = server
                    # We put the client_uid in uncommitted logs
                    uncommitted_logs.append(recv)
                    uncommitted_logs_clients_uid.append(client_rank)
                    # Send logs to followers
                    isend_loop(RANK, uncommitted_logs, CHANGES_TO_COMMIT)  # check

                    have_logs = True

                elif tag == FOLLOWER_ACKNOWLEDGE_CHANGES:
                    list_followers_uncommitted_logs_internal[server - NB_CLIENT].append(recv)  # recv tableau de uncommited
                    have_logs = True

                elif "heartbeat_follower" in recv:
                    data[server - NB_CLIENT] = 1
            elif tag == RECOVERY_TAG:
                comm.isend(globals.committed_logs, dest=server, tag=RECOVERY_TAG)
            elif tag == ASKING_LEADER:
                comm.isend(None, dest=server, tag=ASKING_LEADER)

        # If no one answered the heartbeat, then we are not leader anymore
        if sum(data) == 0:
            globals.status = "FOLLOWER"
            break

        elif len(data) - 1 != sum(data):
            pass
            #print("leader:",RANK,"serveur mort?",data)

        # Logs
        if have_logs:
            max_len = 0
            num_ppl_agreeing = NB_SERVER

            # This code is used to determine in `max_len` the maximum of logs we are able to commit
            while num_ppl_agreeing > NB_SERVER / 2:
                max_len += 1

                # We count the num_ppl_agreeing
                num_ppl_agreeing = 0
                for sub_lists in list_followers_uncommitted_logs_internal:
                    if len(sub_lists) >= max_len:
                        num_ppl_agreeing += 1

            max_len -= 1
            # max len logs

            isend_loop(RANK, uncommitted_logs[:max_len], LEADER_COMMIT)

            # Write down to disk the log file
            with open(f"log_server_{RANK}.txt", "a") as f:
                f.writelines([f"{line}\n" for line in uncommitted_logs[:max_len]])

            # Send confirmation of commit to the sending client
            for client_rank in committed_logs_clients_uid:
                comm.isend(None, dest=client_rank, tag=CLIENT_COMMIT_CONFIRMATION)

            globals.committed_logs += uncommitted_logs[:max_len]
            committed_logs_clients_uid += uncommitted_logs_clients_uid[:max_len]

            uncommitted_logs = uncommitted_logs[max_len:]
            uncommitted_logs_clients_uid = uncommitted_logs_clients_uid[max_len:]

            have_logs = False


def time_loop():
    """
        A proccess can be: candidat leader or follower
        A candidat and a leader can be a follower in their loop so we use if not else for the follower status
    """
    if globals.status == "CANDIDAT":
        candidat_loop()

    elif globals.status == "LEADER":
        leader_loop()

    if globals.status == "FOLLOWER":
        follower_loop()
