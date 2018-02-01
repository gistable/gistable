# Example of stealth addressess using Diffie-Hellman, to create a unique offset between 2 mpks
# doesn't need to exchange data in the blockchain. Payee can just look for new transactions against their
# mpk at offset S, where S is the shared secret between the two parties.

import obelisk
import os
from ecdsa import numbertheory, curves, util, ellipticcurve

# From https://github.com/FelixWeis/python-hdwallet/blob/master/hdwallet/hdwallet.py
def point_decompress(data):
    prefix = data[0]
    curve = curves.SECP256k1.curve

    if prefix == '\x04':
        return data

    assert(prefix in ['\x02', '\x03', '\x04'])
    parity = 1 if prefix == '\x02' else -1

    x = util.string_to_number(data[1:])

    y = numbertheory.square_root_mod_prime( 
        ( x * x * x + curve.a() * x + curve.b() ) % curve.p(),  curve.p()
        )

    y = parity * y % curve.p()
    return ellipticcurve.Point(curve, x, y)


def diffie_hellman(e, Q):
    point = point_decompress(Q)

    e_int = obelisk.string_to_number(e)
    point = e_int * point
    # convert x point to bytes
    result = "\x03" + ("%x" % point.x()).decode("hex")
    assert len(result) == 33
    return result


def test_stealth(bob_seed, alice_seed):

	# Sequence could be anything, ideally it's common and well known, like the root.
	# User could use their branches to create alternate identities, 
	# but they'd then have to remember the sequence along with the seed

    bob_wallet = obelisk.HighDefWallet.root(bob_seed)
    alice_wallet = obelisk.HighDefWallet.root(alice_seed)

    bob_secret = bob_wallet.secret
    alice_secret = alice_wallet.secret

    bob_mpk = bob_wallet.mpk_compressed
    alice_mpk = alice_wallet.mpk_compressed

    bob_mpk_uncompressed = bob_wallet.mpk
    alice_mpk_uncompressed = alice_wallet.mpk

    bob_chain = bob_wallet.chain
    alice_chain = alice_wallet.chain

    print "Bob secret", bob_secret.encode("hex")
    print "Alice secret", alice_secret.encode("hex")
    print "\n"

    print "Bob mpk (compressed)", bob_mpk.encode("hex")
    print "Alice mpk (compressed)", alice_mpk.encode("hex")
    print "\n"

    print "Bob chain", bob_chain.encode("hex")
    print "Alice chain", alice_chain.encode("hex")
    print "\n"

    # Trade mpks now over the internet/telegram whatever. 

    # Calculate shared secret S. 
    # Bob S = bob_secret * alice_mpk
    # Alice S = alice_secret * bob_mpk

    bob_shared_secret = diffie_hellman(bob_secret, alice_mpk)
    alice_shared_secret = diffie_hellman(alice_secret, bob_mpk)

    assert(bob_shared_secret == alice_shared_secret)

    print "Bob Shared secret", bob_shared_secret.encode("hex")
    print "Alice Shared secret", alice_shared_secret.encode("hex")
    print "\n"

    # Since the secret is unique to both we can use it as the initial offset and then use a value n 
    # for every subsequent payment to each person to maintain anonymity, or breaking another chain from the hd wallet


    # secret_int is the first 20 bytes of the shared_secret converted to an integer
    secret_int = long(bob_shared_secret[0:20].encode("hex"), base=16)

    # Shared branches, create a new branch every 2 bytes.
    # up to 20 bytes of entropy, dont want to create too many unncesessary branches.
    sequence = []

    for i in range(10):
    	next_sequence = long(bob_shared_secret[i*2: (i*2)+2].encode("hex"), base=16)
    	sequence.append(next_sequence)


    print "shared secret sequence", sequence


    bob_wallet_branched = bob_wallet
    alice_wallet_branced = alice_wallet

    for s in sequence:
    	bob_wallet_branched = bob_wallet_branched.branch(s)
    	alice_wallet_branced = alice_wallet_branced.branch(s)


    bob_sequence_to_alice = obelisk.BIP32Sequence((alice_mpk_uncompressed.encode("hex"), alice_chain.encode("hex")))
    alice_sequence_to_bob = obelisk.BIP32Sequence((bob_mpk_uncompressed.encode("hex"), bob_chain.encode("hex")))

    print "\nAlice sends to Bob (Only Bob knows the private keys)"

    for i in range(10):
    	print "Alice sends to  \t", alice_sequence_to_bob.get_address(sequence + [i])
    	print "Bob receives to \t", bob_wallet_branched.branch(i).address

    	assert(alice_sequence_to_bob.get_address(sequence + [i]) == bob_wallet_branched.branch(i).address)


    print "\nBob sends to Alice (Only Alice knows the private keys)"

    for i in range(10):
    	print "Bob sends to      \t", bob_sequence_to_alice.get_address(sequence + [i])
    	print "Alice receives to \t", alice_wallet_branced.branch(i).address

    	assert(bob_sequence_to_alice.get_address(sequence + [i]) == alice_wallet_branced.branch(i).address)


def exhaustive_test(iterations=50):
    for i in range(iterations):

        print "\n\nIteration", i

        bob_seed = os.urandom(20).encode("hex")
        alice_seed = os.urandom(20).encode("hex")

        test_stealth(bob_seed, alice_seed)

if __name__ == "__main__":
    bob_seed = "000102030405060708090a0b0c0d0e0f"
    alice_seed = "fffcf9f6f3f0edeae7e4e1dedbd8d5d2cfccc9c6c3c0bdbab7b4b1aeaba8a5a29f9c999693908d8a8784817e7b7875726f6c696663605d5a5754514e4b484542"

    # test_stealth(bob_seed, alice_seed)

    exhaustive_test()


