import time
from concurrent.futures import ProcessPoolExecutor

t = 60
nprocs = 8

start = time.perf_counter()

def burn(t):
    stop = start + t
    while time.perf_counter() < stop:
        pass


print(f"burning {nprocs} cpus for {t} seconds")
pool = ProcessPoolExecutor(nprocs)
list(pool.map(burn, [t] * nprocs))
