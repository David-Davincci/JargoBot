import asyncio
import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from wallet_manager import add_wallet, remove_wallet
from scheduler import monitor_wallets

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to JargoBot. Use /add to connect wallet.")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Send your wallet mnemonic: /add <your 12-word seed>")
    mnemonic = " ".join(context.args)
    admin_id = update.effective_user.id
    add_wallet(admin_id, mnemonic)
    await update.message.reply_text("Wallet connected and will be monitored.")

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    remove_wallet(admin_id)
    await update.message.reply_text("Wallet disconnected.")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("remove", remove))

    asyncio.create_task(monitor_wallets())
    await app.run_polling()

if __name__ == "__main__":
    import asyncio

    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "already running" in str(e):
            loop = asyncio.get_event_loop()
            loop.create_task(main())
            loop.run_forever()
        else:
            raise

