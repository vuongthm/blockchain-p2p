# Blockchain P2P — Source Code Guide

This folder contains the executable Python/Flask prototype, together with its browser interface. It is designed for learning, controlled demonstrations, and source-level inspection. For the complete project overview and safety notices, see the [root README](../README.md).

## Modules

| File | Purpose |
|---|---|
| `app.py` | Flask REST API, peer registration/discovery, HTTP synchronization, data broadcasting, application startup, and logging. |
| `blockchain.py` | Block hashing, fixed-difficulty Proof of Work, chain checks, transaction validation, mining rewards, and mempool management. |
| `wallet.py` | Wallet key generation, secp256k1 ECDSA signing/verification, and address derivation. |
| `storage.py` | JSON storage for blockchain state, wallets, peers, and pending transactions. |
| `templates/index.html` | Browser dashboard written in HTML, CSS, and JavaScript. |
| `requirements.txt` | Python runtime dependencies. |

## Install and run

Run these commands in this `source/` folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py --host 127.0.0.1 --port 5000
```

Open `http://127.0.0.1:5000`. For a second node, open a separate terminal, activate the same virtual environment, and run `python app.py --host 127.0.0.1 --port 5001`. A third node may run on port `5002`.

The node exposes endpoints such as `/info`, `/chain`, `/mempool`, `/nodes`, `/transactions/new`, `/mine`, and `/nodes/register`. See the [API Reference](../docs/api.md) for request methods and examples.

## State and security

Each node writes JSON state into `node_data/node_<port>/`, including `wallet.json`. The wallet file stores the private key as **plaintext JSON**. The source code is not suitable for holding real funds or listening on untrusted public networks. Data integrity checks and peer blacklisting do not constitute formally proven Byzantine consensus. Read [Security and Limitations](../docs/security-and-limitations.md) before any network demonstration.

## Documentation links

[Installation](../docs/installation.md) · [Usage](../docs/usage.md) · [Architecture](../docs/architecture.md) · [API](../docs/api.md) · [Testing](../docs/testing.md) · [Security](../docs/security-and-limitations.md)

The two editable technical reports are in [`../reports/`](../reports/)—one English edition and one Vietnamese edition. No other Vietnamese documentation is included.
