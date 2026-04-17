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


## 2026-04-08 — O(1) reads and rebuild log on restart complete

## Observation
The server and app were mixed, but here I realized I need a place specifically
to start up, so that I can rebuild the in-memory hash on restart.

### Decision
Refactor the server to server.py, and make some functions more functional.

### Result
- Clearer flow

### Decision

Rebuild the index from the append-only log at startup.

### Tradeoff

- Simple and correct
- Startup time increases with log size

## 2026-04-17 — Change from CSV format to length-prefixed binary log

## Observation
The CSV format will become limiting for compaction and might complicate other features.

## Decision
Switch from csv formatting to 32-bit length prefixed binary log

## Tradeoff
- Harder to debug
- Better performance and better space usage.

### Decision
Create a new module called wal.py and refactor the csv format
