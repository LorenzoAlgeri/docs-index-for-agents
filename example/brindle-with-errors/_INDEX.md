# Brindle (with planted errors): documentation index

This copy of the example index has four planted errors. `verify_index.py` must fail on it.

> In brief
> Brindle is a made-up recipe-sharing service used as a demo project. It has a
> Python API with one SQLite file per tenant. Latest state is in the handoff
> note (session 14): export works, backup job not scheduled.

> Start here
> 1. [README.md](README.md): what the project is
> 2. [docs/architecture.md](docs/architecture.md): how one request moves through the system
> 3. [HANDOFF.md](HANDOFF.md): where the last session stopped

## Map

### Overview and setup
| Document | What is inside |
|---|---|
| [README.md](README.md) | Product summary and the invented stack |
| [docs/onboarding.md](docs/onboarding.md) | Install steps and a three-step smoke test |

### Architecture and decisions
| Document | What is inside |
|---|---|
| [docs/architecture.md](docs/architecture.md) | One API process, one SQLite file per tenant, and the trade-off |
| [docs/decisions/0001-images-on-disk.md](docs/decisions/0001-images-on-disk.md) | Accepted decision: images on disk, not in the database |

### Specification and operations
| Document | What is inside |
|---|---|
| [docs/api.md](/srv/brindle/docs/api.md) | Five endpoints and the error format |
| [docs/runbook.md](docs/run-book.md) | Slow export and single-tenant restore procedures |

### Log and history
| Document | What is inside |
|---|---|
| [HANDOFF.md](HANDOFF.md) | Session 14: export works, backup job unscheduled, open image question |
| [Original README](../brindle/README.md) | The correct copy of this project |

## Gaps

- No document describes the backup job; it is only mentioned in the handoff.
- The handoff leaves the image question open, but decision 0001 already answers it.
