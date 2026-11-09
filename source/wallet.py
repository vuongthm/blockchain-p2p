import ecdsa
import hashlib
import json
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class Wallet:
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.address = None

    def generate_keys(self):
        """Generate new ECDSA secp256k1 key pair"""
        signing_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        verifying_key = signing_key.get_verifying_key()

        self.private_key = signing_key.to_string().hex()
        self.public_key = verifying_key.to_string().hex()
        self.address = self.generate_address(self.public_key)

        logger.info(f"Wallet generated: {self.address[:12]}...")

    @staticmethod
    def generate_address(public_key: str) -> str:
        """Generate address from public key using SHA256"""
        return hashlib.sha256(public_key.encode()).hexdigest()[:40]

    def sign_transaction(self, tx: Dict) -> str:
        """Sign transaction with private key"""
        if not self.private_key:
            raise ValueError("No private key available")

        signing_key = ecdsa.SigningKey.from_string(
            bytes.fromhex(self.private_key),
            curve=ecdsa.SECP256k1
        )

        # Sign only essential fields
        tx_data = {k: tx.get(k) for k in ['sender', 'receiver', 'amount']}
        message = json.dumps(tx_data, sort_keys=True).encode()
        signature = signing_key.sign(message)

        return signature.hex()

    @staticmethod
    def verify_signature(tx: Dict, public_key: str) -> bool:
        """Verify transaction signature"""
        try:
            verifying_key = ecdsa.VerifyingKey.from_string(
                bytes.fromhex(public_key),
                curve=ecdsa.SECP256k1
            )

            signature_hex = tx.get('signature')
            if not signature_hex:
                return False

            # Verify only essential fields
            tx_data = {k: tx.get(k) for k in ['sender', 'receiver', 'amount']}
            message = json.dumps(tx_data, sort_keys=True).encode()

            verifying_key.verify(bytes.fromhex(signature_hex), message)
            return True

        except (ecdsa.BadSignatureError, ValueError, KeyError):
            return False

    def to_dict(self) -> Dict:
        """Convert wallet to dictionary"""
        return {
            'private_key': self.private_key,
            'public_key': self.public_key,
            'address': self.address
        }

    def from_dict(self, data: Dict):
        """Load wallet from dictionary"""
        self.private_key = data.get('private_key')
        self.public_key = data.get('public_key')
        self.address = data.get('address')

        if not all([self.private_key, self.public_key, self.address]):
            raise ValueError("Invalid wallet data")

