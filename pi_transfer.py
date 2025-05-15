import requests
from mnemonic import Mnemonic
from stellar_sdk import Keypair, Server, TransactionBuilder, Network
import time

HORIZON_URL = "https://api.testnet.minepi.com"
server = Server(horizon_url=HORIZON_URL)

DESTINATION_WALLET = "GXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

class PiWallet:
    def __init__(self, mnemonic_phrase):
        self.mnemonic_phrase = mnemonic_phrase
        self.keypair = self._generate_keypair()
        self.public_key = self.keypair.public_key
        self.secret = self.keypair.secret

    def _generate_keypair(self):
        mnemo = Mnemonic("english")
        seed = mnemo.to_seed(self.mnemonic_phrase)
        keypair = Keypair.from_secret_seed(seed[:32])
        return keypair

    def get_address(self):
        return self.public_key

    def get_balance(self):
        try:
            account = server.accounts().account_id(self.public_key).call()
            for balance in account["balances"]:
                if balance["asset_type"] == "native":
                    return float(balance["balance"])
        except Exception as e:
            print(f"Error fetching balance: {e}")
        return 0.0

    def send_all_funds(self, destination_wallet):
        try:
            balance = self.get_balance()
            if balance <= 0:
                return False, "No funds to transfer."

            account = server.load_account(self.public_key)
            transaction = (
                TransactionBuilder(
                    source_account=account,
                    network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                    base_fee=100
                )
                .add_text_memo("Auto-transfer by security bot")
                .append_payment_op(destination=destination_wallet, amount=str(balance), asset_code="XLM")
                .set_timeout(30)
                .build()
            )
            transaction.sign(self.keypair)
            response = server.submit_transaction(transaction)
            return True, f"Transferred {balance} Pi. TX hash: {response['hash']}"

        except Exception as e:
            return False, f"Transfer failed: {e}"

if __name__ == "__main__":
    mnemonic = "example seed phrase goes here..."
    wallet = PiWallet(mnemonic)
    success, message = wallet.send_all_funds(DESTINATION_WALLET)
    print(message)
