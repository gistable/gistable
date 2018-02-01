#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib as hasher
import datetime as date


class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    def hash_block(self):
        sha = hasher.sha256()
        sha.update("%s%s%s%s" % (self.index, self.timestamp, self.data, self.previous_hash))
        return sha.hexdigest()

    def __str__(self):
        return "Block <%s>: %s" % (self.hash, self.data)


class SampleCoin(object):
    blockchain = [Block(0, date.datetime.now(), "Genesis Block", "0")]

    def add_block(self, data):
        new_block = Block(
            self.blockchain[-1].index + 1,
            date.datetime.utcnow(),
            data,
            self.blockchain[-1].hash
        )
        self.blockchain.append(new_block)
        return new_block


def main():
    snake_coin = SampleCoin()

    # Add 20 blocks to the chain
    for i in range(20):
        block = snake_coin.add_block("Hey! I'm block #%s" % i)
        # Tell everyone about it!
        print("Block #{} has been added to the blockchain!".format(block.index))
        print("Hash: {}\n".format(block.hash))

    print(snake_coin.blockchain[-1])  # show last block


if __name__ == '__main__':
    main()
