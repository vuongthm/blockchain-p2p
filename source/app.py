from flask import Flask, jsonify, request, send_from_directory
import requests
import argparse
import socket
import threading
import time
import json
import logging
from pathlib import Path
from blockchain import Blockchain
from wallet import Wallet
from storage import Storage

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.FileHandler('blockchain_node.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global state
blockchain = Blockchain()
wallet = Wallet()
storage = None
peers = set()
peers_lock = threading.Lock()
current_port = 5000
node_url = None
discovery_running = False
blacklisted_peers = set()
peer_violations = {}
MAX_VIOLATIONS = 3

# ============================================================================
# NETWORK UTILITIES
# ============================================================================

def get_local_ip():
    """Get LAN IP address"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

def find_available_port(start=5000, max_tries=100):
    """Find available port"""
    for port in range(start, start + max_tries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No available ports in range {start}-{start+max_tries}")

def normalize_peer_url(url):
    """Normalize peer URL to LAN IP"""
    local_ip = get_local_ip()
    if 'localhost' in url or '127.0.0.1' in url:
        port = url.split(':')[-1]
        return f"http://{local_ip}:{port}"
    return url.rstrip('/')

def is_self(peer_url):
    """Check if peer URL is this node"""
    local_ip = get_local_ip()
    peer_norm = normalize_peer_url(peer_url)
    self_urls = [node_url, f"http://localhost:{current_port}",
                 f"http://127.0.0.1:{current_port}", f"http://{local_ip}:{current_port}"]
    return peer_norm in [normalize_peer_url(u) for u in self_urls]

def is_blacklisted(peer_url):
    """Check if peer is blacklisted"""
    return normalize_peer_url(peer_url) in blacklisted_peers

# ============================================================================
# BYZANTINE FAULT TOLERANCE
# ============================================================================

def blacklist_peer(peer_url, reason):
    """Blacklist malicious peer"""
    peer_url = normalize_peer_url(peer_url)
    with peers_lock:
        blacklisted_peers.add(peer_url)
        peers.discard(peer_url)
    storage.save_peers(list(peers))
    logger.warning(f"BLACKLISTED: {peer_url} - {reason}")

def report_violation(peer_url, violation_type):
    """Report peer violation and blacklist if threshold exceeded"""
    peer_url = normalize_peer_url(peer_url)
    peer_violations[peer_url] = peer_violations.get(peer_url, 0) + 1
    logger.warning(f"Violation #{peer_violations[peer_url]}: {peer_url} - {violation_type}")

    if peer_violations[peer_url] >= MAX_VIOLATIONS:
        blacklist_peer(peer_url, f"Exceeded {MAX_VIOLATIONS} violations")
        return True
    return False

# ============================================================================
# PEER DISCOVERY
# ============================================================================

def broadcast_presence():
    """Broadcast node presence via UDP"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            message = json.dumps({
                'type': 'peer_announce',
                'url': node_url,
                'port': current_port,
                'timestamp': time.time()
            }).encode()
            sock.sendto(message, ('255.255.255.255', 9999))
    except Exception:
        pass

def listen_for_peers():
    """Listen for peer announcements"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', 9999))
            sock.settimeout(2)

            while discovery_running:
                try:
                    data, _ = sock.recvfrom(1024)
                    msg = json.loads(data.decode())
                    if msg.get('type') == 'peer_announce':
                        peer_url = normalize_peer_url(msg.get('url'))
                        if peer_url and not is_self(peer_url) and not is_blacklisted(peer_url):
                            with peers_lock:
                                if peer_url not in peers:
                                    logger.info(f"Discovered: {peer_url}")
                                    threading.Thread(target=sync_with_peer,
                                                   args=(peer_url,), daemon=True).start()
                except (socket.timeout, Exception):
                    continue
    except Exception as e:
        logger.error(f"Peer listener failed: {e}")

def scan_local_network():
    """Scan local network for peers"""
    local_ip = get_local_ip()

    # Scan same machine
    for port in range(5000, 5020):
        if port != current_port:
            check_peer(f"http://{local_ip}:{port}")

    # Scan LAN
    if local_ip != "127.0.0.1":
        base_ip = '.'.join(local_ip.split('.')[:3])
        current_last = int(local_ip.split('.')[-1])
        for offset in range(-15, 16):
            ip_last = current_last + offset
            if 1 <= ip_last <= 254:
                target = f"{base_ip}.{ip_last}"
                if target != local_ip:
                    check_peer(f"http://{target}:{current_port}")

def check_peer(peer_url, timeout=0.5):
    """Check if peer is alive and add"""
    if is_self(peer_url) or is_blacklisted(peer_url):
        return
    try:
        response = requests.get(f"{peer_url}/info", timeout=timeout)
        if response.status_code == 200:
            peer_url = normalize_peer_url(peer_url)
            with peers_lock:
                if peer_url not in peers:
                    logger.info(f"Found: {peer_url}")
                    threading.Thread(target=sync_with_peer,
                                   args=(peer_url,), daemon=True).start()
    except requests.exceptions.RequestException:
        pass

def heartbeat_checker():
    """Check peer health periodically"""
    while discovery_running:
        time.sleep(15)
        with peers_lock:
            dead = [p for p in list(peers)
                   if is_blacklisted(p) or not check_peer_alive(p)]
            for peer in dead:
                peers.discard(peer)
                if not is_blacklisted(peer):
                    logger.info(f"Disconnected: {peer}")
            if dead:
                storage.save_peers(list(peers))

def check_peer_alive(peer):
    """Check if peer is responsive"""
    try:
        response = requests.get(f"{peer}/info", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def auto_discovery_loop():
    """Main discovery loop"""
    scan_count = 0
    while discovery_running:
        broadcast_presence()
        scan_count += 1
        if scan_count >= 3:
            scan_local_network()
            scan_count = 0
        time.sleep(10)

def periodic_storage_save():
    """Periodically save data"""
    while discovery_running:
        time.sleep(60)
        try:
            storage.save_seen_txs(blockchain.seen_tx_ids)
        except Exception as e:
            logger.error(f"Periodic save failed: {e}")

# ============================================================================
# PEER SYNCHRONIZATION
# ============================================================================

def sync_with_peer(peer):
    """Sync blockchain and mempool with peer"""
    if is_self(peer) or is_blacklisted(peer):
        return False

    try:
        # Register with peer
        response = requests.post(f"{peer}/nodes/register",
                                json={'node': node_url}, timeout=3)
        if response.status_code != 200:
            return False

        peer = normalize_peer_url(peer)
        with peers_lock:
            peers.add(peer)
            storage.save_peers(list(peers))

        # Sync blockchain
        chain_resp = requests.get(f"{peer}/chain", timeout=3)
        if chain_resp.status_code == 200:
            peer_chain = chain_resp.json()['chain']
            if not blockchain.is_valid_chain(peer_chain):
                logger.warning(f"{peer} has invalid chain")
                report_violation(peer, "Invalid blockchain")
                return False

            if blockchain.resolve_conflicts([peer_chain]):
                storage.save_blockchain(blockchain.chain)
                logger.info(f"Synced chain from {peer}")

        # Sync mempool
        mempool_resp = requests.get(f"{peer}/mempool", timeout=3)
        if mempool_resp.status_code == 200:
            for tx in mempool_resp.json()['transactions']:
                blockchain.add_transaction(tx)
            storage.save_mempool(blockchain.mempool)

        logger.info(f"Connected: {peer}")
        return True

    except requests.exceptions.RequestException:
        return False

def broadcast(endpoint, data, timeout=1):
    """Broadcast to all active peers"""
    with peers_lock:
        peer_list = [p for p in list(peers) if not is_blacklisted(p)]

    for peer in peer_list:
        try:
            requests.post(f"{peer}{endpoint}", json=data, timeout=timeout)
        except requests.exceptions.RequestException:
            pass



# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def index():
    template_path = Path(__file__).parent / 'templates' / 'index.html'
    return send_from_directory(template_path.parent, template_path.name)

@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify({'length': len(blockchain.chain), 'chain': blockchain.chain})

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    data = request.json
    broadcasted = data.pop('broadcasted', False)

    # Auto-sign if no signature present (from this node)
    if 'signature' not in data:
        clean_tx = {k: data.get(k) for k in ['sender', 'receiver', 'amount']}
        data['signature'] = wallet.sign_transaction(clean_tx)
        data['public_key'] = wallet.public_key

    success, message = blockchain.add_transaction(data)

    if success:
        if not broadcasted:
            data['broadcasted'] = True
            broadcast('/transactions/new', data)
        storage.save_mempool(blockchain.mempool)
        return jsonify({'message': message}), 201

    return jsonify({'error': message}), 400

@app.route('/transactions/validate', methods=['POST'])
def validate_transaction():
    data = request.json
    sender = data.get('sender')
    receiver = data.get('receiver')
    amount = data.get('amount')
    errors = []

    if not receiver:
        errors.append('Receiver required')
    elif not blockchain.is_valid_address(receiver):
        errors.append('Invalid address format')
    elif sender == receiver:
        errors.append('Cannot send to yourself')

    if amount is None:
        errors.append('Amount required')
    else:
        try:
            if float(amount) <= 0:
                errors.append('Amount must be positive')
        except ValueError:
            errors.append('Invalid amount')

    if not errors and blockchain.get_balance(sender) < amount:
        errors.append('Insufficient balance')

    return jsonify({'valid': not errors, 'errors': errors}), (400 if errors else 200)

@app.route('/transactions/recent/<address>', methods=['GET'])
def recent_transactions(address):
    limit = request.args.get('limit', 5, type=int)
    return jsonify({'transactions': blockchain.get_recent_transactions(address, limit)})

@app.route('/balance/<address>', methods=['GET'])
def get_balance(address):
    return jsonify({'address': address, 'balance': blockchain.get_balance(address)})

@app.route('/mine', methods=['POST', 'GET'])
def mine():
    block = blockchain.mine_block(wallet.address)
    if not block:
        return jsonify({'message': 'Cannot mine: max supply reached'}), 400

    storage.save_blockchain(blockchain.chain)
    storage.save_mempool(blockchain.mempool)

    broadcast('/block/new', {'block': block})
    broadcast('/nodes/resolve', {})

    return jsonify({'message': 'Block mined successfully', 'block': block})

@app.route('/block/new', methods=['POST'])
def receive_block():
    """Receive and validate block from peer"""
    block = request.json.get('block')
    if not block:
        return jsonify({'message': 'No block data'}), 400

    if len(blockchain.chain) > 0:
        last = blockchain.chain[-1]
        if block['index'] == len(blockchain.chain) and block['previous_hash'] == last['hash']:
            valid, reason = blockchain.validate_block(block, last)
            if not valid:
                logger.warning(f"Invalid block: {reason}")
                return jsonify({'error': 'Invalid block', 'reason': reason}), 400

            blockchain.chain.append(block)
            blockchain.remove_transactions_from_mempool(block['transactions'])
            storage.save_blockchain(blockchain.chain)
            storage.save_mempool(blockchain.mempool)
            logger.info(f"✓ Block #{block['index']} accepted")

    return jsonify({'message': 'Block received'})

@app.route('/mempool', methods=['GET'])
def get_mempool():
    return jsonify({'transactions': blockchain.mempool})

@app.route('/nodes', methods=['GET'])
def get_nodes():
    with peers_lock:
        return jsonify({
            'nodes': list(peers),
            'blacklisted': list(blacklisted_peers),
            'violations': peer_violations
        })

@app.route('/nodes/register', methods=['POST'])
def register_node():
    node = request.json.get('node')
    if not node:
        return jsonify({'error': 'Missing node URL'}), 400
    if is_self(node):
        return jsonify({'message': 'Cannot register self'}), 400
    if is_blacklisted(node):
        return jsonify({'error': 'Node is blacklisted'}), 403

    node = normalize_peer_url(node)
    with peers_lock:
        if node not in peers:
            peers.add(node)
            storage.save_peers(list(peers))
            logger.info(f"Registered: {node}")

    return jsonify({'message': 'Registered', 'total_peers': len(peers)})

@app.route('/nodes/resolve', methods=['POST'])
def resolve():
    """Resolve chain conflicts with Byzantine detection"""
    with peers_lock:
        peer_list = [p for p in list(peers) if not is_blacklisted(p)]

    chains = []
    invalid_peers = []

    for peer in peer_list:
        try:
            response = requests.get(f"{peer}/chain", timeout=2)
            if response.status_code == 200:
                peer_chain = response.json()['chain']
                if blockchain.is_valid_chain(peer_chain):
                    chains.append(peer_chain)
                else:
                    invalid_peers.append(peer)
        except requests.exceptions.RequestException:
            pass

    for peer in invalid_peers:
        report_violation(peer, "Invalid blockchain during sync")

    if blockchain.resolve_conflicts(chains):
        storage.save_blockchain(blockchain.chain)
        if blockchain.chain:
            blockchain.remove_transactions_from_mempool(blockchain.chain[-1]['transactions'])
            storage.save_mempool(blockchain.mempool)
        return jsonify({
            'message': 'Chain replaced',
            'length': len(blockchain.chain),
            'invalid_peers': len(invalid_peers)
        })

    return jsonify({
        'message': 'Chain authoritative',
        'length': len(blockchain.chain),
        'invalid_peers': len(invalid_peers)
    })

@app.route('/info', methods=['GET'])
def info():
    with peers_lock:
        peer_count = len(peers)
        blacklist_count = len(blacklisted_peers)

    return jsonify({
        'node_url': node_url,
        'port': current_port,
        'ip': get_local_ip(),
        'address': wallet.address,
        'public_key': wallet.public_key,
        'balance': blockchain.get_balance(wallet.address),
        'chain_length': len(blockchain.chain),
        'peers': peer_count,
        'blacklisted_peers': blacklist_count,
        'mempool': len(blockchain.mempool),
        'total_supply': blockchain.get_total_supply(),
        'max_supply': blockchain.MAX_SUPPLY,
        'mining_reward': blockchain.get_mining_reward()
    })

# ============================================================================
# NODE INITIALIZATION & MAIN
# ============================================================================

def init_node():
    """Initialize node"""
    global storage, node_url

    storage = Storage(f'node_{current_port}')
    node_url = f"http://{get_local_ip()}:{current_port}"

    # Load or create wallet
    wallet_data = storage.load_wallet()
    if wallet_data:
        wallet.from_dict(wallet_data)
        logger.info(f"Wallet loaded: {wallet.address[:12]}...")
    else:
        wallet.generate_keys()
        storage.save_wallet(wallet.to_dict())
        logger.info(f"Wallet created: {wallet.address[:12]}...")

    # Load or create blockchain
    chain = storage.load_blockchain()
    if chain and blockchain.is_valid_chain(chain):
        blockchain.chain = chain
        logger.info(f"Blockchain loaded: {len(blockchain.chain)} blocks")
    else:
        if chain:
            logger.warning("⚠️ Stored blockchain invalid! Creating new genesis")
        blockchain.create_genesis_block()
        storage.save_blockchain(blockchain.chain)

    # Load mempool and seen transactions
    blockchain.mempool = storage.load_mempool()
    blockchain.seen_tx_ids = storage.load_seen_txs()

    # Load and sync with saved peers
    saved_peers = storage.load_peers()
    if saved_peers:
        logger.info(f"Loading {len(saved_peers)} saved peers")
        with peers_lock:
            for peer in saved_peers:
                if not is_self(peer) and not is_blacklisted(peer):
                    peer = normalize_peer_url(peer)
                    peers.add(peer)
                    threading.Thread(target=sync_with_peer,
                                   args=(peer,), daemon=True).start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Blockchain P2P Node')
    parser.add_argument('--port', type=int, help='Port number')
    parser.add_argument('--host', default='0.0.0.0', help='Host IP')
    parser.add_argument('--no-discovery', action='store_true', help='Disable auto-discovery')
    args = parser.parse_args()

    current_port = args.port or find_available_port()

    print("\n" + "=" * 60)
    print("BLOCKCHAIN P2P NODE - BYZANTINE FAULT TOLERANT")
    print("=" * 60)

    init_node()

    # Start discovery threads
    if not args.no_discovery:
        discovery_running = True
        threads = [
            threading.Thread(target=listen_for_peers, daemon=True),
            threading.Thread(target=auto_discovery_loop, daemon=True),
            threading.Thread(target=heartbeat_checker, daemon=True),
            threading.Thread(target=periodic_storage_save, daemon=True),
            threading.Thread(target=scan_local_network, daemon=True)
        ]
        for t in threads:
            t.start()
        logger.info("Auto-discovery enabled")
    else:
        logger.info("Auto-discovery disabled")

    print(f"\nNode URL: {node_url}")
    print(f"Balance: {blockchain.get_balance(wallet.address)}")
    print(f"Blocks: {len(blockchain.chain)}")
    print(f"Peers: {len(peers)}")
    print(f"Mining Reward: {blockchain.get_mining_reward()}")
    print(f"Security: Signature + Byzantine Detection ENABLED ✓")
    print("=" * 60 + "\n")

    app.run(host=args.host, port=current_port, debug=False, threaded=True)
