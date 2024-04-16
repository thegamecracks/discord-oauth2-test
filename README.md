# discord-oauth2-test

Just me messing around with [Starlette](https://www.starlette.io/) and [ngrok](https://ngrok.com/docs/)
to handle [Discord's OAuth2](https://discord.com/developers/docs/topics/oauth2) flow.

## Usage

TODO

## Updating dependencies

`requirements.txt` contains all the locked dependencies needed to
install this application, along with checksums to ensure integrity
of each dependency. To update this, you must run the following commands:

1. `pip install pip-tools`
2. `pip-compile --generate-hashes`

This will read the application's top-level dependencies from `requirements.in`
and determine all required dependencies.
