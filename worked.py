import base64
import hashlib
import random

class CustomCryptoDecrypt:
    def __init__(self, master_key: str):
        self.master_key = master_key.encode()
        self.key_hash = hashlib.sha256(self.master_key).digest()
        self.key_seed = int.from_bytes(self.key_hash[:4], 'little') % 1000000

    def _generate_substitution_table(self, seed: int):
        random.seed(seed)
        table = list(range(256))
        random.shuffle(table)
        return table

    def _generate_inverse_substitution_table(self, seed: int):
        table = self._generate_substitution_table(seed)
        inverse_table = [0] * 256
        for i, val in enumerate(table):
            inverse_table[val] = i
        return inverse_table

    def _bit_rotate(self, value: int, amount: int) -> int:
        return ((value << amount) | (value >> (8 - amount))) & 0xFF

    def _custom_xor(self, data: bytes, key: bytes) -> bytes:
        result = bytearray()
        key_len = len(key)
        for i, byte in enumerate(data):
            key_byte = key[i % key_len]
            rotated_key = self._bit_rotate(key_byte, (i % 7) + 1)
            result.append(byte ^ rotated_key)
        return bytes(result)

    def _layer2_xor(self, data: bytes, nonce: int) -> bytes:
        nonce_bytes = nonce.to_bytes(8, 'little')
        extended_nonce = (nonce_bytes * (len(data) // 8 + 1))[:len(data)]
        return self._custom_xor(data, extended_nonce)

    def _layer3_permutation(self, data: bytes, key_hash: bytes) -> bytes:
        result = bytearray()
        key_len = len(key_hash)
        for i, byte in enumerate(data):
            result.append(byte ^ key_hash[i % key_len])
        return bytes(result)

    def _layer1_substitution_inverse(self, data: bytes, seed: int) -> bytes:
        inverse_table = self._generate_inverse_substitution_table(seed)
        return bytes(inverse_table[b] for b in data)

    def decrypt(self, encrypted_data: str, time_seed: int) -> bytes:
        # Слой 4: декодируем из base64
        data = base64.b64decode(encrypted_data)
        # Слой 3: обратный (XOR с key_hash)
        data = self._layer3_permutation(data, self.key_hash)
        # Слой 2: обратный (XOR с nonce = time_seed)
        data = self._layer2_xor(data, time_seed)
        # Слой 1: обратная подстановка
        data = self._layer1_substitution_inverse(data, self.key_seed)
        return data

# Данные из задания
master_key = "ctfcup_master_key_0x1337"
encrypted_data = "HNzfqswupoO5eyhbKlOe/f6yLnlbjtaY+me+3SkoDoNOzHWDJdD4NOMOFeuyoOmrb4q2XnQWyZguzD+c"

crypto = CustomCryptoDecrypt(master_key)

# Перебираем возможные значения time_seed
for time_seed in range(0, 100000):
    try:
        decrypted = crypto.decrypt(encrypted_data, time_seed)
        if decrypted.startswith(b'Your flag is: ctfcup{'):
            print(f"Found time_seed: {time_seed}")
            print(decrypted.decode())
            break
    except:

        pass
