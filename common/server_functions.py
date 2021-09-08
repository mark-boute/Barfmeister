import os
import asyncio
import csv

from common.bois_functions import reply_and_delete

# or https://docs.python.org/3/library/subprocess.html


def system_call(cmd: str):
    os.system(cmd)


async def get_by_status(lock: asyncio.Lock, running: bool = True):
    status_list = list()
    with await lock:
        with open("server_status.csv", "r", newline="\n") as f:
            for name, status, since in csv.reader(f):
                if bool(int(status)) == running:
                    status_list.append((name, since))
    return status_list


async def get_configs(lock: asyncio.Lock):
    configs = list()
    with await lock:
        with open("configs.csv", "r", newline="\n") as f:
            for name, server_dir in csv.reader(f):
                configs.append((name, server_dir))

    return configs


async def remove_config(lock: asyncio.Lock, name):
    with await lock:
        with open("configs.csv", "r", newline="\n") as file:
            configs = [(n, d) for n, d in csv.reader(file) if n != name]

        with open("configs.csv", "w", newline="\n") as file:
            for n, d in configs:
                file.write(f"{n},{d}\n")

    return configs


async def add_config(lock: asyncio.Lock, name, server_dir):
    with await lock:
        with open("configs.csv", "r", newline="\n") as file:
            for n, d in csv.reader(file):
                if n == name or d == server_dir:
                    return False
        with open("configs.csv", "a", newline="\n") as file:
            file.write(f"{name},{server_dir}\n")
        return True


async def find_dir(server_dir):
    # check if dir exists
    # find needed files
    return False


async def check_config_availability(ctx, configs, name, server_dir):
    for n, d in configs:
        if n == name:
            await reply_and_delete(ctx, f"Name {n} is already in use for {d}")
            return False
        if d == server_dir:
            await reply_and_delete(ctx, f"Directory {d} is already in use by {n}")
            return False
    return True
