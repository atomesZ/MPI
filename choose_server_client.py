import os


def main():
    n_clients = int(input("Number of clients: "))
    n_servers = int(input("Number of servers: "))

    os.system(f"mpiexec -n {n_clients + n_servers} python3 main.py {n_clients} {n_servers}")


if __name__ == "__main__":
    main()
