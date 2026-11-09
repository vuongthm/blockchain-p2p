# Blockchain P2P — Educational Peer-to-Peer Blockchain

> **Educational software only.** This repository demonstrates a small blockchain network. It is **not a production cryptocurrency**, a financial product, or a secure public-network service.

Blockchain P2P is a Python and Flask prototype demonstrating SHA-256-linked blocks, a simplified Proof-of-Work (PoW) mining process, ECDSA secp256k1 wallets and signatures, a transaction pool (mempool), HTTP peer synchronization, local-area peer discovery, JSON-based persistence, and a browser dashboard.

The project source and all instructions are in **English**. The only translated editions are the two **technical reports**, supplied separately in English and Vietnamese under `reports/`.

## Features and implementation scope

| Component | Behavior in the provided source |
|---|---|
| Blockchain | Blocks linked using SHA-256; chain checks and a fixed-difficulty simulated PoW miner. |
| Transactions | ECDSA signatures, a pending-transaction pool, balance checks, and a coinbase reward. |
| Wallet | secp256k1 key pair with a SHA-256-derived 40-character hexadecimal address. |
| Peer networking | HTTP endpoints for node registration, chain exchange, and transaction/block broadcasting; UDP-based LAN discovery. |
| Persistence | Per-node JSON files containing wallet, blockchain, mempool, and known peers. |
| User interface | HTML, CSS, and JavaScript dashboard served by Flask. |

The implementation is a **learning prototype**. It does not establish Byzantine fault tolerance, production-grade consensus safety, or secure key custody. See [Security and Limitations](docs/security-and-limitations.md).

## Quick start

Python 3 with `venv` and `pip` is required. Python 3.10 or 3.11 is a practical starting point. From the project root on Linux or macOS:

```bash
cd source
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py --host 127.0.0.1 --port 5000
```

Open **http://127.0.0.1:5000** for the dashboard or **http://127.0.0.1:5000/info** to inspect node status. Windows PowerShell instructions are in the [Installation Guide](docs/installation.md).

To demonstrate three independent nodes, use three terminal windows (each inside `source/` with the environment activated):

```bash
python app.py --host 127.0.0.1 --port 5000
python app.py --host 127.0.0.1 --port 5001
python app.py --host 127.0.0.1 --port 5002
```

Nodes may discover one another automatically on an appropriate local network. On a loopback setup, if discovery does not work, register peers manually using the [Usage Guide](docs/usage.md). Do **not** expose these unauthenticated services to the public Internet.

## Repository layout

```text
blockchain-p2p-project-english/
├── README.md
├── .gitignore
├── SHA256SUMS
├── reports/
│   ├── Blockchain_P2P_Report_EN.docx   # English technical report
│   └── Blockchain_P2P_Report_VI.docx   # Vietnamese technical report
├── source/
│   ├── README.md                        # English source-code guide
│   ├── app.py                           # HTTP API and P2P orchestration
│   ├── blockchain.py                    # Blocks, mining, and validation
│   ├── wallet.py                        # ECDSA wallet and signatures
│   ├── storage.py                       # Local JSON persistence
│   ├── requirements.txt
│   └── templates/index.html             # Browser user interface
├── docs/
│   ├── installation.md
│   ├── usage.md
│   ├── architecture.md
│   ├── api.md
│   ├── testing.md
│   └── security-and-limitations.md
└── scripts/
    ├── run-node.sh
    └── check_project.py
```

## Documentation

| Topic | Guide |
|---|---|
| Installation and setup | [Installation](docs/installation.md) |
| Starting nodes, wallet operations, and mining | [Usage](docs/usage.md) |
| Components, processing flows, and code map | [Architecture](docs/architecture.md) |
| REST endpoints and example requests | [API Reference](docs/api.md) |
| Reproducible test procedures | [Testing](docs/testing.md) |
| Threats, operational constraints, and known gaps | [Security and Limitations](docs/security-and-limitations.md) |

## Technical reports

Two **editable Word reports** are available in [`reports/`](reports/):

- [`Blockchain_P2P_Report_EN.docx`](reports/Blockchain_P2P_Report_EN.docx) — English edition.
- [`Blockchain_P2P_Report_VI.docx`](reports/Blockchain_P2P_Report_VI.docx) — Vietnamese edition.

Both reports are retained as supplied in the previous package. They are the **only** non-English deliverables in this repository.

## Safety and publication notes

**Never commit `node_data/`**: `wallet.json` contains an **unencrypted private key**. The `.gitignore` excludes runtime data, but you should also inspect `git status` and review all staged files before publishing. The API is intended for a trusted local demonstration, not a public service. The repository has no `LICENSE` file; the owner must select an appropriate license before inviting reuse.

Use `python3 scripts/check_project.py` from the project root to validate the expected files and Python syntax. It does **not** run multi-node integration tests or certify security or performance. `SHA256SUMS` provides SHA-256 hashes of the packaged files.
