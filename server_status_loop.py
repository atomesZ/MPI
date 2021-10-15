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
        server, data = irecv_data()

        if data is not None:
            print("candidat_loop - rank", RANK, " data: " , data, " from: ", server)
            #if there is a leader ==> become follower
            if "imtheleader" in data or "heartbeat" in data:  # Si un autre candidat est devenu leader avant lui :sad:
                status = "FOLLOWER"
                leader = server
                return leader, term, status
            #count votes received
            elif "vote" in data:
                cpt = cpt + 1          #else -> iwanttobecandidate -> skip

    #if majory ==> he becomes leader
    if cpt > np.floor(NB_SERVER / 2):
        status = "LEADER"
        leader = RANK
        im_the_leader(RANK)
        print("DEBUG - rank:" + str(RANK) + status+ ", term: "+str(term)+", leader:"+str(leader)+", candidat_loop devient un leader nb_vote:"+str(cpt)+"\n")

    return leader, term, status


# 3 possibilités de recv : heartbeat, imtheleader, iwanttobecandidate
def follower_loop(leader, term, time_out = random.randint(300,500)):
    '''
        A follower can receive:
        "imtheleader" ==> save who is the leader
        "heartbeat_leader ==> response to the leader (send heartbeat_follower)
        "iwanttobecandidat" ==> a candidat ask him to vote for him, vote for him (if possible)
        a follower votes once per term
    '''
    time_now = now()
    while now() - time_now < time_out:
        server, data = irecv_data()

        #if BCAST is not None : # fonctionne pas :cry:
        #    print("BCAST :",BCAST," rank:",RANK)

        if data is not None:
            print("follower_loop - rank: ", RANK, " data: ",data, "from ", server)

            if "heartbeat_leader" in data:
                #check if heartbeat send by current leader (and not by old leader who dead)
                if int(server) == leader:
                    heartbeat_follower(leader)
            if "imtheleader" in data:
                print("DEBUG - rank:" + str(RANK) + ", term: "+str(term)+", leader:"+str(leader) + ", follower_loop imtheleader server: "+str(server)+"\n")
                leader = server
            if "iwanttobecandidate" in data:  # leader == -1: #todo - + si leader est mort check le heartbeat
                # vote once per term
                term_candidate = int(data.split('=')[1])
                if term < term_candidate:
                    vote(server)
                    term += 1
                    print("DEBUG - rank:" + str(RANK) + "term: "+str(term)+"leader:"+str(leader)+"follower_loop a vote"+str(server)+"\n")

            #else:
                # donnée client, tout va bene : truc de sego & etienne?
                #data = comm.recv(dest=leader, tag=SERVER_TAG)
                #comm.isend(data, dest=leader, tag=SERVER_TAG)

            time_now = now()
    return leader, term



# Heartbeat + Leader death
def leader_loop(term, time_heartbeat = random.randint(150,300)):
    '''
        A leader can receive:
        "heartbeat_follower" ==> we stocked who answered
            if data is empty :
                the leader was dead and resuscitated -> he becomes follower again
            if data is not full (we don't count the leader) :
                one or more servers didn't answer
        data of the clients ==> TODO
    '''
    heartbeat_leader(RANK, term)
    time_now = now()
    data = [0] * NB_SERVER
    while now() - time_now < time_heartbeat:
        server, recv = irecv_data()
        if server is not None:
            print("leader_loop rank: ", RANK, " data: ",recv, "from ", server)
        if recv is not None and recv == "heartbeat_follower":
            data[server - NB_CLIENT] = 1
        #TODO : else #data client return
    if sum(data) == 0:
        status = "FOLLOWER"
        return term, status
    elif len(data) -1 != sum(data):
        print("leader:",RANK,"serveur mort?",data)
    return leader_loop(term)


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