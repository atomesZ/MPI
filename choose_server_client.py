import os


def main():
    n_clients = int(input("Number of clients: "))
    n_servers = int(input("Number of servers: "))

    n_nodes = n_clients + n_servers
    os.system(f"mpiexec --stdin {n_nodes} -n {n_nodes + 1} python3 main.py {n_clients} {n_servers}")


if __name__ == "__main__":
    main()
