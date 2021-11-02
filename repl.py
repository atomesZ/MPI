import globals
from server_status_loop import *

def start_clients():
    # nothing to parse : send to clients
    isend_loop_client("START")


def speed_process(command: str):
    spl = command.split(" ")
    if len(spl) != 3:
        print("Please SPEED (LOW, MEDIUM, HIGH) $PROCESS")
    else:
        speed = spl[1]
        processus_uid = int(spl[2])
        if processus_uid >= SIZE:
            print("Please enter a good $PROCESS number inferior to", SIZE)
        else:
            if "LOW" in speed:
                comm.isend("SPEED_LOW", dest=processus_uid, tag=REPL_TAG)
            elif "MEDIUM" in speed:
                comm.isend("SPEED_MEDIUM", dest=processus_uid, tag=REPL_TAG)
            elif "HIGH" in speed:
                comm.isend("SPEED_HIGH", dest=processus_uid, tag=REPL_TAG)
            else:
                print("Please enter a good speed term: LOW, MEDIUM or HIGH")


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


def end_all_nodes():
    for processus_uid in range(NB_CLIENT + NB_SERVER):
        comm.isend("END", dest=processus_uid, tag=REPL_TAG)
    exit(0)


def main_repl():
    while True:
        try:
            command = input("Enter a command:\n")
        except EOFError:
            print(" To exit program, it is better to use the REPL's command: END instead of Ctrl+C")
            exit(0)

        if "START" in command:
            start_clients()
        elif "SPEED" in command:
            speed_process(command)
        elif "CRASH" in command:
            crash_a_process(command)
        elif "RECOVERY" in command:
            recover_a_process(command)
        elif "END" in command:
            end_all_nodes()
        else:
            print("Please enter a good command")