"""childK common: identical M/B/T/P builder as childI (childF definitions)."""
import sys, os, importlib.util
_spec = importlib.util.spec_from_file_location(
    "childI_common",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "childI", "common.py"))
_ci = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ci)
g6_to_adj, build, perron_h, geng = _ci.g6_to_adj, _ci.build, _ci.perron_h, _ci.geng
import numpy as np


def resolvent_check(bd, alpha):
    """R(alpha): (1-alpha)(I-alpha P)^{-1} d <= d. Returns max violation."""
    P = bd["B"] / bd["T"][:, None]
    n = bd["n"]
    d = bd["d"]
    h = np.linalg.solve(np.eye(n) - alpha * P, d)
    return np.max((1 - alpha) * h - d)
