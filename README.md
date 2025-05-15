# Pi Wallet Security Bot

A Telegram bot to monitor Pi Network wallets and automatically transfer funds to a secure address if compromised.

## Features
- Add/Remove wallet by admin via Telegram
- Constant monitoring (~500ms) for new funds
- monitor transactions

## Deployment on Render
1. Create a new Web Service on https://dashboard.render.com/
2. Connect to your GitHub repo
3. Use `render.yaml` as deployment config
4. Add environment variables:
   - `BOT_TOKEN`: your Telegram bot token
   - `DESTINATION_WALLET`: secure address
   - `POLLING_INTERVAL_MS`: e.g. 500
5. Deploy and monitor logs

> **Note**: Do not commit your `.env` file. Use Render's environment settings.

