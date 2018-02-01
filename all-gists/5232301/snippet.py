# Since I ask this of people before using their code samples, anyone can
# use this under BSD.
import os
import M2Crypto


def empty_callback():
    return

# Seed the random number generator with 1024 random bytes (8192 bits)
M2Crypto.Rand.rand_seed(os.urandom(1024))

# Generate public/private key pair for Alice
print "Generating a 1024 bit private/public key pair for Alice..."
# If you don't like the default M2Crypto ASCII "progress"
# bar it makes when generating keys, you can use:
# Alice = M2Crypto.RSA.gen_key (1024, 65537, empty_callback)
# You can change the key size, though key lengths < 1024 are
# considered insecure
# The larger the key size the longer it will take to generate
# the key and the larger the signature will be when signing
# You should probably leave the public exponent at 65537
# (http://en.wikipedia.org/wiki/Rsa#Key_generation_2)
Alice = M2Crypto.RSA.gen_key(1024, 65537)

# Save Alice's private key
# The 'None' tells it to save the private key in an unencrypted format
# For best security practices, you'd use:
# Alice.save_key ('Alice-private.pem')
# That would cause the private key to be saved in an encrypted format
# Python would ask you to enter a password to use to encrypt the key file
# For a demo script though it's easier/quicker to just use 'None'
Alice.save_key('Alice-private.pem', None)

# Save Alice's public key
Alice.save_pub_key('Alice-public.pem')


# Generate public/private key pair for Bob
print "Generating a 1024 bit private/public key pair for Bob..."
Bob = M2Crypto.RSA.gen_key(1024, 65537)
Bob.save_key('Bob-private.pem', None)
Bob.save_pub_key('Bob-public.pem')


# Alice wants to send a message to Bob, which only Bob will be able to decrypt
# Step 1, load Bob's public key
WriteRSA = M2Crypto.RSA.load_pub_key('Bob-public.pem')
# Step 2, encrypt the message using that public key
# Only Bob's private key can decrypt a message encrypted using Bob's public key
CipherText = WriteRSA.public_encrypt(
    "This is a secret message that can"
    "only be decrypted with Bob's private key",
    M2Crypto.RSA.pkcs1_oaep_padding)
# Step 3, print the result
print "\nAlice's encrypted message to Bob:"
print CipherText.encode('base64')
# Step 4 (optional), sign the message so Bob knows it really was from Alice
# 1) Generate a signature
MsgDigest = M2Crypto.EVP.MessageDigest('sha1')
MsgDigest.update(CipherText)

Signature = Alice.sign_rsassa_pss(MsgDigest.digest())
# 2) Print the result
print "Alice's signature for this message:"
print Signature.encode('base64')


# Bob wants to read the message he was sent
# Step 1, load Bob's private key
ReadRSA = M2Crypto.RSA.load_key('Bob-private.pem')
# Step 2, decrypt the message using that private key
# If you use the wrong private key to try to decrypt the message it
# generates an exception, so this catches the exception
try:
    PlainText = ReadRSA.private_decrypt(
        CipherText, M2Crypto.RSA.pkcs1_oaep_padding)
except:
    print "Error: wrong key?"
    PlainText = ""

if PlainText == "":
    # Step 3, print the result of the decryption
    print "Message decrypted by Bob:"
    print PlainText
    # Step 4 (optional), verify the message was really sent by Alice
    # 1) Load Alice's public key
    VerifyRSA = M2Crypto.RSA.load_pub_key('Alice-public.pem')
    # 2 ) Verify the signature
    print "Signature verificaton:"

    MsgDigest = M2Crypto.EVP.MessageDigest('sha1')
    MsgDigest.update(CipherText)

    if VerifyRSA.verify_rsassa_pss(MsgDigest.digest(), Signature) == 1:
        print "This message was sent by Alice.\n"
    else:
        print "This message was NOT sent by Alice!\n"


# Generate a signature for a string
# Use Bob's private key
SignEVP = M2Crypto.EVP.load_key('Bob-private.pem')
# Begin signing
SignEVP.sign_init()
# Tell it to sign our string
SignEVP.sign_update(
    'This is an unencrypted string that will be signed by Bob')
# Get the final result
StringSignature = SignEVP.sign_final()
# Print the final result
print "Bob's signature for the string:"
print StringSignature.encode('base64')


# Verify the string was signed by Bob
PubKey = M2Crypto.RSA.load_pub_key('Bob-public.pem')
# Initialize
VerifyEVP = M2Crypto.EVP.PKey()
# Assign the public key to our VerifyEVP
VerifyEVP.assign_rsa(PubKey)
# Begin verification
VerifyEVP.verify_init()
# Tell it to verify our string, if this string is not identicial to the
# one that was signed, it will fail
VerifyEVP.verify_update(
    'This is an unencrypted string that will be signed by Bob')
# Was the string signed by Bob?
if VerifyEVP.verify_final(StringSignature) == 1:
    print "The string was successfully verified."
else:
    print "The string was NOT verified!"
