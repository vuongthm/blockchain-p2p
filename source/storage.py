import json
import os
import logging
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)

class Storage:
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = os.path.join('node_data', data_dir)
        os.makedirs(self.data_dir, exist_ok=True)

        self.files = {
            'wallet': os.path.join(self.data_dir, 'wallet.json'),
            'blockchain': os.path.join(self.data_dir, 'blockchain.json'),
            'peers': os.path.join(self.data_dir, 'peers.json'),
            'mempool': os.path.join(self.data_dir, 'mempool.json'),
            'seen_txs': os.path.join(self.data_dir, 'seen_txs.json')
        }

    def _read(self, key: str, default: Any = None) -> Any:
        """Generic JSON file reader"""
        file_path = self.files.get(key)
        if not file_path or not os.path.exists(file_path):
            return default

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                return json.loads(content) if content else default
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error reading {key}: {e}")
            return default

    def _write(self, key: str, data: Any):
        """Generic JSON file writer"""
        file_path = self.files.get(key)
        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except (IOError, TypeError) as e:
            logger.error(f"Error writing {key}: {e}")

    def save_wallet(self, wallet_data: Dict):
        self._write('wallet', wallet_data)

    def load_wallet(self) -> Optional[Dict]:
        return self._read('wallet')

    def save_blockchain(self, chain: List[Dict]):
        self._write('blockchain', chain)

    def load_blockchain(self) -> Optional[List[Dict]]:
        return self._read('blockchain')

    def save_peers(self, peers: List[str]):
        self._write('peers', peers)

    def load_peers(self) -> List[str]:
        return self._read('peers', [])

    def save_mempool(self, mempool: List[Dict]):
        self._write('mempool', mempool)

    def load_mempool(self) -> List[Dict]:
        return self._read('mempool', [])

    def save_seen_txs(self, seen_tx_ids: set):
        self._write('seen_txs', list(seen_tx_ids))

    def load_seen_txs(self) -> set:
        return set(self._read('seen_txs', []))
