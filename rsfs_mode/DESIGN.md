# rsfs_mode — Architecture (pyraclaw / Top Layer Orchestration)

> **Spec status:** placeholders. Every `TODO(pyraclaw-spec)` below must be
> reconciled against the published pyraclaw framework once supplied. Do not
> treat the choices here as authoritative.

## 1. Premise

One agent at the apex (**iAiA**) is solely responsible for accepting a request
and returning a deliverable. Everything underneath competes — the orchestrator
does not delegate trust, it harvests candidates and arbitrates.

The pipeline must be a **single route to truth**: exactly one path from
request → candidates → arbiter → `The_Truth` → ToL handoff. No back-channels,
no hidden fallbacks, no side-doors. If a stage cannot produce its artifact
the whole route fails loudly.

## 2. Roles

### 2.1 iAiA — the apex orchestrator (`iaia/orchestrator.py`)

- One process, one identity, one inbox.
- Receives a `Request`.
- Fans out to N subordinate agents via the hermes bridge.
- Awaits candidates (bounded by a deadline).
- Calls the arbiter to select `The_Truth`.
- Hands `The_Truth` to the ToL dispatcher.
- Returns the deliverable to the caller.

The Musk analogy in the brief is taken to mean: iAiA sets direction, sets the
bar, and ships the final artifact — it does not itself produce candidates.

### 2.2 Competing agents (`agents/`)

Every candidate-producing agent implements `agents.base.CompetingAgent`. Each
is scored on four axes drawn from the brief:

| Axis      | Meaning                                                                |
| --------- | ---------------------------------------------------------------------- |
| precision | Quantitative correctness against the request's checkable criteria      |
| speed     | Wall-clock latency to first complete candidate                         |
| accuracy  | Semantic match to the request's intent (rubric-based)                  |
| neatness  | Structural quality of the artifact (format, brevity, no extraneous)    |

`TODO(pyraclaw-spec)`: confirm the weighting function across the four axes.

### 2.3 Arbiter (`truth/arbiter.py`)

Deterministic, stateless. Given a list of `Candidate`, returns the single
`The_Truth`. No ties — ties resolve in the order specified by
`TODO(pyraclaw-spec)`.

### 2.4 ToL dispatcher (`tol/dispatcher.py`)

Receives `The_Truth` and is responsible for downstream:

- **refinement** (polish, normalize)
- **documentation** (write to the persistent record)
- **analysis** (telemetry / scoring archive)
- **external dissemination** (publish to whatever sinks ToL owns)

`TODO(pyraclaw-spec)`: confirm whether ToL is in-process, a separate service,
or a queue. Current placeholder treats it as an injectable interface.

### 2.5 Hermes bridge (`hermes_bridge/`)

The sole adapter onto the `hermes-agent` Python package. Subordinate agents
get their model + tool capabilities through this bridge so that swapping
hermes versions is a one-file change.

## 3. The_Truth contract

See `truth/models.py`. Fields are deliberately small:

```
The_Truth(
    request_id: str,
    payload:    Any,           # the deliverable
    producer:   str,           # which competing agent won
    scores:     dict[str, float],
    sealed_at:  datetime,
)
```

Once sealed, `The_Truth` is immutable. Any refinement happens in ToL and
produces a *new* artifact downstream — the sealed truth is the audit anchor.

## 4. Failure semantics

- Zero candidates returned before deadline → raise, do not fall back.
- Arbiter cannot select → raise.
- ToL handoff fails → `The_Truth` is still considered produced; the dispatcher
  is responsible for its own retry policy. iAiA does not retry ToL.

## 5. What is intentionally NOT here

- No caching layer (would create a second route to truth).
- No "best of fallback" logic (would create a second route to truth).
- No agent self-grading (separation of producer and arbiter).

## 6. Open spec questions

1. `TODO(pyraclaw-spec)` exact scoring function and tie-break ordering.
2. `TODO(pyraclaw-spec)` cardinality of competing agents — fixed pool? dynamic?
3. `TODO(pyraclaw-spec)` ToL transport — in-proc, HTTP, queue, file?
4. `TODO(pyraclaw-spec)` whether iAiA is allowed to re-fan-out on zero
   candidates, or must surface the failure to the caller verbatim.
5. `TODO(pyraclaw-spec)` is `The_Truth` cryptographically sealed? If so, what scheme?
