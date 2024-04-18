# discord-oauth2-test

Just me messing around with [Starlette](https://www.starlette.io/) and [ngrok](https://ngrok.com/docs/)
to handle [Discord's OAuth2](https://discord.com/developers/docs/topics/oauth2) flow.

## Usage

1. Copy `.env.example` to `.env` and fill in the variables, except `REDIRECT_URI`.

2. Start an HTTPS tunnel with ngrok in a separate terminal:

   ```sh
   ngrok http 8000
   ```

3. Copy the forwarding address to `REDIRECT_URI`, and add it to your bot
   application under the OAuth2 tab in the [Discord Developer Portal].

4. Start the application:

   ```sh
   docker compose up --build --exit-code-from app
   ```

5. In Discord, send `@bot-mention invite` to receive a temporary,
   10-minute link for authorizing the bot.

[Discord Developer Portal]: https://discord.com/developers/applications
