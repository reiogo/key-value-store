# Key-Value Store
I created a key-value storage engine that is similar to Bitcask. I wrote this in Python because I wanted to emphasize getting a hands-on perspective of database internals. (I limited myself to not use any ai-generated code. I still asked llms about what would be considered the canonical way of doing something, but I didn't always agree. Otherwise I used llms to help format my documentation)

A friend of mine, an ex Google SRE, recommended that I study “Designing Data-Intensive Applications” by Martin Kleppmann in my first year of transitioning from biology to computer science (which is a bit wild to think about now), so we went through the book chapter by chapter. 

Last year I finished a course on systematic program design (“How to Design Programs” by Felleisen et al), and I felt confident in being able to start implementing these ideas from DDIA, so it has been on my mind for a wild to implement this. I think other db algorithms like B-Trees and lsm-trees are also really interesting.

I built this project using a “Tracer Bullet” approach (from “the Pragmatic Programmer”) where I create an end-to-end skeleton and build features from that frame. I personally think the tests are the most interesting part of this project, especially since this project working well means a user types in PUT and then GET's a value back. It’s not exactly exciting stuff.

---

## Architecture

- TCP server using Python's `socket` library with a simple binary protocol (`GET`, `PUT`, `DELETE`)
- In-memory hash index for amortized O(1) reads
- Append-only log with length-prefixed binary encoding
- Background merge and compaction for space reclamation
- Crash recovery via log replay on startup
- Docker-based development environment
- Type-checked with mypy, tested with pytest
