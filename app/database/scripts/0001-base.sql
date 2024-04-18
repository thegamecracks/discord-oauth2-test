CREATE TABLE discord_user (
    id BIGINT PRIMARY KEY
);
CREATE TABLE discord_oauth (
    user_id BIGINT PRIMARY KEY REFERENCES discord_user (id),
    access_token TEXT NOT NULL,
    token_type TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    refresh_token TEXT,
    scope TEXT NOT NULL
);
