import os


def main():
    n_clients = int(input("Number of clients: "))
    n_servers = int(input("Number of servers: "))

    n_nodes = n_clients + n_servers + 1

    # Generate clients' data to send
    for client_rank in range(n_clients):
        with open(f"client_input_{client_rank}.txt", "w") as f:
            f.write(f"{client_rank}")

    os.system(f"mpiexec --host localhost:{n_nodes} --stdin {n_nodes - 1} -n {n_nodes} python3 main.py {n_clients} {n_servers}")


if __name__ == "__main__":
    main()