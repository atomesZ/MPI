# ------------------ PREPARE DATA ----------------------

from mpi4py import MPI
from mpi_main import NB_CLIENT, NB_SERVER
import globals

comm = MPI.COMM_WORLD
SIZE = comm.Get_size()
RANK = comm.Get_rank()

CLIENT_TAG = 10
SERVER_TAG = 11
LEADER_COMMIT = 12
COMMIT_CONFIRMATION = 13
CHANGES_TO_COMMIT = 14
FOLLOWER_ACKNOWLEDGE_CHANGES = 15
REPL_TAG = 16
RECOVERY_TAG = 17

MAX_HEARTBEAT_SKIP = 5
CLIENT_MESSAGE_SIZE = 1  # Hard-coded (the uid of the client)

if_client = RANK < NB_CLIENT
if_server = NB_CLIENT <= RANK < SIZE - 1

REPL_UID = SIZE - 1
