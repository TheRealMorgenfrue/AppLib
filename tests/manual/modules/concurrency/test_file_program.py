import sys
from time import sleep

for i in range(10):
    print(f"[{i}] {sys.argv}")
    sleep(0.25)
