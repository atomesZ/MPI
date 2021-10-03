from mpi4py import MPI
import numpy as np
import sys

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

num_clients = int(sys.argv[1])
num_servers = int(sys.argv[2])

is_client = rank < num_clients
is_server = not is_client and rank < num_clients + num_servers

# TODO remove this implem later
is_client = rank == 0
is_server = rank == 1


# TODO : implement RAFT algorithm

# Clients code
if is_client:  # FIXME find an other way to get clients
    data = np.array([rank], dtype='i')
    comm.Send([data, MPI.INT], dest=1)  # FIXME send data to servers
# Servers code
elif is_server:  # FIXME find an other way to get servers
    data = np.empty(1000, dtype='i')

    lines = []

    # Do a loop or some stuff here to retrieve all clients UIDs
    comm.Recv([data, MPI.INT], source=0)  # FIXME get data from clients
    lines.append(str(data[0]))

    # Then servers synchronise and communicate to agree on an order

    # Write down to disk the log file
    with open(f"log_server_{rank}.txt", "w+") as f:
        f.writelines([f"{line}\n" for line in lines])
"""else:
    print("/!\\ Wait, this node is not a client nor a server /!\\")
    print(f"rank: {rank}")
    print(f"num nodes: {num_clients + num_servers}")
    print(f"num_clients: {num_clients}")
    print(f"num_servers: {num_servers}")"""
