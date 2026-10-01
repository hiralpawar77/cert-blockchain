import hashlib
import time
import sqlite3
DB_NAME = "blockchain.db"
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blocks (
            idx INTEGER PRIMARY KEY,
            timestamp REAL,
            cert_hash TEXT,
            previous_hash TEXT,
            hash TEXT
        )
    ''')
    conn.commit()
    conn.close()
class Block:
    def __init__(self, index, timestamp, cert_hash, previous_hash, current_hash=None):
        self.index = index
        self.timestamp = timestamp
        self.cert_hash = cert_hash
        self.previous_hash = previous_hash
        self.hash = current_hash if current_hash else self.calculate_hash()
    def calculate_hash(self):
        block_string = f"{self.index}{self.timestamp}{self.cert_hash}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()
class Blockchain:
    def __init__(self):
        init_db()
        if len(self.get_all_blocks()) == 0:
            self.create_genesis_block()
    def create_genesis_block(self):
        genesis = Block(0, time.time(), "GENESIS_HASH", "0")
        self.save_block_to_db(genesis)
    def save_block_to_db(self, block):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO blocks (idx, timestamp, cert_hash, previous_hash, hash)
            VALUES (?, ?, ?, ?, ?)
        ''', (block.index, block.timestamp, block.cert_hash, block.previous_hash, block.hash))
        conn.commit()
        conn.close()
    def get_all_blocks(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT idx, timestamp, cert_hash, previous_hash, hash FROM blocks ORDER BY idx ASC')
        rows = cursor.fetchall()
        conn.close()
        blocks = []
        for r in rows:
            blocks.append(Block(r[0], r[1], r[2], r[3], r[4]))
        return blocks
    def get_latest_block(self):
        blocks = self.get_all_blocks()
        return blocks[-1] if blocks else None
    def add_certificate(self, cert_hash):
        latest_block = self.get_latest_block()
        new_index = latest_block.index + 1
        new_block = Block(new_index, time.time(), cert_hash, latest_block.hash)
        self.save_block_to_db(new_block)
        return new_block
    def is_chain_valid(self):
        blocks = self.get_all_blocks()
        for i in range(1, len(blocks)):
            current = blocks[i]
            previous = blocks[i - 1]
            if current.hash != current.calculate_hash():
                return False, f"Block {current.index} data has been tampered!"
            if current.previous_hash != previous.hash:
                return False, f"Block {current.index} previous hash link broken!"
        return True, "Blockchain is valid and secure."