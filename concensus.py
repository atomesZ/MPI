from mpi4py import MPI
import numpy as np
import sys

CLIENT_TAG = 10
SERVER_TAG = 11
LEADER_COMMIT = 12
COMMIT_CONFIRMATION = 13
CHANGES_TO_COMMIT = 14
FOLLOWER_ACKNOWLEDGE_CHANGES = 15

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

num_clients = int(sys.argv[1])
num_servers = int(sys.argv[2])

num_nodes = num_clients + num_servers

is_client = rank < num_clients
is_server = not is_client and rank < num_clients + num_servers

# TODO : implement RAFT algorithm

leader_uid = num_clients  # FIXME leader election

# Clients code
if is_client:
    data = np.array([rank], dtype='i')
    comm.Send([data, MPI.INT], dest=leader_uid, tag=CLIENT_TAG)

    print("Client sent data.")
# Servers code
elif is_server:
    buffer = np.empty(1000, dtype='i')

    committed_logs = []

    # if I am the leader
    if rank == leader_uid:
        print(f"Leader is {rank}")
        uncommitted_logs = []

        while len(committed_logs) < num_clients:  # Sleep at the end for a heartbeat
            # A client sends its message to the leader
            comm.Recv([buffer, MPI.INT], source=MPI.ANY_SOURCE, tag=CLIENT_TAG)
            client_uid = buffer[0]  # FIXME use status

            # We put the client_uid in uncommitted logs
            uncommitted_logs.append(client_uid)
            print(f"Leader received a data from client: {client_uid}")

            # Send logs to followers
            if uncommitted_logs:
                print("Leader entered uncommitted logs")
                # TODO broadcast the uncommitted logs to the followers
                for server_uid in range(num_clients, num_nodes):
                    if server_uid == leader_uid:
                        continue
                    comm.Send([np.array([len(uncommitted_logs)] + uncommitted_logs, dtype="i"), MPI.INT], dest=server_uid, tag=CHANGES_TO_COMMIT)

                list_servers_acknowledging_logs: list = []
                # Wait for a majority of responses
                while len(list_servers_acknowledging_logs) < num_servers / 2:
                    comm.Recv([buffer, MPI.INT], source=MPI.ANY_SOURCE, tag=FOLLOWER_ACKNOWLEDGE_CHANGES)

                    uid_of_server_acknowledging: int = buffer[0]
                    if uid_of_server_acknowledging not in list_servers_acknowledging_logs:
                        list_servers_acknowledging_logs.append(uid_of_server_acknowledging)

                # Commit logs
                committed_logs += uncommitted_logs
                uncommitted_logs = []

                # Send confirmation of commit to the servers
                for server_uid in range(num_clients, num_nodes):
                    if server_uid == leader_uid:
                        continue
                    comm.Send([None, MPI.INT], dest=server_uid, tag=LEADER_COMMIT)

                # Write down to disk the log file
                with open(f"log_server_{rank}.txt", "w+") as f:
                    f.writelines([f"{line}\n" for line in committed_logs])

                # Send confirmation of commit to the sending client
                comm.Send([None, MPI.INT], dest=committed_logs[-1], tag=COMMIT_CONFIRMATION)


    else:  # Follower's code
        while len(committed_logs) < num_clients:
            # Wait for the changes to commit
            comm.Recv([buffer, MPI.INT], source=leader_uid, tag=CHANGES_TO_COMMIT)
            print(f"Server {rank} received data from Leader")

            len_uncommitted_logs = buffer[0]
            uncommitted_logs = buffer[1:len_uncommitted_logs+1].tolist()

            buffer[0] = rank
            comm.Send([buffer, MPI.INT], dest=leader_uid, tag=FOLLOWER_ACKNOWLEDGE_CHANGES)
            print(f"Server {rank} sent acknowledgement")

            # Wait for the leader to confirm the commit
            comm.Recv([None, MPI.INT], source=leader_uid, tag=LEADER_COMMIT)
            committed_logs += uncommitted_logs

            num_received_client = len(committed_logs)

            # Write down to disk the log file
            with open(f"log_server_{rank}.txt", "w+") as f:
                f.writelines([f"{line}\n" for line in committed_logs])
else:
    print("/!\\ Wait, this node is not a client nor a server /!\\")
    print(f"rank: {rank}")
    print(f"num nodes: {num_clients + num_servers}")
    print(f"num_clients: {num_clients}")
    print(f"num_servers: {num_servers}")
