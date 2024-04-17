from starlette.responses import JSONResponse
from starlette.routing import Route


async def homepage(request):
    return JSONResponse({"hello": "world"})


ROUTES = [
    Route("/", homepage),
]
