import hashlib

MINING_DIFFICULTY = 3


def mine_block(hash_data):

    nonce = 0

    while True:
        s = hashlib.sha256()
        hash_string = hash_data + str(nonce)
        binary_string = hash_string.encode()
        s.update(binary_string)
        block_hash = s.hexdigest()

        if block_hash[:MINING_DIFFICULTY] == "0" * MINING_DIFFICULTY:
            print(block_hash, nonce)
            return {"nonce": nonce, "block_hash": block_hash}
        nonce += 1
