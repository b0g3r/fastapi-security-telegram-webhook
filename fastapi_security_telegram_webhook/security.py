from secrets import compare_digest
from ipaddress import (
    IPv4Network,
    IPv4Address,
)
from typing import (
    Optional,
    Sequence,
)

from fastapi import (
    Path,
    HTTPException,
)
from fastapi.openapi.models import HTTPBase
from fastapi.security.base import SecurityBase
from starlette.requests import Request

# Source: https://core.telegram.org/bots/webhooks#the-short-version
DEFAULT_NETWORKS = [IPv4Network("149.154.160.0/20"), IPv4Network("91.108.4.0/22")]
SECRET_PATH_PARAM = Path(
    ...,
    alias="secret",
    description="Secret token, should be placed as `{secret}` in path operation function",
)


def check_secret(request_secret: str, real_secret: str) -> None:
    """
    Compare secrets with safe method.

    :raises: HTTPException
    """
    if not compare_digest(request_secret, real_secret):
        raise HTTPException(status_code=403)


def check_ip(request_ip: IPv4Address, telegram_networks: Sequence[IPv4Network]) -> None:
    """
    Check that request was from telegram networks.

    :raises: HTTPException
    """
    if not any(request_ip in network for network in telegram_networks):
        raise HTTPException(status_code=403, detail="Bad IP address")


def convert_to_ip(request_host: Optional[str]) -> IPv4Address:
    """
    Convert request host name to IP object.

    :raises: HTTPException
    """
    if request_host is None:
        raise HTTPException(status_code=500, detail="IP address cannot be empty")
    return IPv4Address(request_host)


class OnlyTelegramNetwork(SecurityBase):
    """
    Secure telegram webhook, validate that request was made from one of telegram subnets.
    """

    scheme_name = "only_telegram_network"
    model = HTTPBase(
        scheme=scheme_name,
        description="Your request should be permitted from Telegram subnet",
    )

    def __init__(
        self, *, telegram_networks: Optional[Sequence[IPv4Network]] = None,
    ):
        if telegram_networks is None:
            telegram_networks = DEFAULT_NETWORKS
        self.telegram_networks = telegram_networks

    def __call__(self, request: Request) -> None:
        """
        :raises: HTTPException
        """
        request_host: Optional[str] = request.client.host
        request_ip = convert_to_ip(request_host)
        check_ip(request_ip, self.telegram_networks)


class OnlyTelegramNetworkWithSecret(SecurityBase):
    """
    Secure telegram webhook, validate that request was made from one of telegram subnets and contains
    correct `secret` in path.

    If you use this type of security, please, add correspond `{secret}` in path operation function.

    Check example:
    >>> from fastapi import FastAPI, Depends, Body
    ... app = FastAPI()
    ... webhook_security = OnlyTelegramNetworkWithSecret(real_secret="your-secret-from-config-or-env")
    ...
    ... # {secret} in path and OnlyTelegramNetworkWithSecret as dependency:
    ... @app.post('/webhook/{secret}', dependencies=[Depends(webhook_security)])
    ... def process_telegram_update(update_raw = Body(...)):
    ...     ...
    """

    scheme_name = "only_telegram_network_with_secret"
    model = HTTPBase(
        scheme=scheme_name,
        description="You should pass the 'secret' value in the path and request "
        "should be permitted from Telegram subnet",
    )

    def __init__(
        self,
        *,
        real_secret: str,
        telegram_networks: Optional[Sequence[IPv4Network]] = None,
    ):
        self.real_secret = real_secret
        if telegram_networks is None:
            telegram_networks = DEFAULT_NETWORKS
        self.telegram_networks = telegram_networks

    def __call__(
        self, request: Request, request_secret: str = SECRET_PATH_PARAM
    ) -> None:
        """
        :raises: HTTPException
        """
        request_host: Optional[str] = request.client.host
        request_ip = convert_to_ip(request_host)
        check_ip(request_ip, self.telegram_networks)
        check_secret(request_secret, self.real_secret)
