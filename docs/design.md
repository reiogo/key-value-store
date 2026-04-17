# Design: Key-Value Store

## Overview

This project is a TCP-based key-value store built using an iterative (tracer bullet) approach. The system currently supports basic `GET` and `PUT` operations with append-only persistence.

---

## Architecture

### Components

- **TCP Server**
  - Handles client connections
  - Parses incoming commands
  - Sends responses

- **Storage Engine**
  - Interfaces with persistence layer
  - In-Memory Hash keeps track of byte offsets

- **Write-Ahead Log (WAL)**
  - Append-only file (length-prefixed binary log)
  - Stores all write operations

---

## Data Flow

1. Client sends command over TCP (`PUT key value`)
2. Server parses command
3. Storage layer processes request:
   - Writes to WAL
4. Server sends response to client

---

## Storage Design

- Recreate in-memory hash on restart
- Append-only log (length-prefixed[32-bit] binary log)
- Each operation is recorded as a new line
- No compaction (yet)
- Reads update the hash index

---

## Tradeoffs

### Advantages

- Simple write path (append-only)
- Easy to debug (human-readable format)
- Fast reads with O(1)(amortized) indexing
- persistent storage with in-memory hash

### Limitations

- keys must fit within memory
- File grows indefinitely (no compaction)
- No concurrency control

---

## Future Improvements

- Log compaction
- Snapshot of compressed logs
- Improved command parsing
- Concurrency handling
- Benchmarking

---

## Non-Goals (for now)

- Distributed system
- Strong consistency guarantees
- Complex query support
