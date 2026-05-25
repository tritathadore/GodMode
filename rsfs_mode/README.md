# rsfs_mode

A reorganization of `godmode` under the **pyraclaw** "Top Layer Orchestration"
methodology. A single orchestrator agent (**iAiA**) presides over a pool of
competing subordinate agents; the winning candidate becomes **The_Truth** and is
handed off to the **ToL** (Top-of-Layer) consumer for refinement,
documentation, analysis, and external dissemination.

> Status: scaffolding only. See `DESIGN.md` for the architecture, and search
> for `TODO(pyraclaw-spec)` for every place that needs to be reconciled with
> the published framework spec.

## Why this lives in `godmode/` for now

The target repository `tritathadore/rsfs_mode` does not yet exist. Once it is
created, this `rsfs_mode/` subtree should be extracted with:

```bash
git subtree split --prefix=rsfs_mode -b rsfs_mode-export
# then push rsfs_mode-export to the new repo's main
```

## Single route to truth

```
              ┌───────────────────┐
   request ──▶│   iAiA (apex)    │────┐
              └───────┬─────────┘    │ fan-out
                      │                ▼
                      │        ┌──────────────────────┐
                      │        │ competing agents   │
                      │        │  (hermes-backed)   │
                      │        └─────────┬──────────┘
                      │         arbiter ◀─┘   scores
                      ▼
              ┌───────────────────┐
              │   The_Truth     │
              └───────┬─────────┘
                      │
                      ▼
              ┌───────────────────┐
              │ ToL dispatcher  │──▶ refine / doc / publish
              └───────────────────┘
```

## Layout

| Path             | Role                                                       |
| ---------------- | ---------------------------------------------------------- |
| `iaia/`          | The singular top-layer orchestrator                        |
| `agents/`        | Competing subordinate agents and their contract            |
| `truth/`         | Arbiter + `The_Truth` data model                           |
| `tol/`           | Handoff to the Top-of-Layer downstream consumer            |
| `hermes_bridge/` | Adapter onto the `hermes-agent` dependency                 |

## Dependency

`rsfs_mode` depends on [`hermes-agent`](https://github.com/tritathadore/hermes-agent).
Until it is published to an index, install editably:

```bash
pip install -e ../hermes-agent
pip install -e .
```
