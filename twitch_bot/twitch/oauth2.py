from urllib.parse import quote_plus
import requests
from getpass import getpass
import webbrowser
import datetime
from twitch_bot.auth.auth import (
    get_random_string,
    is_expired,
)
from twitch_bot.data.consts import KEYRING_SERVICE
from twitch_bot.data.logger import logger
from twitch_bot.auth.models import TwitchApp, TwitchToken
import keyring
import json

TWITCH_OAUTH_URI = "https://id.twitch.tv/oauth2"


def _get_auth_uri(twitch_app: TwitchApp, api_state: str):
    # https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/#authorization-code-grant-flow
    auth_uri = f"\
    {TWITCH_OAUTH_URI}/authorize\
    ?response_type=code\
    &client_id={twitch_app.client}\
    &redirect_uri={twitch_app.endpoint}\
    &scope={quote_plus(twitch_app.scope)}\
    &state={api_state}\
    ".replace(
        " ", ""
    )
    return auth_uri


def _get_auth_code(twitch_app: TwitchApp) -> str:
    api_state = get_random_string(32)
    auth_uri = _get_auth_uri(
        twitch_app=twitch_app,
        api_state=api_state,
    )

    webbrowser.open_new_tab(auth_uri)
    uri = getpass(prompt="Enter the redirect URL: ")
    return _parse_auth_uri(twitch_app, uri, api_state)


def _parse_auth_uri(twitch_app: TwitchApp, uri: str, api_state: str) -> str:
    try:
        uri_parts = uri.split("?")
        redirect_uri = uri_parts[0]
        redirect_vars = uri_parts[-1]
        ret_auth_vars = redirect_vars.split("&")
        auth = {}
        for ret_auth_var in ret_auth_vars:
            key_value = ret_auth_var.split("=")
            k = key_value[0]
            v = key_value[-1]
            auth[k] = v
        if redirect_uri.strip("/") != twitch_app.endpoint.strip("/"):
            logger.error("[twitch-oauth] Redirect URL was altered")
        if auth["scope"] != quote_plus(twitch_app.scope):
            logger.error("[twitch-oauth] Scope was altered")
        if auth["state"] != api_state:
            logger.error("[twitch-oauth] State was altered")
        twitch_auth_code = auth["code"]
    except KeyError:
        twitch_auth_code = None
    return twitch_auth_code


def get_twitch_app() -> TwitchApp:
    webbrowser.open_new_tab("https://dev.twitch.tv/console/apps")
    default_oauth_redirect_url = "http://localhost"
    default_api_scope = [
        "chat:edit",
        "chat:read",
        "bits:read",
        "channel:read:redemptions",
        "channel:read:subscriptions",
        "channel:moderate",
        "whispers:read",
    ]
    default_api_scope_str = " ".join(default_api_scope)
    oauth_redirect_url = input(f"OAuth Redirect URL ({default_oauth_redirect_url}): ").strip()
    if not oauth_redirect_url:
        oauth_redirect_url = default_oauth_redirect_url
    client_id = input("Client ID: ").strip()
    client_secret = getpass(prompt="Client Secret: ").strip()
    api_scope = input(f'Scope ({default_api_scope_str}): ').strip()
    if not api_scope:
        api_scope = default_api_scope_str
    twitch_app = TwitchApp(
        client=client_id,
        secret=client_secret,
        endpoint=oauth_redirect_url,
        scope=api_scope,
    )
    return twitch_app

def get_twitch_token(twitch_app: TwitchApp, twitch_token: TwitchToken = None):
    
    if not twitch_token:
        grant_type = "authorization_code"
    elif twitch_token.refresh_token:
        grant_type = "refresh_token"
    else:
        grant_type = "client_credentials"

    body = {
        "client_id": twitch_app.client,
        "client_secret": twitch_app.secret,
        "grant_type": grant_type,
    }
    
    if grant_type == "refresh_token":
        auth_type = "refresh_token"
        auth_value = twitch_token.refresh_token
        body[auth_type] = auth_value
    elif grant_type == "authorization_code":
        auth_type = "code"
        auth_value = _get_auth_code(twitch_app)
        body[auth_type] = auth_value
        body["redirect_uri"] = twitch_app.endpoint

    _time = datetime.datetime.now()
    response = requests.post(f"{TWITCH_OAUTH_URI}/token", body)
    response_data = response.json()
    if response_data.get("access_token"):
        twitch_token = TwitchToken(
            access_token=response_data["access_token"],
            refresh_token=response_data.get("refresh_token"),
            expires_on=str(_time + datetime.timedelta(0, response_data["expires_in"])),
        )
        return twitch_token
    
    logger.error(f"[twitch-oauth] > {response_data}")
    return None
