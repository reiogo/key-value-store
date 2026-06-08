# Design: Key-Value Store

## Overview
Currently supports `GET`,`PUT`,`DELETE` operations with append-only persistence.

---

## Architecture

### Components

- **TCP Server**
  - Handles single connection
  - Sends responses

- **Storage Engine**
  - Writes to files to store data in bytes.
  - There is an in-memory hash that keeps track of byte offsets

- **Write-Ahead Log (WAL)**
  - Append-only file (length-prefixed binary log) [type][key-size][key][value-size][value][crc32])
  - Stores all write operations
  - Tombstones for deletes
  - CRC32 checksum for detecting partial writes
  - background process for merge and compaction
