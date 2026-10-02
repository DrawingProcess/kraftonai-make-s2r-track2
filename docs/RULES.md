# Track 2 — Rules

*The rules of submission, scoring and execution for both Track 2 subproblems. The problem statement
(문제 2 · Make Sim to Real) states the same rules; this document gives the detail.*

## 1. What the track is

Track 2 has two subproblems, scored independently. The Problem 2 score is 30% of the 2-1 score plus 70% of the 2-2 score (out of 100); a subproblem you do not enter counts 0.

- **2-1 forward-dynamics calibration.** You are given a simplified simulator and logs from a held-back
  "real" vessel; you submit a simulator that follows the same trajectories under unseen command sequences.
- **2-2 dataset design for closed-loop guide following.** You submit action-labelled driving records; the
  organisers train one fixed policy on them and roll it out behind a moving guide in a held-back
  environment; the score is how well it follows the guide: on the guide's own track, `d_target` behind it.

2-2's held-back environment is the vessel 2-1 asks you to model, so a participant who skipped 2-1 may enter
2-2 but should not expect to score well.

## 2. The held-back environment

The reference is the base simulator with several elements added, held back and frozen for the contest,
with deterministic physics and stochastic sensors. The kit's camera and the reference camera share one
renderer build; its stamp is in `VERSION.txt`, and the kit writes it into every dataset manifest. What
the reference camera adds to the picture, and how the hidden episodes are composed, is withheld: the kit
carries the clean camera and nothing of the gap; the released real-driving episodes show what the reference
camera sees. The clean picture is the studio's (the map's colours, shoreline, shadows, outlines, anti-aliased).
Your own model of what the reference camera adds goes in `closedloop.Env(camera=...)` -- a function on every
frame as it is rendered -- or, the same hook, the studio's camera selector and its `camera.py`.

**A submission must be a genuine attempt at the task. A submission designed to extract information about
the hidden sets or the reference configuration — through error messages, timing, the leaderboard or any
other channel — is disqualifying.** What is allowed and expected: modelling the reference from the
released logs (2-1) and designing data that survives it (2-2).

## 3. Submitting

| | 2-1 | 2-2 |
|---|---|---|
| What | a directory: `manifest.json`, an entry module defining `make_sim(config, seed)`, anything it imports (`docs/PACKAGING.md`) | a directory: `manifest.json`, `method.md`, one `.npz` per episode (`docs/SCHEMA.md`) |
| Budget | none on size; 600 s of one core for the whole hidden set | at most 18,000 decision records in all; each episode file may declare at most 1 GiB uncompressed |
| Quota | 10 submissions per participant per 24 hours | 2 per participant per 24 hours |
| Deadline | 2026-10-29 (Thu) 23:59 KST. No leaderboard freeze; scoring continues after the deadline until the queue is empty | same |
| Counts | your best-scoring submission on the leaderboard set; ties go to the earlier submission. Your final 2-1 score is that submission re-scored on the final set after the deadline (§4) | your best-scoring submission; ties go to the earlier submission. The leaderboard score is already the final score (three training seeds) |
| How to submit | see the common rules page, section '제출과 접수' (Submission) | same |

`manifest.json` of a 2-1 submission gives your participant ID in its `team` field. A byte-identical
resubmission is refused. A submission that fails intake validation is refused with the validator's report
and does not use your quota. Run the bundled validator first (`usvsim validate-submission`,
`usvsim validate-dataset`); it is the same code.

Submissions are scored in arrival order, and the leaderboard is updated each time a scoring finishes.

## 4. How you are scored

**2-1.** Your simulator is replayed open-loop over 60 hidden command sequences per manoeuvre group (six groups:
`straight`, `accel_decel`, `turn`, `scurve`, `brake`, `lowspeed`; 360 replays of 120 s) from rest at the origin,
one command per 0.05 s, state logged at 10 Hz, and compared with the true trajectory — the hidden sets carry no
measurement noise and no current. Per replay, four channels (position 1.0 m, heading 0.2 rad, surge 0.3 m/s,
yaw rate 0.15 rad/s) are normalised, clipped at 3 per sample and averaged; per group,
`skill = clip(1 − E / E_base, 0, 1)` with `E_base` the shipped simulator's own error on the same replays: 100 is
the true trajectory reproduced, 0 no better than the shipped simulator; `S_sim` is 100 × the mean over the six
groups.

There are two hidden sets of command sequences, drawn by the same generator with different seeds, each of 60
replays per group. The **leaderboard set** scores every submission during the contest; its `E_base` per group is
in `data/anchors.json`. The **final set** is used only after the deadline: your best leaderboard submission is
re-scored on it, and that score is your final 2-1 score. The final set has its own `E_base`, computed by the
organisers the same way and published after the deadline.

The released library is 12 replays of 60 s, two per group; its records were made in a weak constant water
current per replay (0.03–0.10 m/s, direction random, the realisation not disclosed) on top of the measurement
noise; the reference's actuator feedback is not released.

**2-2.** Your dataset is validated (format, ranges, budget, duplicates, coverage warnings, and the
comparison against hidden frames — a frame identical to a hidden-set frame is an error), the fixed learner
(the four frames of the window stacked as channels, the newest frame's velocity, yaw rate and `d_target`, a
fixed recipe, no augmentation by the organisers) is trained on your dataset alone, and the policy is rolled out
over the hidden episodes: 90 s each (180 decisions), of equal weight; their conditions include sudden stops and
sharp turns of the guide and static obstacles near its course; their number and make-up are not published. The
guide's own track keeps at least 5.5 m from every static obstacle: buoys, moorings, piers and quays can come to
within 5.5 m of it but not closer, so an ego that follows the guide's track does not hit them. The task is to
follow the guide in its wake: on the water the guide went through, with the guide `d_target` ahead along that
track — or `d_target` away in a straight line, either counts — and up to 2 m to either side of the track
without loss. The track is the guide's path, extended 40 m straight behind its start. Per decision,
`q_t = exp(−½ (e_s / 2 m)²) · exp(−½ (max(0, n − 2 m) / 2 m)²)`, with `e_s` the ego's distance along the track
from the station (zero anywhere between the point `d_target` behind the guide in a straight line and the point
`d_target` behind it along the track) and `n` its distance from the track; the score is 100/180 × Σ q_t. An
episode ends early on guide loss (3 s out of frame), collision or leaving the water, and every remaining
decision scores 0. The learner is trained at three seeds, the same for every participant, and the score is
their mean; the leaderboard score is the final score.

**Disclosure.** During the contest the leaderboard shows the total score only. The 2-1 per-group scores and
final-set scores and the 2-2 per-condition scores are released after the deadline.

## 5. Faults

- 2-1: a non-finite sample is worth the metric's cap; a crash or a timeout is a submission fault — every
  replay at the cap, `S_sim` 0; a non-deterministic simulator is refused without a score (checked by building
  it twice through `make_sim` with two seeds). Files that declare more than the intake caps are refused
  unopened.
- 2-2: a dataset over the budget, outside the format or carrying hidden frames is rejected at intake with
  the report.

## 6. What you may use

- **Your own data.** In 2-2 nothing about how you generate or edit your data is forbidden: any controller,
  any plant, any camera model (`Env(camera=...)` is the place), any editing; only the recorded fields ship.
- **External data and pretrained weights: no restriction, in either subproblem.** In 2-1 a learned component
  is bounded by the runtime (one core, 600 s, the runtime's packages), not by a rule.
- **2-1 timing and delay parameters are legal**; the only requirement is causality, which the `step()`
  interface enforces.
- **2-1 dependencies:** the scoring runtime's packages and the standard library only, CPU only, no network
  (`docs/RUNTIME.md`).

## 7. Execution environment

`docs/RUNTIME.md` lists the interpreter, package versions, hardware and limits: a 2-1 submission runs pinned
to one core under an 8 GB memory ceiling with no network; a 2-2 scoring runs under 24 GB.

Every score is recorded with its scoring environment — the renderer build, the 2-1 and 2-2 hidden sets, the
reference plant, the learner recipe and the score definition. Should the organisers have to change any of it, every score produced under
the earlier environment is shown as *stale* on the leaderboard and re-scored under the new one without using
your quota; new and old scores are never mixed unmarked.

## 8. Not in this document

There is no per-group skill floor in
2-1, and no rule on augmentation in 2-2 beyond §6: what you put in your data is yours to decide.
