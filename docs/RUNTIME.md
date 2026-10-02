# Scoring runtime

Everything below is what your submission is run with, or run by. Each scoring PC scores one submission at a
time.

## Interpreter and packages

| | version |
|---|---|
| Python | 3.10.12 (Ubuntu 22.04.5, Linux 6.8.0-138-generic) |
| numpy | 1.21.5 |
| scipy | 1.8.0 |
| pillow | 12.1.0 |
| torch | 2.8.0+cu128 (CUDA 12.8), with torchvision 0.23.0+cu128 — the organisers' 2-2 trainer; the kit's `usvsim.guide.learner` needs torch only. A 2-1 submission gets neither |

**2-1 submissions may import only numpy, scipy, pillow and the Python standard library.**
No compiled extensions of your own, no packages installed at scoring time, no network. Scoring runs
numpy 1.21.5; develop and test against that version.

## Hardware

| | |
|---|---|
| CPU | Intel Core i7-14700, 28 logical cores; a 2-1 submission is pinned to **one** |
| RAM | 30 GB; a 2-1 submission runs under an **8 GB** ceiling, a 2-2 scoring under **24 GB** |
| GPU | NVIDIA GeForce RTX 5060 (8 GB); used only by the organisers' 2-2 trainer |

## What a 2-1 submission runs under

- a child process pinned to one core, with only the kit on its path (it cannot import the
  reference plant);
- **600 s of wall clock for the whole hidden-set replay** (360 replays of 120 s). The shipped plant needs
  about 1/50 of that; `usvsim speed-check` extrapolates yours;
- CPU only, no network (an unprivileged network namespace), an 8 GB memory ceiling;
- **a timeout or a crash is a submission fault**: every replay is worth the metric's cap and the
  score is 0. There is no partial credit for the replays that finished;
- the determinism check first (`usvsim/submission.py`): built twice through `make_sim` with two
  seeds, replayed over six sequences, refused if the outputs differ.

## What a 2-2 submission runs under

You submit data, not code. Intake validates the directory (`usvsim validate-dataset` shows you what,
minus the hidden-frame comparison), the fixed learner is trained on it (30 epochs, three seeds,
the same for every participant; the score is their mean, and the leaderboard score is the final score),
and each policy is rolled out on the hidden set. A scoring takes about 30 minutes (measured on the previous
scoring hardware; to be re-measured on the scoring PCs).
