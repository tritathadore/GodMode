# rsfs_mode — Architecture (pyraclaw / Top Layer Orchestration)

## 1. Premise

One agent at the apex (**iAiA**) is solely responsible for accepting a request
and returning a deliverable. Everything underneath competes — the orchestrator
does not delegate trust, it harvests candidates and arbitrates.

The pipeline must be a **single route to truth**: exactly one path from
request → candidates → arbiter → `The_Truth` → ToL handoff. No back-channels,
no hidden fallbacks, no side-doors. If a stage cannot produce its artifact
the whole route fails loudly (after bounded re-fan-out, see §4).

## 2. Roles

### 2.1 iAiA — the apex orchestrator (`iaia/orchestrator.py`)

- One process, one identity, one inbox.
- Receives a `Request`.
- Fans out to N subordinate agents via the hermes bridge.
- Awaits candidates (bounded by `deadline_seconds`).
- On zero candidates, re-fans-out up to `max_refans` times (default 2).
- Calls the arbiter to select a winner.
- Seals `The_Truth` (HMAC-SHA256, see §3).
- Hands `The_Truth` to the ToL dispatcher.
- Returns the deliverable to the caller.

The Musk analogy in the brief is taken to mean: iAiA sets direction, sets the
bar, and ships the final artifact — it does not itself produce candidates.

### 2.2 Competing agents (`agents/`)

Every candidate-producing agent implements `agents.base.CompetingAgent`. Each
is scored on four axes drawn from the brief:

| Axis      | Weight | Meaning                                                             |
| --------- | ------ | ------------------------------------------------------------------- |
| precision | 0.40   | Quantitative correctness against the request's checkable criteria   |
| accuracy  | 0.30   | Semantic match to the request's intent (rubric-based)               |
| speed     | 0.15   | Wall-clock latency to first complete candidate                      |
| neatness  | 0.15   | Structural quality of the artifact (format, brevity, no extraneous) |

### 2.3 Arbiter (`truth/arbiter.py`)

Deterministic, stateless. Given a list of `Candidate`, returns the single
winner. Ties resolve by **fan-out arrival order**: the earliest-submitted
candidate wins (Python's stable sort preserves input order for equal keys).

### 2.4 ToL dispatcher (`tol/dispatcher.py`)

Receives `The_Truth` and is responsible for downstream:

- **refinement** (polish, normalize)
- **documentation** (write to the persistent record)
- **analysis** (telemetry / scoring archive)
- **external dissemination** (publish to whatever sinks ToL owns)

**Transport: in-process function call.** ToL is a Python object injected into
iAiA. Real sinks compose via `FanOutToL`.

### 2.5 Hermes bridge (`hermes_bridge/`)

The sole adapter onto the `hermes-agent` package. **Transport: subprocess
fork of `run_agent.py` per invocation** — no shared in-process state, which
preserves the no-shared-cache rule. Configure via `RSFS_HERMES_RUN_AGENT`
env var or the `script_path` field on `HermesClient`.

## 3. The_Truth contract

See `truth/models.py`. Fields:

```
The_Truth(
    request_id: str,
    payload:    Any,
    producer:   str,
    scores:     Mapping[str, float],
    sealed_at:  datetime,
    signature:  str,           # HMAC-SHA256, hex
)
```

Seal is HMAC-SHA256 over a canonical JSON form of every field except
`signature`. The key comes from the `RSFS_TRUTH_KEY` env var; `seal()`
refuses to run if it is missing. `verify(truth)` returns bool.

Once sealed, `The_Truth` is immutable. Any refinement happens in ToL and
produces a *new* artifact downstream — the sealed truth is the audit anchor.

## 4. Failure semantics

- Zero candidates in a fan-out round → retry up to `max_refans` (default 2);
  after that, raise. No silent fallback.
- Arbiter cannot select → raise.
- ToL handoff fails → `The_Truth` is still considered produced; the dispatcher
  is responsible for its own retry policy. iAiA does not retry ToL.
- `FanOutToL` runs every sink even if one fails, then raises an
  `ExceptionGroup` so partial dispatches are never silent.

## 5. What is intentionally NOT here

- No caching layer (would create a second route to truth).
- No "best of fallback" logic (would create a second route to truth).
- No agent self-grading (separation of producer and arbiter).

## 6. Open spec questions

1. Cardinality of competing agents — fixed pool? dynamic discovery? Currently
   the orchestrator accepts an arbitrary `Sequence[CompetingAgent]` at
   construction time.
2. Seal-scheme strength — HMAC-SHA256 with a shared secret is the current
   answer. If non-repudiation across organizations is required, this should
   move to an asymmetric signature (Ed25519). Flag if/when needed.
