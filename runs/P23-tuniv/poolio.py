"""Shared loader for the self-contained tuniv pool."""
import os
import pickle

POOL = os.environ.get("POOL", os.path.join(os.path.dirname(__file__), "pool.pkl"))


def load_all(path=POOL):
    with open(path, "rb") as f:
        rec = pickle.load(f)
    points = rec[0] if isinstance(rec, tuple) else rec
    return [v for tag, v in points if tag == "A"]
