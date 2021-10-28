import os
import random
import numpy as np
import string


def generate_random_data(nbr_clients: int) -> list:
    """
    This function generate the random data for the clients to send
    :param nbr_clients:
    :return: data for the clients
    """
    lengths = random.choices(range(10, 30), k=nbr_clients * 3)
    S = []
    for length in lengths:
        S.append(''.join(random.sample(string.ascii_letters, k=length)))
    S = list(set(S))
    list_separators_for_clients = np.sort(random.sample(range(1, len(lengths)), nbr_clients - 1))
    res = [S[:list_separators_for_clients[0]], S[list_separators_for_clients[len(list_separators_for_clients) - 1]:]]
    prev_sep = list_separators_for_clients[0]
    for i, sep in enumerate(list_separators_for_clients):
        if i == 0:
            continue
        res.append(S[prev_sep:sep])
        prev_sep = sep
    return res


def main():
    n_clients = int(input("Number of clients: "))
    n_servers = int(input("Number of servers: "))

    n_nodes = n_clients + n_servers + 1

    # Generate clients' data to send
    clients_data = generate_random_data(n_clients)
    for client_rank in range(n_clients):
        with open(f"client_input_{client_rank}.txt", "w") as f:
            f.writelines("%s\n" % l for l in clients_data[client_rank])

    os.system(f"mpiexec --host localhost:{n_nodes} "
              f"--stdin {n_nodes - 1} "
              f"-n {n_nodes} "
              f"python3 mpi_main.py {n_clients} {n_servers}")


if __name__ == "__main__":
    main()
