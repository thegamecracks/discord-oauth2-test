import contextlib
import time
from contextvars import ContextVar
from typing import AsyncGenerator, Self, cast

import asyncpg

_current_conn: ContextVar[asyncpg.Connection] = ContextVar("_current_conn")


class DatabaseClient:
    """Provides an API for making common queries with an :class:`asyncpg.Pool`."""

    def __init__(self, pool: asyncpg.Pool) -> None:
        self.pool = pool

    @property
    def conn(self) -> asyncpg.Connection:
        """Returns the current connection used by the query client.

        This is set by the :meth:`acquire()` method on a per-context basis.

        """
        try:
            return _current_conn.get()
        except LookupError:
            raise RuntimeError(
                "acquire() async context manager must be entered before "
                "running SQL statements"
            ) from None

    @contextlib.asynccontextmanager
    async def acquire(self, *, transaction: bool = True) -> AsyncGenerator[Self, None]:
        """Acquires a connection from the pool to be used by the client.

        :param transaction: If True, a transaction is opened as well.

        """
        async with self.pool.acquire() as conn:
            conn = cast(asyncpg.Connection, conn)

            if transaction:
                transaction_manager = conn.transaction()
            else:
                transaction_manager = contextlib.nullcontext()

            async with transaction_manager:
                token = _current_conn.set(conn)
                try:
                    yield self
                finally:
                    _current_conn.reset(token)

    async def add_user(self, user_id: int) -> None:
        await self.conn.execute(
            "INSERT INTO discord_user (id) VALUES ($1) ON CONFLICT DO NOTHING",
            user_id,
        )

    async def add_discord_oauth(
        self,
        user_id: int,
        *,
        access_token: str,
        token_type: str,
        expires_in: int,
        refresh_token: str | None,
        scope: str,
    ) -> None:
        expires_at = int(time.time() + expires_in)
        await self.add_user(user_id)
        await self.conn.execute(
            "INSERT INTO discord_oauth (user_id, access_token, token_type, "
            "expires_at, refresh_token, scope) VALUES ($1, $2, $3, $4, $5, $6)",
            user_id,
            access_token,
            token_type,
            expires_at,
            refresh_token,
            scope,
        )
