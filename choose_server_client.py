import os
import random
import string


def main():
    n_clients = int(input("Number of clients: "))
    n_servers = int(input("Number of servers: "))

    n_nodes = n_clients + n_servers + 1

    # Generate clients' data to send
    for client_rank in range(n_clients):
        with open(f"client_input_{client_rank}.txt", "w") as f:

            length = random.randint(10, 30)
            result = ''.join((random.choice(string.ascii_letters) for x in range(length)))

            f.write(result)

    os.system(f"mpiexec --host localhost:{n_nodes} "
              f"--stdin {n_nodes - 1} "
              f"-n {n_nodes} "
              f"python3 main.py {n_clients} {n_servers}")


if __name__ == "__main__":
    main()
