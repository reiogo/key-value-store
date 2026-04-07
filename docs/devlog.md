## 2026-04-07 — Tracer Bullet Complete

### Goal
Build end-to-end flow: TCP -> parse -> process(store/retrieve) -> respond

### What I built
- TCP server using sockets
- Simple text protocol (GET/PUT)
- Append-only CSV log

### Observations
- Writes are simple and reliable
- Reads require scanning entire file → O(n)

### Next steps
- Introduce an in-memory index mapping keys to file offsets.

### Tradeoff

- Improved read performance to O(1)
- Increased memory usage
- Added complexity in maintaining index consistency

### Observation

The in-memory index enables O(1) reads but is lost on restart.
The shift to indexing means that the scanning read is no longer supported

### Decision

Rebuild the index from the append-only log at startup.

### Tradeoff

- Simple and correct
- Startup time increases with log size
