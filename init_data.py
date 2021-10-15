# ------------------ PREPARE DATA ----------------------

from mpi4py import MPI

comm = MPI.COMM_WORLD
SIZE = comm.Get_size()
RANK = comm.Get_rank()

NB_CLIENT = 0
NB_SERVER = 4

if_client = RANK < NB_CLIENT
if_server = RANK >= NB_CLIENT

SERVER_TAG = 11
CLIENT_TAG = 12

#BCAST = None