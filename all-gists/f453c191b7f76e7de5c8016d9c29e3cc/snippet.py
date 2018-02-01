class Blockchain(object):
    def __init__(self):
        self.current_transactions = []
        self.chain = []

    def new_block(self):
        # Creates a new Block in the Blockchain
        pass

    def new_transaction(self):
        # Creates a new transaction to go into the next mined Block
        pass

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        # Creates the hash of a Block
        pass