wallets = {}

def add_wallet(admin_id, mnemonic):
    wallets[admin_id] = mnemonic

def remove_wallet(admin_id):
    wallets.pop(admin_id, None)

def get_all_wallets():
    return wallets.items()
