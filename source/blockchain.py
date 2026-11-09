import hashlib
import json
import time
import logging
from typing import List, Dict, Optional, Tuple
import threading

logger = logging.getLogger(__name__)

class Blockchain:
    MAX_SUPPLY = 13082005
    HALVING_INTERVAL = 100
    INITIAL_REWARD = 50
    MAX_TX_PER_BLOCK = 10

    def __init__(self):
        self.chain: List[Dict] = []
        self.mempool: List[Dict] = []
        self.difficulty = 4
        self.seen_tx_ids: set = set()
        self.lock = threading.RLock()

    def create_genesis_block(self):
        """Create genesis block"""
        if not self.chain:
            genesis = {
                'index': 0,
                'timestamp': time.time(),
                'transactions': [],
                'nonce': 0,
                'previous_hash': '0'
            }
            genesis['hash'] = self._hash(genesis)
            self.chain.append(genesis)
            logger.info("Genesis block created")

    def _hash(self, block: Dict) -> str:
        """Calculate block hash"""
        block_copy = {k: v for k, v in block.items() if k != 'hash'}
        return hashlib.sha256(json.dumps(block_copy, sort_keys=True).encode()).hexdigest()

    def _proof_of_work(self, block: Dict) -> int:
        """Find nonce that satisfies difficulty"""
        target = '0' * self.difficulty
        nonce = 0
        while True:
            block['nonce'] = nonce
            if self._hash(block).startswith(target):
                return nonce
            nonce += 1

    def get_mining_reward(self) -> float:
        """Calculate mining reward with halving"""
        halvings = len(self.chain) // self.HALVING_INTERVAL
        return self.INITIAL_REWARD / (2 ** halvings)

    def get_total_supply(self) -> float:
        """Calculate total coins in circulation"""
        return sum(tx['amount'] for block in self.chain
                   for tx in block['transactions'] if tx['sender'] == 'COINBASE')

    def _tx_id(self, tx: Dict) -> str:
        """Generate unique transaction ID"""
        data = {k: tx[k] for k in ['sender', 'receiver', 'amount', 'signature']}
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def _check_double_spend(self, tx: Dict) -> bool:
        """Check if transaction would cause double-spending"""
        pending = sum(t['amount'] for t in self.mempool if t['sender'] == tx['sender'])
        return (pending + tx['amount']) > self.get_balance(tx['sender'])

    def _verify_signature(self, tx: Dict) -> Tuple[bool, str]:
        """Verify transaction signature"""
        if tx['sender'] == 'COINBASE':
            return True, 'Coinbase transaction'

        if 'public_key' not in tx:
            return False, 'Missing public key'

        from wallet import Wallet

        if not Wallet.verify_signature(tx, tx['public_key']):
            return False, 'Invalid signature'

        if Wallet.generate_address(tx['public_key']) != tx['sender']:
            return False, 'Public key mismatch'

        return True, 'Valid'

    def add_transaction(self, tx: Dict) -> Tuple[bool, str]:
        """Add transaction to mempool with validation"""
        with self.lock:
            # Required fields check
            if not all(k in tx for k in ['sender', 'receiver', 'amount', 'signature']):
                return False, 'Missing required fields'

            # Signature verification
            valid, msg = self._verify_signature(tx)
            if not valid:
                return False, msg

            # Basic validations
            if not self.is_valid_address(tx['receiver']):
                return False, 'Invalid receiver address'
            if tx['sender'] == tx['receiver']:
                return False, 'Cannot send to self'
            if self._check_double_spend(tx):
                return False, 'Double-spend detected'
            if self.get_balance(tx['sender']) < tx['amount']:
                return False, 'Insufficient balance'

            # Duplicate check
            tx_id = self._tx_id(tx)
            if tx_id in self.seen_tx_ids:
                return False, 'Duplicate transaction'

            # Add to mempool
            self.seen_tx_ids.add(tx_id)
            tx['tx_id'] = tx_id
            tx.setdefault('timestamp', time.time())
            self.mempool.append(tx)

            logger.debug(f"Transaction added: {tx_id[:8]}...")
            return True, 'Added to mempool'

    def mine_block(self, miner: str) -> Optional[Dict]:
        """Mine new block"""
        with self.lock:
            reward = self.get_mining_reward()
            if self.get_total_supply() + reward > self.MAX_SUPPLY:
                logger.warning("Max supply reached")
                return None

            # Create coinbase transaction
            reward_tx = {
                'sender': 'COINBASE',
                'receiver': miner,
                'amount': reward,
                'signature': 'mining_reward',
                'timestamp': time.time()
            }

            # Build block
            last_block = self.chain[-1]
            block = {
                'index': len(self.chain),
                'timestamp': time.time(),
                'transactions': [reward_tx] + self.mempool[:self.MAX_TX_PER_BLOCK],
                'previous_hash': last_block['hash'],
                'nonce': 0
            }

            # Mine
            block['nonce'] = self._proof_of_work(block)
            block['hash'] = self._hash(block)

            # Add to chain
            self.chain.append(block)
            self.mempool = self.mempool[self.MAX_TX_PER_BLOCK:]

            logger.info(f"Block #{block['index']} mined")
            return block

    def validate_block(self, block: Dict, prev_block: Dict) -> Tuple[bool, str]:
        """Validate block structure and PoW"""
        # Structure check
        required = ['index', 'timestamp', 'transactions', 'previous_hash', 'nonce', 'hash']
        if not all(k in block for k in required):
            return False, 'Missing fields'

        # Chain continuity
        if block['index'] != prev_block['index'] + 1:
            return False, 'Invalid index'
        if block['previous_hash'] != prev_block['hash']:
            return False, 'Hash mismatch'

        # Proof of work
        if not block['hash'].startswith('0' * self.difficulty):
            return False, 'Invalid PoW'
        if self._hash(block) != block['hash']:
            return False, 'Block hash mismatch'

        # Coinbase validation
        coinbase_txs = [tx for tx in block['transactions'] if tx['sender'] == 'COINBASE']
        if len(coinbase_txs) != 1:
            return False, f'Invalid coinbase count: {len(coinbase_txs)}'

        expected_reward = self.INITIAL_REWARD / (2 ** (block['index'] // self.HALVING_INTERVAL))
        if abs(coinbase_txs[0]['amount'] - expected_reward) > 0.0001:
            return False, 'Invalid reward amount'

        # Verify all transaction signatures
        for tx in block['transactions']:
            valid, msg = self._verify_signature(tx)
            if not valid:
                return False, f'Transaction {msg}'

        return True, 'Valid'

    def is_valid_chain(self, chain: List[Dict]) -> bool:
        """Validate entire blockchain"""
        if not chain or chain[0]['previous_hash'] != '0' or chain[0]['index'] != 0:
            return False

        for i in range(1, len(chain)):
            valid, _ = self.validate_block(chain[i], chain[i-1])
            if not valid:
                return False

        # Check total supply
        total = sum(tx['amount'] for block in chain
                    for tx in block['transactions'] if tx['sender'] == 'COINBASE')
        return total <= self.MAX_SUPPLY

    def resolve_conflicts(self, chains: List[List[Dict]]) -> bool:
        """Choose longest valid chain"""
        with self.lock:
            max_len = len(self.chain)
            new_chain = None

            for chain in chains:
                if len(chain) > max_len and self.is_valid_chain(chain):
                    max_len = len(chain)
                    new_chain = chain

            if new_chain:
                self.chain = new_chain
                logger.info(f"Chain replaced: {max_len} blocks")
                return True
            return False

    def get_balance(self, address: str) -> float:
        """Calculate address balance"""
        balance = 0.0
        for block in self.chain:
            for tx in block['transactions']:
                if tx['receiver'] == address:
                    balance += tx['amount']
                if tx['sender'] == address:
                    balance -= tx['amount']
        return balance

    def get_recent_transactions(self, address: str, limit: int = 5) -> List[Dict]:
        """Get recent transactions for address"""
        transactions = []
        for block in reversed(self.chain):
            for tx in block['transactions']:
                if tx['sender'] == address or tx['receiver'] == address:
                    transactions.append({**tx, 'block_index': block['index']})
                    if len(transactions) >= limit:
                        return transactions
        return transactions

    def remove_transactions_from_mempool(self, transactions: List[Dict]):
        """Remove mined transactions from mempool"""
        with self.lock:
            tx_sigs = {(tx['sender'], tx['receiver'], tx['amount'], tx['signature'])
                       for tx in transactions}
            self.mempool = [tx for tx in self.mempool
                           if (tx['sender'], tx['receiver'], tx['amount'], tx['signature'])
                           not in tx_sigs]

    @staticmethod
    def is_valid_address(address: str) -> bool:
        """Validate address format (40 hex characters)"""
        if not address or len(address) != 40:
            return False
        try:
            int(address, 16)
            return True
        except ValueError:
            return False
