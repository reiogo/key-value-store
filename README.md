# Key-Value Store

A key-value store is a simple data storage system where a key acts as an identifier and a value is the associated data.

This project is built using a **tracer bullet approach**—a minimal end-to-end implementation that cuts through all layers of the system, followed by iterative refinement based on observed limitations and system design principles.

---

## Current System

- TCP server using Python sockets  
- Simple text protocol (`GET`, `PUT`)  
- In-Memory Hash
- Append-only log (length-prefixed binary log)  
- Docker-based development environment  

---

## Philosophy

Rather than designing upfront, I started with a working vertical slice and am evolving the system incrementally. Each iteration focuses on improving correctness, performance, and system design.

---

## Documentation

The `docs/` directory contains design notes and a development log documenting tradeoffs, limitations, and iteration decisions.

---

## Stack

- Python (pytest, mypy)
- Docker
- Concepts from Designing Data-Intensive Applications (Martin Kleppmann)  
- (Planned) lower-level implementation in C

---

## Future Work

- Benchmarking
- Log compaction  
- Improved concurrency handling  
