"""
Encryption layer for secure data storage.
"""

import os
import base64
import json
from typing import Dict, Any, Optional, Tuple
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import secrets
import hashlib


class EncryptionManager:
    """Manages encryption and decryption of sensitive data."""

    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize encryption manager.

        Args:
            master_key: Master encryption key (hex string)
        """
        if master_key:
            self.master_key = bytes.fromhex(master_key)
        else:
            # Generate a new key if none provided
            self.master_key = self._generate_master_key()

        self.backend = default_backend()
        self._key_cache = {}

    def _generate_master_key(self) -> bytes:
        """Generate a new master key."""
        return secrets.token_bytes(32)  # 256-bit key

    def derive_key(
        self,
        password: str,
        salt: Optional[bytes] = None,
        iterations: int = 100000
    ) -> Tuple[bytes, bytes]:
        """
        Derive an encryption key from a password.

        Args:
            password: Password to derive key from
            salt: Optional salt (generated if not provided)
            iterations: Number of iterations for key derivation

        Returns:
            Tuple of (derived_key, salt)
        """
        if salt is None:
            salt = secrets.token_bytes(32)

        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
            backend=self.backend
        )
        key = kdf.derive(password.encode())
        return key, salt

    def encrypt_data(
        self,
        data: Any,
        key: Optional[bytes] = None
    ) -> Dict[str, str]:
        """
        Encrypt data using AES-256-GCM.

        Args:
            data: Data to encrypt (will be JSON serialized)
            key: Encryption key (uses master key if not provided)

        Returns:
            Dictionary containing encrypted data and metadata
        """
        if key is None:
            key = self.master_key

        # Serialize data to JSON
        if isinstance(data, str):
            plaintext = data.encode()
        else:
            plaintext = json.dumps(data).encode()

        # Generate nonce
        nonce = secrets.token_bytes(12)  # 96-bit nonce for GCM

        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce),
            backend=self.backend
        )
        encryptor = cipher.encryptor()

        # Encrypt
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        return {
            'ciphertext': base64.b64encode(ciphertext).decode(),
            'nonce': base64.b64encode(nonce).decode(),
            'tag': base64.b64encode(encryptor.tag).decode(),
            'algorithm': 'AES-256-GCM'
        }

    def decrypt_data(
        self,
        encrypted_data: Dict[str, str],
        key: Optional[bytes] = None
    ) -> Any:
        """
        Decrypt data encrypted with AES-256-GCM.

        Args:
            encrypted_data: Dictionary containing encrypted data
            key: Decryption key (uses master key if not provided)

        Returns:
            Decrypted data
        """
        if key is None:
            key = self.master_key

        # Decode from base64
        ciphertext = base64.b64decode(encrypted_data['ciphertext'])
        nonce = base64.b64decode(encrypted_data['nonce'])
        tag = base64.b64decode(encrypted_data['tag'])

        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce, tag),
            backend=self.backend
        )
        decryptor = cipher.decryptor()

        # Decrypt
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        # Try to deserialize as JSON, otherwise return as string
        try:
            return json.loads(plaintext.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            return plaintext.decode()

    def encrypt_field(self, field_value: str, field_name: str = '') -> str:
        """
        Encrypt a single field value.

        Args:
            field_value: Value to encrypt
            field_name: Optional field name for key derivation

        Returns:
            Encrypted value as base64 string
        """
        # Use Fernet for simpler field-level encryption
        key = self._get_field_key(field_name)
        f = Fernet(key)
        return f.encrypt(field_value.encode()).decode()

    def decrypt_field(self, encrypted_value: str, field_name: str = '') -> str:
        """
        Decrypt a single field value.

        Args:
            encrypted_value: Encrypted value
            field_name: Optional field name for key derivation

        Returns:
            Decrypted value
        """
        key = self._get_field_key(field_name)
        f = Fernet(key)
        return f.decrypt(encrypted_value.encode()).decode()

    def _get_field_key(self, field_name: str) -> bytes:
        """Get or generate a key for field encryption."""
        if field_name not in self._key_cache:
            # Derive field key from master key
            h = hmac.HMAC(self.master_key, hashes.SHA256(), backend=self.backend)
            h.update(field_name.encode())
            derived = h.finalize()
            # Fernet needs a URL-safe base64-encoded 32-byte key
            self._key_cache[field_name] = base64.urlsafe_b64encode(derived)
        return self._key_cache[field_name]

    def hash_content(self, content: Any) -> str:
        """
        Create a hash of content for integrity verification.

        Args:
            content: Content to hash

        Returns:
            SHA-256 hash as hex string
        """
        if isinstance(content, str):
            data = content.encode()
        else:
            data = json.dumps(content, sort_keys=True).encode()

        return hashlib.sha256(data).hexdigest()

    def sign_data(self, data: Any) -> str:
        """
        Create HMAC signature for data.

        Args:
            data: Data to sign

        Returns:
            HMAC signature as hex string
        """
        if isinstance(data, str):
            message = data.encode()
        else:
            message = json.dumps(data, sort_keys=True).encode()

        h = hmac.HMAC(self.master_key, hashes.SHA256(), backend=self.backend)
        h.update(message)
        return h.finalize().hex()

    def verify_signature(self, data: Any, signature: str) -> bool:
        """
        Verify HMAC signature.

        Args:
            data: Data to verify
            signature: HMAC signature (hex string)

        Returns:
            True if signature is valid
        """
        expected = self.sign_data(data)
        return secrets.compare_digest(expected, signature)


class PrivacyPreservingEncryption:
    """Advanced privacy-preserving encryption techniques."""

    @staticmethod
    def anonymize_pii(text: str) -> str:
        """
        Anonymize personally identifiable information in text.

        Args:
            text: Text containing PII

        Returns:
            Anonymized text
        """
        import re

        # Email addresses
        text = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            '[EMAIL]',
            text
        )

        # Phone numbers (various formats)
        text = re.sub(
            r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
            '[PHONE]',
            text
        )

        # Social Security Numbers
        text = re.sub(
            r'\b\d{3}-\d{2}-\d{4}\b',
            '[SSN]',
            text
        )

        # Credit card numbers
        text = re.sub(
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            '[CREDIT_CARD]',
            text
        )

        # IP addresses
        text = re.sub(
            r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            '[IP_ADDRESS]',
            text
        )

        # Dates (MM/DD/YYYY or MM-DD-YYYY)
        text = re.sub(
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            '[DATE]',
            text
        )

        return text

    @staticmethod
    def tokenize_pii(text: str, token_map: Optional[Dict] = None) -> Tuple[str, Dict]:
        """
        Replace PII with reversible tokens.

        Args:
            text: Text containing PII
            token_map: Optional existing token map

        Returns:
            Tuple of (tokenized_text, token_map)
        """
        import re
        import uuid

        if token_map is None:
            token_map = {}

        def replace_with_token(match):
            value = match.group(0)
            if value not in token_map:
                token_map[value] = f"TOKEN_{uuid.uuid4().hex[:8]}"
            return token_map[value]

        # Email addresses
        text = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            replace_with_token,
            text
        )

        # Names (simplified - would need NER for better results)
        # This is a placeholder - real implementation would use spaCy or similar

        return text, token_map

    @staticmethod
    def differential_privacy_noise(value: float, epsilon: float = 1.0) -> float:
        """
        Add differential privacy noise to a value.

        Args:
            value: Original value
            epsilon: Privacy budget

        Returns:
            Value with added noise
        """
        import numpy as np

        # Add Laplace noise
        sensitivity = 1.0  # Assume normalized data
        scale = sensitivity / epsilon
        noise = np.random.laplace(0, scale)
        return value + noise


class ConsentBasedEncryption:
    """Encryption that respects user consent levels."""

    def __init__(self, encryption_manager: EncryptionManager):
        """
        Initialize consent-based encryption.

        Args:
            encryption_manager: Base encryption manager
        """
        self.encryption = encryption_manager

    def process_data(
        self,
        data: Dict[str, Any],
        consent_level: str
    ) -> Dict[str, Any]:
        """
        Process data based on consent level.

        Args:
            data: Data to process
            consent_level: User's consent level

        Returns:
            Processed data
        """
        if consent_level == 'none':
            # No data storage
            return {}

        elif consent_level == 'metadata_only':
            # Keep only metadata, no content
            return {
                'timestamp': data.get('timestamp'),
                'type': data.get('type'),
                'source': data.get('source'),
                'metadata': {
                    'char_count': len(str(data.get('content', ''))),
                    'has_attachments': bool(data.get('attachments'))
                }
            }

        elif consent_level == 'anonymized':
            # Anonymize PII in content
            anonymized_data = data.copy()
            if 'content' in anonymized_data:
                if isinstance(anonymized_data['content'], str):
                    anonymized_data['content'] = PrivacyPreservingEncryption.anonymize_pii(
                        anonymized_data['content']
                    )
                elif isinstance(anonymized_data['content'], dict):
                    for key, value in anonymized_data['content'].items():
                        if isinstance(value, str):
                            anonymized_data['content'][key] = PrivacyPreservingEncryption.anonymize_pii(value)
            return anonymized_data

        elif consent_level == 'full':
            # Full data with encryption
            encrypted_content = self.encryption.encrypt_data(data.get('content', ''))
            processed_data = data.copy()
            processed_data['content_encrypted'] = encrypted_content
            processed_data['content_hash'] = self.encryption.hash_content(data.get('content', ''))
            # Remove unencrypted content
            if 'content' in processed_data:
                del processed_data['content']
            return processed_data

        else:
            raise ValueError(f"Invalid consent level: {consent_level}")


# Global encryption manager
_encryption_manager = None


def get_encryption_manager() -> EncryptionManager:
    """Get or create the global encryption manager."""
    global _encryption_manager
    if _encryption_manager is None:
        # Get key from environment or generate new one
        master_key = os.getenv('ENCRYPTION_KEY')
        _encryption_manager = EncryptionManager(master_key)
    return _encryption_manager