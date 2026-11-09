# REST API reference

Endpoints are defined in `source/app.py`. The examples use a node listening at `http://127.0.0.1:5000`. This server does not provide production-ready authentication or authorization and must not be exposed to untrusted networks.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Serve the web UI. |
| GET | `/info` | Node, wallet address, balance, chain length, peers and reward. |
| GET | `/chain` | Current chain and length. |
| GET | `/mempool` | Pending transactions. |
| GET | `/nodes` | Peers, blacklist and violation counters. |
| GET | `/balance/<address>` | Address balance based on the current chain. |
| GET | `/transactions/recent/<address>` | Recent transactions; supports `?limit=5`. |
| POST | `/transactions/new` | Validate and enqueue a transaction; signs with local wallet when unsigned. |
| POST | `/transactions/validate` | Preliminary input validation. |
| GET, POST | `/mine` | Mine and broadcast a block; prefer POST for demos. |
| POST | `/block/new` | Receive and validate an incoming block. |
| POST | `/nodes/register` | Register a peer. |
| POST | `/nodes/resolve` | Compare chains with peers. |

## Examples

```bash
curl http://127.0.0.1:5000/info
curl -X POST http://127.0.0.1:5000/nodes/register \
  -H 'Content-Type: application/json' \
  -d '{"node":"http://127.0.0.1:5001"}'
```

For preliminary transaction validation:

```bash
curl -X POST http://127.0.0.1:5000/transactions/validate \
  -H 'Content-Type: application/json' \
  -d '{"sender":"<SENDER_ADDRESS>","receiver":"<RECEIVER_ADDRESS>","amount":1}'
```

A successful preliminary validation response is not a guarantee that the transaction will later be accepted or confirmed. Always inspect the actual response from `/transactions/new` and the resulting chain after mining.
