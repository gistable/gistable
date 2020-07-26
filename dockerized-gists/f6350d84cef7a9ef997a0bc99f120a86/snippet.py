from bitmerchant.wallet import Wallet
from mnemonic import Mnemonic

# put in whatever Trezor generates for you here (or backup from this empty/insecure one as a test)
mnemonic = 'clean health food open blood network differ female lion eagle rough upon update zone antique defense venture uncover mobile charge actress film vocal enough'
passphrase = ''  # empty string or whatever you actually choose
path = "m/44'/0'/0'/0/0"  # whatever shows up on the UI for that account (everything will start with m/44'/0' since it's bip44)

child = Wallet.from_main_secret(Mnemonic('english').to_seed(mnemonic, passphrase)).get_child_for_path(path)
child.to_address()  # '18K9axbPpwqZgngB58nuwsYevL2z6ey4YG' (confirm this matches what Trezor is showing you)
child.export_to_wif()  # 'L4orhKxb9YSGRHZvv8th3KeUqRz6x3PPmdqLThajUgSesTovfKPG' (what you can use to spend the funds for the previous address)