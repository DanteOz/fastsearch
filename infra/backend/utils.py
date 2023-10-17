import os
import re
from pathlib import Path


def load_env_vars(env_path: str | Path) -> dict:
    env = {}
    with open(env_path, "r") as file:
        for line in file.readlines():
            keys = re.findall("^(\w+)=", line)
            if len(keys) == 0:
                continue
            elif len(keys) == 1:
                key = keys[0]
                env[key] = os.getenv(key)
            else:
                raise RuntimeError(f"Too many environment variable keys found in line: {keys}")
    return env
