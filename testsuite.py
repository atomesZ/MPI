import difflib
import os
import re

r = re.compile("log_server_\d*\.txt")

log_files = os.listdir()

log_files = list(filter(r.match, log_files))

errors = []

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

GREEN = "\033[92m"
RED = "\033[91m"
NC = "\033[0m"

if not errors:
    print(f"\nTESTSUITE: {GREEN}OK{NC}")
else:
    for e in errors:
        print(e, end="")
    print(f"\nTESTSUITE: {RED}KO{NC}")
    exit(1)
