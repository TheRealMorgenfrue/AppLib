import sys
from time import sleep

for i in range(10):
    print(f"[{i}] {sys.argv}")  # noqa: T201
    sleep(0.25)
