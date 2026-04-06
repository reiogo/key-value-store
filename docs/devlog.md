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
- Introduce in-memory index
- Separate protocol handling from storage layer
