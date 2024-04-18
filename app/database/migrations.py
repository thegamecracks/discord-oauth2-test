import logging
import re
from pathlib import Path

import asyncpg

log = logging.getLogger(__name__)

APP_ID = 1
APP_VERSION_SCHEMA = """
CREATE TABLE IF NOT EXISTS app_version (
    id INTEGER PRIMARY KEY,
    version INTEGER
);
"""


async def run_migrations(conn: asyncpg.Connection):
    await conn.execute(APP_VERSION_SCHEMA)
    version: int | None = await conn.fetchval(
        "SELECT version FROM app_version WHERE id = $1",
        APP_ID,
    )
    version = version or 0
    script_version = version

    for script_version, script in _get_migrations(version).items():
        await conn.execute(script)

    if script_version > version:
        await conn.execute(
            "INSERT INTO app_version (id, version) VALUES ($1, $2) "
            "ON CONFLICT (id) DO UPDATE SET version = $2",
            APP_ID,
            script_version,
        )
        log.info("Migrated database v%d to v%d", version, script_version)


def _get_migrations(version: int) -> dict[int, str]:
    migrations: dict[int, str] = {}

    scripts = Path(__file__).parent / "scripts"
    for file in scripts.glob("*.sql"):
        m = re.match(r"\d+", file.stem)
        if m is None:
            continue

        file_version = int(m[0])
        if file_version in migrations:
            raise ValueError(f"Duplicate migration found for version {file_version}")

        if file_version <= version:
            continue

        migrations[file_version] = file.read_text("utf-8")

    return dict(sorted(migrations.items()))
