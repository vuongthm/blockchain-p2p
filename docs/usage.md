# Web interface and node operations

## Using the dashboard

Start the server and open `http://127.0.0.1:5000`. The UI presents wallet details, chain length, peers, a mempool overview, mining, and transaction submission. A freshly created wallet starts with zero balance. Mining a block creates a simulated coinbase reward. `Blockchain.difficulty` defaults to four leading zeroes in the hexadecimal SHA-256 digest; mining time depends on CPU and should not be quoted as a guaranteed measurement.

## Basic JSON endpoints

```bash
curl http://127.0.0.1:5000/info
curl http://127.0.0.1:5000/chain
curl http://127.0.0.1:5000/nodes
curl http://127.0.0.1:5000/mempool
curl -X POST http://127.0.0.1:5000/mine
```

Read the `address` field from `/info`; it identifies the local node wallet. After mining, compare `/info` and `/chain` before and after.

## Sending a transaction

After node 5000 has mined funds, retrieve both nodes' addresses and issue:

```bash
curl -X POST http://127.0.0.1:5000/transactions/new \
  -H 'Content-Type: application/json' \
  -d '{"sender":"<NODE_5000_ADDRESS>","receiver":"<NODE_5001_ADDRESS>","amount":1}'
```

When `signature` is omitted, the receiving node signs using **its local wallet**. The supplied `sender` must therefore match node 5000's wallet address. An accepted transfer enters the mempool; mining is required to include it in a block. Input validation is not production-grade: use controlled test values.

## Manual peer registration

If discovery does not work, register peers in both directions:

```bash
curl -X POST http://127.0.0.1:5000/nodes/register \
  -H 'Content-Type: application/json' \
  -d '{"node":"http://127.0.0.1:5001"}'

curl -X POST http://127.0.0.1:5001/nodes/register \
  -H 'Content-Type: application/json' \
  -d '{"node":"http://127.0.0.1:5000"}'

curl -X POST http://127.0.0.1:5000/nodes/resolve
```

Registering an address alone does not force mempool synchronization. The resolve endpoint fetches peer chains and considers longer valid ones. Confirm actual results via both nodes' `/nodes` and `/chain` endpoints; nodes generate time-dependent genesis blocks independently.

## Shutdown and persistence

Use `Ctrl+C` in each terminal. Node state is stored under `source/node_data/node_<port>/` and includes an unencrypted wallet private key. Do not publish these folders. The software is for local educational simulation.
