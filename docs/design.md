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
  - Tombstones for deletes
  - CRC32 checksum for detecting partial writes

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
- Append-only log (length-prefixed binary log: 
                   [type][key-size][key][value-size][value][crc32])
- No compaction (yet)

---

## Tradeoffs

### Advantages

- Simple write path (append-only)
- Fast reads with O(1)(amortized) indexing
- persistent storage with in-memory hash

### Limitations

- Keys must fit within memory
- Sequential reads are not efficient
- File grows indefinitely (no compaction)
- No concurrency control

---

## Future Improvements

- Log compaction
- Hint files of merged logs
- Concurrency handling
- Benchmarking

---

