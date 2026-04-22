# Key-Value Store

A persistent key-value storage engine built from scratch in Python, without generative AI assistance. Architecture decisions were made independently, informed by *Designing Data-Intensive Applications* (Kleppmann) and hands-on iteration.

Built using a **tracer bullet approach** — a minimal end-to-end implementation cutting through all system layers, refined iteratively based on observed limitations and design tradeoffs.

---

## Architecture

- TCP server using Python's `socket` library with a simple binary protocol (`GET`, `PUT`, `DELETE`)
- In-memory hash index for amortized O(1) reads
- Append-only log with length-prefixed binary encoding
- Background merge and compaction for space reclamation
- Crash recovery via log replay on startup
- Docker-based development environment
- Type-checked with mypy, tested with pytest

---

## Design Philosophy

Rather than designing upfront, I started with a working vertical slice and evolved the system incrementally. Each iteration focuses on improving correctness, performance, and design clarity. Tradeoffs, limitations, and iteration decisions are documented in `docs/`.

---

## Planned Work

- Benchmarking and performance characterization
- Improved concurrency handling
