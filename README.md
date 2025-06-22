# TheBonimBot

Telegram bot for order management

## Installation

1. Install dependencies: `pip install -r requirements.txt`
2. Set BOT_TOKEN in .env file
3. Run: `python main.py`

## Features

- Order management
- Group limit control (configurable)
- Hebrew interface
- Payment tracking

## Configuration

- To change the maximum number of groups the bot can be active in simultaneously, edit the `MAX_ACTIVE_GROUPS` variable in `main.py`.

## Example .env file

```
BOT_TOKEN=your-telegram-bot-token-here
```

## Example Usage

- Start the bot in a group or private chat.
- Follow the instructions in Hebrew to place an order.
- If the group limit is reached, the bot will notify you.
