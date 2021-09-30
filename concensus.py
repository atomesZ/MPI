from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

# Clients code
if rank == 0: # FIXME find an other way to get clients
    data = np.array([rank], dtype='i')
    comm.Send([data, MPI.INT], dest=1) # FIXME send data to servers
# Servers code
elif rank == 1: # FIXME find an other way to get servers
    data = np.empty(1000, dtype='i')

    lines = []

    # Do a loop or some stuff here to retrieve all clients UIDs
    comm.Recv([data, MPI.INT], source=0) # FIXME get data from clients
    lines.append(str(data[0]))

    # Then servers synchronise and communicate to agree on an order

    # Write down to disk the log file
    with open(f"log_server_{rank}.txt", "w+") as f:
        f.writelines([f"{line}\n" for line in lines])