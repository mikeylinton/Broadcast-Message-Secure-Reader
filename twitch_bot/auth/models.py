from pydantic import BaseModel


class TwitchApp(BaseModel):
    client: str
    secret: str
    endpoint: str
    scope: str

class TwitchToken(BaseModel):
    access_token: str
    refresh_token: str
    expires_on: str