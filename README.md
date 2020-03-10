# fastapi-security-telegram-webhook

Plugin for [FastAPI](https://github.com/tiangolo/fastapi) which allows you to secure your Telegram Bot API webhook
 endpoint with IP restriction and an optional secret token.

Telegram provides two ways of getting updates: long polling and webhook. When you use webhook you just register
endpoint address and telegram sends JSON to this address. If the bad guy finds out the address of your webhook, then
he can send fake "telegram updates" to your bot.

Telegram doesn't provide any security features like signing or authentication mechanisms, so securing webhook is a task
for a bot developer.

Thence, for securing your webhook you have only two option:
 - Allow requests only from Telegram subnets. 
 [Telegram assures](https://core.telegram.org/bots/webhooks#the-short-version) that they won't change.
 - Use secret value in endpoint address, e.g. `/telegram-webhook/468e95826f224a60a4e9355ab76e0875`. It will
  complicate the brute force attack and you can easily change it if the value was compromised.

This little plugin allows you to use both ways to secure.

## How to use

Use pip or another package management util:
```bash
pip install fastapi-security-telegram-webhook
```

or

```bash
poetry add fastapi-security-telegram-webhook
```

or

```bash
pipenv install fastapi-security-telegram-webhook
```

Package contains two Security objects: 
 - `OnlyTelegramNetwork` allows request only from telegram subnets
 - `OnlyTelegramNetworkWithSecret` additionally checks secret in path
 
Example with `OnlyTelegramNetworkWithSecret`. Pay attention to `{secret}` in path operation, it's required

```python
from fastapi import FastAPI, Body, Depends
from fastapi_security_telegram_webhook import OnlyTelegramNetworkWithSecret

app = FastAPI()
webhook_security = OnlyTelegramNetworkWithSecret(real_secret="your-secret-from-config-or-env")

# {secret} in path and OnlyTelegramNetworkWithSecret as dependency:
@app.post('/webhook/{secret}', dependencies=[Depends(webhook_security)])
def process_telegram_update(update_raw = Body(...)):
   ...

```

## Use behind proxy

The plugin uses `starlette.Request.client.host` for extracting IP address of the request, so if your web-app is
behind proxy you should pass the real IP to the app.

For `uvicorn` you can use `--proxy-headers` as it describes in 
[documentation](https://www.uvicorn.org/deployment/#running-behind-nginx).  