# Testing and evidence collection

This document defines **reproducible test procedures**, not fabricated measurement results. Record the environment, exact commands, timestamps, HTTP responses and logs before marking any case as passed. The supplied source does not include a verified automated integration suite or benchmark results.

## Offline package check

```bash
python3 scripts/check_project.py
```

This checks Python syntax with the standard-library `ast` parser and required package files. It does **not** establish functional correctness, consensus safety, or application security.

## Suggested manual test matrix

| ID | Goal | Procedure | Evidence |
|---|---|---|---|
| T01 | Start a node | Start port 5000; GET `/info`. | HTTP status, wallet, chain length, logs. |
| T02 | Persistence | Mine, restart, inspect state. | Address and chain length before/after. |
| T03 | PoW | POST `/mine`. | Nonce, hash, block index, measured time. |
| T04 | Valid transfer | Mine funds, transfer, mine again. | API response, mempool, balances. |
| T05 | Invalid signature | Submit a forged signature in an isolated test. | Error response and log. |
| T06 | Peer discovery | Start 2–3 ports; GET `/nodes`. | Observed peer list at each port. |
| T07 | Chain resolution | Make A longer, call resolve from B. | Chain lengths/hashes before/after. |
| T08 | Invalid block | Send a block with an invalid previous hash in a lab. | Rejection behavior and logs. |

For every case record `Pass`, `Fail`, or `Not run` plus observed output, Python/OS versions, CPU and network context. Do not claim throughput from an assumed block interval or assert a Byzantine fault threshold without supporting measurements and an appropriate protocol. Independently generated genesis blocks and competing branches can affect multi-node experiments.

## Run record template

```text
Test ID:
Environment:
Preconditions:
Actions:
Expected result:
Actual result:
Evidence:
Status: Pass | Fail | Not run
Limitations:
```
