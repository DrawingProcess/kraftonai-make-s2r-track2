# Packaging a 2-1 submission (`t2-1-submission/1`)

A contest submission is **one directory**. `usvsim validate-submission` and the other kit tools also accept
a bare `.py` for local work, but a contest submission must be a directory, because its manifest carries your
participant ID.

```
my_submission/
  manifest.json      required
  sim.py             the entry module (any name; named in the manifest)
  method.md          optional, read by the organisers, never by the scorer
  helpers.py, ...    optional: anything the entry imports, beside it
  weights.npz, ...   optional: data the entry loads, relative to its own directory
```

`manifest.json`:

```json
{"format": "t2-1-submission/1", "team": "your participant ID", "entry": "sim.py", "notes": "free text"}
```

- `team` holds your participant ID (the key keeps this name); use the same ID in every submission.
- `entry` is a path inside the directory to a Python file defining `make_sim(config, seed)`
  (README, "What you submit"). Its directory is on `sys.path` when it is loaded, so helper
  modules beside it import by name; load data files relative to `__file__`, never by an absolute path.
- Everything else is yours. There is no size cap on a 2-1 submission, but it runs under the
  constraints in `RUNTIME.md`: one core, 600 s for the whole hidden set, the runtime's packages only,
  no network, an 8 GB memory ceiling, and it must be deterministic.

Check before you submit:

```
usvsim validate-submission my_submission/     # layout, contract, determinism, finiteness, beats the shipped plant
usvsim speed-check my_submission/             # will it finish in time?
usvsim replay-eval my_submission/             # your score on the released logs
```

`examples/submission/` is the parameter-fit example packaged this way.
