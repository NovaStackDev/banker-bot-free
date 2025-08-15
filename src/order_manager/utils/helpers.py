#(Config loader + logging.)
import logging
import sys
from typing import Any, Dict, Optional

try:
    import yaml  # type: ignore
except Exception as e:
    raise RuntimeError("PyYAML is required. Run: pip install -r requirements.txt") from e

# Set up clean console logs.
# %(asctime)s → timestamp.
# %(levelname)s → severity level (INFO, ERROR, etc.).
# %(name)s → module name.
# %(message)s → the actual log text.

def setup_logging(level: int = logging.INFO) -> None:
    logger = logging.getLogger()
    logger.setLevel(level)
    if not logger.handlers:
        h = logging.StreamHandler(sys.stdout)
        fmt = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
        h.setFormatter(fmt)
        logger.addHandler(h)
        
# YAML loader
# Reads a .yaml file from disk and converts it into a Python dict.
# yaml.safe_load() → parses YAML safely (avoids executing arbitrary code, which is possible with the unsafe loader).
# Returns: a dictionary with arbitrary key/value pairs.

def load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# Nested dictionary value getter
# Safely get a deeply nested value from a dictionary without KeyError.
# keys means you can pass multiple keys in sequence.
# If at any point the key path doesn’t exist, it returns the default value.

def get_nested(d: Dict[str, Any], *keys, default: Optional[Any] = None) -> Any:
    cur: Any = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


""" 
Main Value:

setup_logging → consistent logs help debug execution timing, latency, and decision making.

load_yaml → easily load parameters, settings, and balances from a config file.

get_nested → safe lookups mean if a config is missed, workflow won’t instantly crash. 

"""