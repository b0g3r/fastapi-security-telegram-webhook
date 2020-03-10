# fastapi-security-telegram-webhook

Plugin for [FastAPI](https://github.com/tiangolo/fastapi) which allows you secure your Telegram Bot API webhook endpoint
 with IP restriction and optional secret token.
 


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
 - `OnlyTelegramNetworkWithSecret` additionally check secret in path
 
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
