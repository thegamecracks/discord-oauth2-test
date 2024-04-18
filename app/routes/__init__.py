from starlette.responses import JSONResponse
from starlette.routing import Route

from .auth import auth_flow


async def homepage(request):
    return JSONResponse({"hello": "world"})


ROUTES = [
    Route("/", homepage),
    Route("/callback", auth_flow.exchange_token),
]
