import time
import sys

start = time.perf_counter()
# run for 30 minutes
time_limit = 30 * 60
elapsed = 0
last_dot = -10
while elapsed < time_limit:
    elapsed = time.perf_counter() - start
    if elapsed - last_dot >= 2:
        sys.stdout.write(".")
        sys.stdout.flush()
        last_dot = elapsed

sys.exit(1)
