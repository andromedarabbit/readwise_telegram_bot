![build](https://github.com/andromedarabbit/readwise_telegram_bot/workflows/build/badge.svg)
![dockerimage](https://github.com/andromedarabbit/readwise_telegram_bot/workflows/dockerimage/badge.svg)

# Telegram Bot for ReadWise

Telegram bot for https://readwise.io

## How to Run?

```bash
pip install -r ./requirements.txt
python ./app.py
```

You can deploy this bot [anywhere](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Where-to-host-Telegram-Bots).
## How It Works?
```mermaid
sequenceDiagram
    User->>+TelegramBot: Forwards post to highlight it
    TelegramBot->>+ReadWise API: Using ReadWise API token sends post text and link to the ReadWise
    TelegramBot-->>-User: Responses "Message from channel was highlighted"
```

## Features

1. Forward post from someone or some channel in Telegram and this bot will the post to the ReadWise Reader. 
2. Add *a* commentary to the forwarded post to send text and link (and the first link in the post itself) to ReadWise.

## Security considerations

1. To make this bot work you have to provide to the bot ReadWise API token.
2. Because I don't want to store your tokens, you have to set up a separate bot for yourself.
3. From my perspective Telegram Bot API doesn't provide secure way to store sensitive data, that is why you have to [create your own bot](https://core.telegram.org/bots/features#botfather). 

