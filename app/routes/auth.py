import os
import secrets
import time
from dataclasses import dataclass
from typing import Iterable

import discord
import httpx
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.constants import DISCORD_BASE_URL
from app.database import DatabaseClient

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ.pop("CLIENT_SECRET")
REDIRECT_URI = os.environ["REDIRECT_URI"]


@dataclass(kw_only=True)
class AuthorizationLink:
    state: str
    expires_at: float

    def is_valid(self) -> bool:
        return time.monotonic() < self.expires_at


class AuthorizationFlow:
    def __init__(self, *, expires_after: float = 600) -> None:
        self.expires_after = expires_after
        self._links: dict[str, AuthorizationLink] = {}

    def _create_state(self) -> str:
        state = secrets.token_hex(16)
        while state in self._links:
            state = secrets.token_hex(16)
        return state

    def create_oauth_url(
        self,
        *,
        scopes: Iterable[str] = ("identify", "guilds"),
        state: str | None = None,
    ) -> str:
        state = state or self._create_state()
        assert state not in self._links

        self._links[state] = AuthorizationLink(
            state=state,
            expires_at=time.monotonic() + self.expires_after,
        )

        return discord.utils.oauth_url(
            CLIENT_ID,
            redirect_uri=REDIRECT_URI,
            scopes=scopes,
            state=state,
        )

    def is_valid_state(self, state: str) -> bool:
        link = self._links.get(state)
        return link is not None and link.is_valid()

    async def exchange_token(self, request: Request) -> JSONResponse:
        code = request.query_params["code"]
        state = request.query_params["state"]

        if not self.is_valid_state(state):
            return JSONResponse({"error": "invalid state"}, status_code=400)

        client: httpx.AsyncClient = request.state.http_client
        response = await client.post(
            "https://discord.com/api/oauth2/token",
            auth=(CLIENT_ID, CLIENT_SECRET),
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
            },
        )
        response.raise_for_status()

        data = response.json()
        access_token: str = data["access_token"]
        token_type: str = data["token_type"]
        expires_in: int = data["expires_in"]
        refresh_token: str = data["refresh_token"]
        scope: str = data["scope"]

        response = await client.get(
            DISCORD_BASE_URL + "/users/@me",
            headers={"Authorization": f"{token_type} {access_token}"},
        )
        response.raise_for_status()
        user = response.json()

        async with DatabaseClient(request.state.pool).acquire() as query:
            await query.add_discord_oauth(
                user["id"],
                access_token=access_token,
                token_type=token_type,
                expires_in=expires_in,
                refresh_token=refresh_token,
                scope=scope,
            )

        del self._links[state]

        return JSONResponse("Successfully authorized!")


auth_flow = AuthorizationFlow()
