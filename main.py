import blitz.app as app
from blitz.utils import get_config
from blitz.utils import info

from contextlib import asynccontextmanager
from http import HTTPStatus
from fastapi import FastAPI, Request, Response
import uvicorn

'''
Every app in APPS must have
bot: Application
endpoint: str
async def setup() -> None
async def process_request() -> Response
'''
@asynccontextmanager
async def lifespan(_: FastAPI):
    await app.setup()
    async with app.bot:
        await app.bot.start()
        yield
        await app.bot.stop()

# Initialize FastAPI app (similar to Flask)
webserver = FastAPI(lifespan=lifespan)

@webserver.get(f'{app.endpoint}/test')
async def test_webapp(request: Request) -> Response:
    # Test with below urls
    # https://localhost:13337/webhook/blitz/test
    info(f"{request.url} from {request.client.host}:{request.client.port}")
    return Response("All is good!", status_code=HTTPStatus.OK)

async def process_request(request: Request):
    info(f"{request.url} from {request.client.host}:{request.client.port}")
    return await app.process_request(request)
webserver.add_api_route(app.endpoint, process_request, methods=['POST'])

if __name__ == '__main__':
    info("Starting Blitz uvicorn server...", command='uvicorn')
    try:
        uvicorn.run(
            "main:webserver",
            host='127.0.0.1',
            port=get_config("port"),
            reload=False,
        )
    finally:
        info('Blitz uvicorn server stopped...', command='uvicorn')
