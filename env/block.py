
class Block:
    def __init__(self, size=0):
        self._size = size
        self._transactions = []

    @property
    def size(self):
        return self._size

    @property
    def transactions(self):
        return self._transactions

    def set_size(self, size):
        self._size = size

    def add_transaction(self, transaction):
        self._transactions.append(transaction)

