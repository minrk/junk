import time
import os
from concurrent.futures import ProcessPoolExecutor

t = int(os.environ.get('BURN_TIME') or 60)
nprocs = int(os.environ.get('BURN_CPUS') or 8)

start = time.perf_counter()

def burn(t):
    stop = start + t
    while time.perf_counter() < stop:
        pass


print(f"burning {nprocs} cpus for {t} seconds")
pool = ProcessPoolExecutor(nprocs)
list(pool.map(burn, [t] * nprocs))
