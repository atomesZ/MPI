import os


def main():
    n_clients = int(input("Number of clients: "))
    n_servers = int(input("Number of servers: "))

    n_nodes = n_clients + n_servers + 1

    os.system(f"mpiexec --host localhost:{n_nodes} --stdin {n_nodes - 1} -n {n_nodes} python3 main.py {n_clients} {n_servers}")


if __name__ == "__main__":
    main()