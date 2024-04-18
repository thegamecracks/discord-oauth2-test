import os
import secrets
import time
from dataclasses import dataclass
from typing import Iterable

import discord
import httpx
from starlette.requests import Request
from starlette.responses import JSONResponse

CLIENT_ID = os.environ["CLIENT_ID"]
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
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
            },
        )
        response.raise_for_status()


auth_flow = AuthorizationFlow()
