"""Loading a submission and checking it is deterministic.

The same code the contest scorer runs, shipped so that "it passed locally" means the same
thing as "it will be accepted". Determinism is not a formality: your score is computed
once, so if your simulator has any randomness in it, your score is a coin flip and the
scorer refuses it rather than picking one of the two answers.

The check builds your simulator twice through `make_sim` with two different `seed` values
rather than replaying one instance twice, because the likeliest way randomness gets in is
at construction -- a coefficient perturbed at setup, a dropout left enabled in a learned
residual -- and replaying a single instance would never see it.
"""
import importlib.util
import os
import sys

import numpy as np

from usvsim import data


SUBMISSION_FORMAT = 't2-1-submission/1'


def resolve(path):
    """A submission is a `t2-1-submission/1` directory (PACKAGING.md) or, for local use, a bare
    `.py`. Returns `(entry_module_path, manifest_or_None)`; raises ValueError on a bad layout."""
    import json
    if os.path.isdir(path):
        mpath = os.path.join(path, 'manifest.json')
        if not os.path.exists(mpath):
            raise ValueError(f"{path}: manifest.json missing (PACKAGING.md)")
        man = json.load(open(mpath))
        if man.get('format') != SUBMISSION_FORMAT:
            raise ValueError(f"{path}: format is {man.get('format')!r}, expected {SUBMISSION_FORMAT!r}")
        for key in ('team', 'entry'):
            if not isinstance(man.get(key), str) or not man[key].strip():
                raise ValueError(f"{path}: manifest.json needs a non-empty {key!r}")
        entry = os.path.normpath(os.path.join(path, man['entry']))
        if not entry.startswith(os.path.abspath(path) + os.sep) and not entry.startswith(path.rstrip('/') + os.sep):
            raise ValueError(f"{path}: entry {man['entry']!r} points outside the submission")
        if not os.path.isfile(entry) or not entry.endswith('.py'):
            raise ValueError(f"{path}: entry {man['entry']!r} is not a Python file in the submission")
        return entry, man
    if os.path.isfile(path) and path.endswith('.py'):
        return path, None
    raise ValueError(f"{path}: neither a submission directory nor a .py file")


def load(path, name=None):
    path, _ = resolve(path)
    d = os.path.dirname(os.path.abspath(path))
    if d not in sys.path:                      # helper modules beside the entry import by name
        sys.path.insert(0, d)
    name = name or f"_submission_{abs(hash(os.path.abspath(path)))}"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"not an importable Python module: {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    if not hasattr(mod, 'make_sim'):
        raise ValueError(f"{path} defines no make_sim(config, seed)")
    return mod


def _finite(a):
    return np.nan_to_num(a, nan=0.0, posinf=1e300, neginf=-1e300)


def check_determinism(mod, lset, limit=6, config=None):
    """None if deterministic, else a message. `limit` caps how many replays are used."""
    small = data.LogSet(lset.names[:limit], lset.groups[:limit],
                        lset.commands[:limit], lset.states[:limit])
    with np.errstate(invalid='ignore'):
        a = _finite(data.replay(mod, small, config, seed=0))
        b = _finite(data.replay(mod, small, config, seed=1))
        if np.array_equal(a, b):
            return None
        d = float(np.abs(a - b).max())
    return (f"output changed between two runs (largest difference {d:.3e}). Your "
            f"simulator must be deterministic and must ignore `seed`")
