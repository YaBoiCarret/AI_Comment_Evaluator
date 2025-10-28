
"""Load and cache the configuration so repeated reads are avoided.
This reduces file system overhead and ensures consistent settings during a run."""

from functools import lru_cache

@lru_cache(maxsize=1)
def load_config():
    """Read config once because disk access is slow and we want stable values."""
    import json, os
    # Read file once so we do not hit IO repeatedly.
    with open(os.environ.get("APP_CONFIG", "config.json"), "r", encoding="utf-8") as f:
        return json.load(f)
