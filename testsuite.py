import difflib
import os

client_input_files_dir_name = 'clients_input/'
log_files_dir_name = 'logs_server/'
try:
    client_input_files = os.listdir(client_input_files_dir_name)
    log_files = os.listdir(log_files_dir_name)

    client_input_files = [client_input_files_dir_name + e for e in client_input_files]
    log_files = [log_files_dir_name + e for e in log_files]
except FileNotFoundError:
    log_files = []

errors = []
errors_client = []

if len(log_files) == 0:
    errors = ["There are no logfiles saved.\n"]
else:
    with open(log_files[0]) as f:
        f_text = f.readlines()
        for i in range(1, len(log_files)):
            with open(log_files[i]) as f2:

                f2_text = f2.readlines()
                for line in difflib.unified_diff(f_text, f2_text, fromfile=log_files[0], tofile=log_files[i]):
                    errors.append(line)

    # Check that all client_inputs are in the log_files

    for client_file in client_input_files:
        errors_per_cli = []
        with open(client_file) as f_client:
            f_client_text = f_client.readlines()
            for f_ct in f_client_text:
                if f_ct not in f_text:
                    errors_per_cli.append(f_ct)
        if errors_per_cli:
            errors_client.append((client_file, errors_per_cli))

GREEN = "\033[92m"
RED = "\033[91m"
NC = "\033[0m"

if not errors and not errors_client:
    print(f"\nTESTSUITE: {GREEN}OK{NC}")
else:
    if errors:
        print(f"\nSERVER LOGS ERRORS :")
    for e in errors:
        print(e, end="")
    if errors_client:
        print(f"\nCLIENT ERRORS :")
    for e in errors_client:
        print("\n" + e[0] + ": ")
        for err_text in e[1]:
            print(err_text[:-2] + " ", end="")
    print(f"\n\nTESTSUITE: {RED}KO{NC}")
    exit(1)
