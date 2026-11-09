# Installing and starting Blockchain P2P

## Requirements

Install Python 3 and pip. `source/requirements.txt` pins `Flask==3.0.0`, `requests==2.31.0`, and `ecdsa==0.18.0`. Python 3.10 or 3.11 is a practical reproducible choice; verify other versions yourself. No external database is needed because node state uses local JSON files.

## Linux/macOS

From the project root:

```bash
cd source
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py --host 127.0.0.1 --port 5000
```

On Ubuntu, install the relevant `python3-venv` OS package if the venv module is unavailable. Open `http://127.0.0.1:5000`. The default runtime directory (from within `source/`) is `node_data/node_5000/`, and logs go to `blockchain_node.log`. `wallet.json` contains the private key as plaintext JSON.

## Windows PowerShell

```powershell
cd source
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py --host 127.0.0.1 --port 5000
```

If activation is blocked, use `.venv\Scripts\python.exe app.py --host 127.0.0.1 --port 5000` directly rather than changing machine-wide execution policy.

## Three-node demonstration

Open three independent terminal windows, each with the environment activated and working directory set to `source/`:

```bash
python app.py --host 127.0.0.1 --port 5000
python app.py --host 127.0.0.1 --port 5001
python app.py --host 127.0.0.1 --port 5002
```

The three commands above belong in **separate terminals**. Each port gets separate JSON state. Automatic peer discovery uses UDP port 9999 and network scanning; behavior depends on the firewall and host network. If discovery fails, follow [manual registration instructions](usage.md). To disable discovery, add `--no-discovery` and manage peers manually. `python app.py --help` lists available flags.

For convenience, `bash scripts/run-node.sh --host 127.0.0.1 --port 5000` launches a node from the package root. Avoid exposing this unauthenticated demo to public networks.
