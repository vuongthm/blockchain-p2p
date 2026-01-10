# Blockchain P2P Network

A simple blockchain system with peer-to-peer networking for educational purposes and demonstration. This project simulates fundamental blockchain concepts like Bitcoin, including Proof of Work, transactions, cryptocurrency wallets, and peer-to-peer network synchronization.

## Project Overview

### What is Blockchain?

Blockchain is a distributed database that stores information as a chain of blocks linked together by cryptographic hashes. Each block contains:
- List of transactions
- Hash of the previous block
- Nonce (number used for Proof of Work)
- Timestamp

### What Does This Project Do?

This project simulates a basic blockchain network with the following features:

**1. Blockchain Core**
- **Proof of Work (PoW)**: Consensus algorithm requiring computation to mine blocks
- **Mining**: Mine new blocks to receive rewards
- **Halving**: Block rewards halve every 100 blocks (similar to Bitcoin)
- **Max Supply**: Maximum total coin limit (1,000,000 coins)
- **Transaction Validation**: Verify transactions before adding to mempool

**2. Cryptography**
- **ECDSA secp256k1**: Digital signature algorithm (same as Bitcoin)
- **Wallet**: Cryptocurrency wallet with public/private key pair
- **Digital Signature**: Sign and verify transactions
- **SHA-256**: Hash function for addresses and block hashes
- **Enforced Signature Verification**: Mandatory verification for all transactions

**3. P2P Network**
- **Auto-discovery**: Automatically find other nodes on LAN
- **UDP Broadcast**: Announce node presence on port 9999
- **Network Scanning**: Scan local network (±15 IPs, ports 5000-5020)
- **Peer Health Check**: Monitor and remove dead peers every 15 seconds
- **Chain Synchronization**: Synchronize blockchain between nodes
- **Consensus**: Longest valid chain rule
- **Byzantine Fault Tolerance**: Detect and blacklist malicious peers after 3 violations

**4. Storage**
- Persistent data storage on disk
- Automatic saving of wallet, blockchain, peers, and mempool
- Data recovery on restart

**5. Web Interface**
- Dashboard to monitor node status
- Send transactions with auto-signing
- Mine new blocks
- View blockchain and transaction history
- Check address balances
- Security badge displaying signature verification status

## Installation

### System Requirements
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step 1: Download Source Code

```bash
# Clone repository (or download source files)
# Navigate to project directory
cd blockchain-p2p
```

### Step 2: Create Virtual Environment

A virtual environment helps isolate project dependencies and avoid conflicts with other Python packages on your system.

#### On Windows:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

**If you encounter "cannot run scripts" error:**

```powershell
# Run PowerShell as Administrator and execute:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try again:
venv\Scripts\activate
```

#### On Linux/macOS:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

**If python3 command doesn't work:**

```bash
# Install python3-venv (Ubuntu/Debian)
sudo apt-get install python3-venv

# Or on Fedora/CentOS
sudo dnf install python3-virtualenv

# Then create virtual environment again
python3 -m venv venv
source venv/bin/activate
```

**Confirm successful activation:**
- Windows: Command line shows `(venv)` prefix
- Linux/macOS: Terminal shows `(venv)` prefix

### Step 3: Install Dependencies

After successfully activating the virtual environment:

```bash
# Install required libraries
pip install -r requirements.txt
```

**If installation errors occur:**

```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Try again
pip install -r requirements.txt
```

## Usage

### Running a Single Node

```bash
python app.py
```

The node will:
- Automatically create a new wallet (or load existing wallet)
- Initialize genesis block (if running for the first time)
- Start on available port (default: 5000)
- Enable auto-discovery to find peers
- Enable signature verification

Access web interface: `http://localhost:5000`

### Running Multiple Nodes to Create P2P Network

Open multiple terminals/cmd windows and run:

```bash
# Terminal 1
python app.py --port 5000

# Terminal 2
python app.py --port 5001

# Terminal 3
python app.py --port 5002
```

Nodes will automatically discover each other on the LAN.

### Startup Options

```bash
# Specify custom port
python app.py --port 5000

# Specify host (default: 0.0.0.0)
python app.py --host 127.0.0.1

# Disable auto-discovery (manual connection only)
python app.py --no-discovery

# View all options
python app.py --help
```

### Using Web Interface

1. **Dashboard**: View node information, balance, blocks, peers
2. **Send Transaction**: Send coins to another address (auto-signed and verified)
3. **Mine Block**: Mine new block to receive reward
4. **Blockchain**: View entire blockchain
5. **Recent Transactions**: View recent transaction history
6. **Security Badge**: Confirm signature verification is active

### API Interaction

#### View Node Information
```bash
curl http://localhost:5000/info
```

#### View Blockchain
```bash
curl http://localhost:5000/chain
```

#### Check Balance
```bash
curl http://localhost:5000/balance/<address>
```

#### Send Transaction (auto-signed)
```bash
curl -X POST http://localhost:5000/transactions/new \
  -H "Content-Type: application/json" \
  -d '{
    "receiver": "a1b2c3d4e5f6...",
    "amount": 10
  }'
```

**Transaction will be automatically:**
1. Signed with node's private key
2. Public key added to transaction
3. Signature verified before adding to mempool
4. Broadcast to peers with complete signature

#### Mine Block
```bash
curl -X POST http://localhost:5000/mine
```

#### View Peer List (including blacklisted peers)
```bash
curl http://localhost:5000/nodes

# Response includes:
# - nodes: active peer list
# - blacklisted: blacklisted peer list
# - violations: violation count per peer
```

#### Synchronize Blockchain
```bash
curl -X POST http://localhost:5000/nodes/resolve
```

## Project Structure

```
blockchain-p2p/
├── app.py                     # Flask app + P2P networking + Byzantine fault tolerance
├── blockchain.py              # Core blockchain logic with signature verification
├── wallet.py                  # ECDSA cryptography + wallet management
├── storage.py                 # JSON-based data persistence
├── requirements.txt           # Python dependencies
├── README.md                  # Documentation (this file)
├── templates/
│   └── index.html            # Web UI with auto-signing support
├── blockchain_node.log        # Application log file (auto-created)
└── node_data/                # Data directory (auto-created)
    └── node_{port}/
        ├── wallet.json          # Private/public keys + address
        ├── blockchain.json      # Complete blockchain data
        ├── peers.json          # Known peer list
        ├── mempool.json        # Pending transactions
        └── seen_txs.json       # Transaction ID set for deduplication
```

## Configuration

Important parameters in `blockchain.py`:

```python
MAX_SUPPLY = 1000000           # Maximum total coins
HALVING_INTERVAL = 100          # Blocks between halvings
INITIAL_REWARD = 50             # Initial block mining reward
MAX_TX_PER_BLOCK = 10          # Maximum transactions per block
difficulty = 4                  # Proof of Work difficulty (number of zeros)
```

Modify these parameters to adjust blockchain behavior.

## How It Works

### 1. Peer Discovery (Auto-discovery)

**Discovery Mechanisms:**
- UDP broadcast on port 9999 every 10 seconds
- LAN scanning every 30 seconds (±15 IP addresses around node's IP)
- Port scanning range: 5000-5020 on same machine
- Heartbeat check every 15 seconds
- Automatic removal of unresponsive peers

```
┌─────────────┐
│   Node A    │  ←  UDP broadcast every 10s (port 9999)
│   :5000     │  →  LAN scan every 30s (±15 IPs)
└─────────────┘  ←  Health check every 15s
       ↕
┌─────────────┐     ┌─────────────┐
│   Node B    │ ←→  │   Node C    │
│   :5001     │     │   :5002     │
└─────────────┘     └─────────────┘
```

### 2. Transaction Flow (Updated)

```
1. User creates transaction (receiver + amount)
   ↓
2. Validate (address, balance, format)
   ↓
3. Automatically sign with node's private key
   ↓
4. Add public_key to transaction
   ↓
5. Verify signature with public_key
   ↓
6. Verify public_key matches sender address
   ↓
7. Add to mempool (if valid)
   ↓
8. Broadcast to all peers
   ↓
9. Wait to be included in block
```

### 3. Mining Process

```
1. Get transactions from mempool (max 10)
   ↓
2. Create coinbase transaction (reward)
   ↓
3. Create new block
   ↓
4. Find valid nonce (Proof of Work)
   ↓  (compute hash until it starts with "0000...")
   ↓
5. Add block to chain
   ↓
6. Remove transactions from mempool
   ↓
7. Broadcast block to peers
   ↓
8. Peers validate and sync
```

### 4. Consensus Mechanism

**Longest Chain Rule with Byzantine Fault Tolerance:**

```
Node A: [Block 0] → [Block 1] → [Block 2]
                                     ↓
Node B: [Block 0] → [Block 1] → [Block 2] → [Block 3]
                                                  ↓
Node C: [Block 0] → [Block 1]               (receives chain from B)
                                                  ↓
Validation: Check all blocks are valid, total supply ≤ MAX_SUPPLY
                                                  ↓
Result: All nodes accept the longest valid chain (from Node B)
```

**Byzantine Detection:**
- Invalid chains are rejected
- Peers sending invalid data receive violation marks
- After 3 violations, peer is automatically blacklisted
- Blacklisted peers are removed from peer list and cannot reconnect

### 5. Signature Verification Flow

```
Transaction arrives at node
   ↓
Check sender != 'COINBASE' ?
   ↓ Yes
Check public_key exists ?
   ↓ Yes
Verify signature with public_key (ECDSA)
   ↓ Valid?
   ↓ Yes
Verify address = hash(public_key) ?
   ↓ Match
✓ Transaction accepted
```

## Security

### Security Improvements (Version 2.0)

**Before:**
```python
# No signature verification
tx = {
    'sender': 'fake_address',
    'receiver': 'victim',
    'amount': 1000000,
    'signature': 'random_string'  # Not checked
}
# → Transaction accepted!
```

**Now:**
```python
# Full verification
tx = {
    'sender': 'real_address',
    'receiver': 'recipient',
    'amount': 100,
    'signature': 'valid_ecdsa_signature',
    'public_key': 'real_public_key'
}

# Checks:
# 1. Is signature valid with public_key?
# 2. Does public_key → address match sender?
# 3. Sufficient balance?
# → Only then accept transaction
```

### Current Security Measures

**Implemented:**
- ECDSA secp256k1 signature verification (enforced)
- Public key validation
- Address verification (SHA-256 hash of public key)
- Double-spend prevention in mempool
- Transaction ID deduplication using seen_tx_ids set
- Balance checking before transaction acceptance
- Address format validation (40 hexadecimal characters)
- Byzantine fault tolerance with peer violation tracking
- Automatic peer blacklisting after 3 violations
- Block validation before chain synchronization

**Not Implemented (educational project):**
- DOS protection
- Rate limiting
- SSL/TLS encryption for P2P communication
- User authentication
- Advanced input sanitization
- Transaction replay protection across different chains

## Current Limitations

This is an educational project, **NOT for production use**. Limitations include:

### Security
- No DOS protection
- No rate limiting
- No SSL/TLS encryption for P2P
- No authentication
- Signature verification implemented (new)

### Performance
- Entire blockchain stored in memory
- No database optimization
- Simple PoW, CPU intensive
- No transaction pooling optimization

### Features
- No transaction fees (all transactions are free)
- No UTXO model (uses account-based like Ethereum)
- No Merkle trees for efficient verification
- No SPV (Simplified Payment Verification)
- No smart contracts
- LAN only (no internet P2P support)
- Fixed difficulty (does not adjust based on network hashrate)

### Scalability
- Not scalable for large networks
- Fixed block size
- No sharding
- No layer 2 solutions

## Development Roadmap

Potential features to improve the project:

### Easy Level
1. **Transaction Fees**: Add transaction fees for miners
2. **Block Explorer**: Interface to view block/transaction details
3. **Config File**: Use YAML/JSON instead of hardcoding
4. **Better Logging**: Log levels, log rotation
5. **Transaction History Pagination**: Paginate history

### Medium Level
1. **UTXO Model**: Switch to UTXO model like Bitcoin
2. **Merkle Trees**: Optimize verification
3. **SPV Support**: Light clients
4. **Network Protocol**: Custom protocol instead of HTTP
5. **Multi-signature Wallets**: Multi-sig wallets
6. **Difficulty Adjustment**: Automatic difficulty adjustment

### Hard Level
1. **Proof of Stake**: Replace PoW with PoS
2. **Smart Contracts**: Add VM to run contracts
3. **Sharding**: Split blockchain into shards
4. **Lightning Network**: Layer 2 solution
5. **Cross-chain Bridge**: Connect with other chains
6. **Zero-knowledge Proofs**: Privacy features

### Security Improvements
1. Enforce signature verification (Done!)
2. Implement rate limiting
3. Add SSL/TLS for P2P
4. DOS protection
5. Stricter input validation
6. Transaction replay protection

### Performance Improvements
1. Database backend (SQLite, PostgreSQL)
2. Cache layer (Redis)
3. Async/await for network calls
4. Block indexing
5. Transaction batching

## Testing

### Test Signature Verification

```bash
# Start node
python app.py

# View logs to confirm signature verification
tail -f blockchain_node.log | grep -i "signature"

# Test sending transaction
curl -X POST http://localhost:5000/transactions/new \
  -H "Content-Type: application/json" \
  -d '{
    "receiver": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
    "amount": 10
  }'

# Success response:
# {"message": "Added to mempool"}

# Logs will show:
# [INFO] Signature verified for tx from abc12345...
```

### Manual Testing

```bash
# Start 3 nodes
python app.py --port 5000
python app.py --port 5001
python app.py --port 5002

# Mine block on node 1
curl -X POST http://localhost:5000/mine

# Send transaction from node 2 (auto-signed)
curl -X POST http://localhost:5001/transactions/new \
  -H "Content-Type: application/json" \
  -d '{
    "receiver": "a1b2c3d4...",
    "amount": 10
  }'

# Check sync on node 3
curl http://localhost:5002/chain

# View logs
cat blockchain_node.log | grep -i "signature"
```

### Check Consistency

```bash
# Compare chain length of nodes
curl http://localhost:5000/info | grep chain_length
curl http://localhost:5001/info | grep chain_length
curl http://localhost:5002/info | grep chain_length

# Sync if needed
curl -X POST http://localhost:5001/nodes/resolve
```

## Common Troubleshooting

### "Invalid signature" Error

**Cause:**
- Transaction missing public_key
- Public key doesn't match sender
- Invalid signature

**Solution:**
```bash
# Send from web UI → automatically signed correctly
# Or send via API with complete information:
curl -X POST http://localhost:5000/transactions/new \
  -H "Content-Type: application/json" \
  -d '{
    "receiver": "...",
    "amount": 10
  }'
# Backend will automatically add signature + public_key
```

### Peers Cannot Connect

**Cause:**
- Firewall blocking port
- Not on same LAN
- UDP port 9999 blocked

**Solution:**
```bash
# Windows: Temporarily disable firewall or add exception
# Linux:
sudo ufw allow 5000:5020/tcp
sudo ufw allow 9999/udp

# Check connectivity
ping <other_node_ip>
```

### Chain Not Synchronizing

**Solution:**
```bash
# Run resolve endpoint
curl -X POST http://localhost:5000/nodes/resolve

# Check logs
cat blockchain_node.log | grep -i sync

# Restart node if needed
```

### Port Already in Use

**Solution:**
```bash
# Use different port
python app.py --port 5001

# Or let it auto-select port
python app.py
```

### "Module not found" Error

**Solution:**
```bash
# Check if venv is activated
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Contributing

Contributions are welcome! Steps:

1. Fork repository
2. Create new branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## Changelog

### Version 2.0 (Latest)
- Enforced signature verification for all transactions
- Public key validation
- Auto-signing in web UI
- Security badge showing verification status
- Improved error messages
- Updated documentation

### Version 1.0
- Basic blockchain functionality
- P2P networking
- Web UI
- Signature not verified (security vulnerability)

## Learning Resources

### Blockchain Basics
- [Bitcoin Whitepaper](https://bitcoin.org/bitcoin.pdf) - Original paper by Satoshi Nakamoto
- [Blockchain Demo](https://andersbrownworth.com/blockchain/) - Visualize blockchain operation
- [Mastering Bitcoin](https://github.com/bitcoinbook/bitcoinbook) - Free book about Bitcoin

### Cryptography
- [ECDSA Explained](https://cryptobook.nakov.com/digital-signatures/ecdsa-sign-verify-messages)
- [SHA-256 Algorithm](https://en.wikipedia.org/wiki/SHA-2)
- [Digital Signatures](https://en.wikipedia.org/wiki/Digital_signature)

### Python & Networking
- [Python Socket Programming](https://realpython.com/python-sockets/)
- [Flask Documentation](https://flask.palletsprojects.com/)

### Video Tutorials
- [Blockchain in Python - YouTube](https://www.youtube.com/results?search_query=blockchain+python+tutorial)

## License

MIT License - See LICENSE file for details

## Author

Educational Project - Blockchain P2P Network

## Contact

If you have questions or encounter issues:
- Open an issue on GitHub
- Email: vuongtranhoangminhhh@gmail.com

---

**Note:** This is an educational project to understand how blockchain works. Do not use in production environments or with real money!
# blockchain-p2p
