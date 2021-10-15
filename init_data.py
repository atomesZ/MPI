# ------------------ PREPARE DATA ----------------------

from mpi4py import MPI

comm = MPI.COMM_WORLD
SIZE = comm.Get_size()
RANK = comm.Get_rank()

NB_CLIENT = 0
NB_SERVER = 4

CLIENT_TAG = 10
SERVER_TAG = 11
LEADER_COMMIT = 12
COMMIT_CONFIRMATION = 13
CHANGES_TO_COMMIT = 14
FOLLOWER_ACKNOWLEDGE_CHANGES = 15

if_client = RANK < NB_CLIENT
if_server = RANK >= NB_CLIENT

#BCAST = None