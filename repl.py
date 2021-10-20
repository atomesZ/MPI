from server_status_loop import *

def start_clients():
    # nothing to parse : send to clients
    isend_loop_client("START")


def speed_process(command: str):
    spl = command.split(" ")
    if len(spl) != 3:
        print("Please SPEED (low, medium, high) $PROCESS")
    else:
        speed = spl[1]
        processus_uid = int(spl[2])
        if processus_uid >= SIZE:
            print("Please enter a good $PROCESS number inferior to", SIZE)
        else:
            if "low" in speed:
                comm.isend("SPEED_LOW", dest=processus_uid, tag=REPL_TAG)
            elif "medium" in speed:
                comm.isend("SPEED_MEDIUM", dest=processus_uid, tag=REPL_TAG)
            elif "high" in speed:
                comm.isend("SPEED_HIGH", dest=processus_uid, tag=REPL_TAG)
            else:
                print("Please enter a good speed term: low, medium or high")


def crash_a_process(command: str):
    spl = command.split(" ")

    if len(spl) != 2:
        print("Please enter CRASH $PROCESS")
    else:
        processus_uid = int(spl[1])
        if processus_uid >= SIZE:
            print("Please enter a good $PROCESS number inferior to", SIZE)
        else:
            comm.isend("CRASH", dest=processus_uid, tag=REPL_TAG)


def recover_a_process(command: str):
    spl = command.split(" ")

    if len(spl) != 2:
        print("Please enter RECOVERY $PROCESS")
    else:
        processus_uid = int(spl[1])
        if processus_uid >= SIZE:
            print("Please enter a good $PROCESS number inferior to", SIZE)
        else:
            comm.isend("RECOVERY", dest=processus_uid, tag=REPL_TAG)

def main_repl():
    while True:
        command = input("Enter a command:\n")

        if "START" in command:
            start_clients()
        elif "SPEED" in command:
            speed_process(command)
        elif "CRASH" in command:
            crash_a_process(command)
        elif "RECOVERY" in command:
            recover_a_process(command)
        else:
            print("Please enter a good command")

''''
def listen_repl():
    data = comm.recv(source=REPL_UID)

    if "SPEED" in data:
        if "LOW" in data:
            pass
        elif "MEDIUM" in data:
            pass
        else: #high
            pass

    elif "CRASH" in data:
        while True:
            data = comm.recv(source=REPL_UID)
            if "RECOVERY" in data:
                break
                # TODO ask leader for summary

    elif "RECOVERY" in data:
        pass  # process vivant

    return data
'''