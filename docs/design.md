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

- **Write-Ahead Log (WAL)**
  - Append-only file (CSV format)
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

- Append-only log (CSV format)
- Each operation is recorded as a new line
- No compaction (yet)
- Reads update the hash index

---

## Tradeoffs

### Advantages

- Simple write path (append-only)
- Easy to debug (human-readable format)
- Fast reads with O(1)(amortized) indexing

### Limitations

- The in-memory hash is lost on each restart
- File grows indefinitely (no compaction)
- No concurrency control

---

## Future Improvements

- Rebuild in-memory hash from log
- Log compaction
- Improved command parsing
- Concurrency handling

---

## Non-Goals (for now)

- Distributed system
- Strong consistency guarantees
- Complex query support
