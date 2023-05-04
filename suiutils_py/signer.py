import base64
import hashlib
import nacl.signing

SigFlagEd25519 = 0x00
SigFlagSecp256k1 = 0x01

class TxnMetaData:
    def __init__(self, tx_bytes: bytes) -> None:
        self.TxBytes = tx_bytes

    def SignSerializedSigWith(self, private_key: bytes) -> 'SignedTransactionSerializedSig':
        tx_bytes = base64.b64decode(self.TxBytes)
        message = self.messageWithIntent(tx_bytes)
        digest = hashlib.blake2b(message, digest_size=32).digest()
        signing_key = nacl.signing.SigningKey(private_key)
        signed = signing_key.sign(digest)
        return SignedTransactionSerializedSig(self.TxBytes, self.toSerializedSignature(signed.signature, signing_key.verify_key.encode()))

    def messageWithIntent(self, message: bytes) -> bytes:
        intent = bytes([0, 0, 0])
        intent_message = intent + message
        return intent_message

    def toSerializedSignature(self, signature: bytes, pub_key: bytes) -> str:
        serialized_signature = bytearray([SigFlagEd25519]) + signature + pub_key
        return base64.b64encode(serialized_signature).decode()

class SignedTransactionSerializedSig:
    def __init__(self, tx_bytes: bytes, signature: str) -> None:
        self.TxBytes = tx_bytes
        self.Signature = signature
