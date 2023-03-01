from time import time
from typing import Union
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.gzip import GZipMiddleware
from strawberry.asgi import GraphQL
import uvicorn

from scanner.resolver import schema



graphql_app = GraphQL(schema)

app = FastAPI()


origins = [
        'http://localhost:3000',
        '*',
        ]

app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
        )

# response time middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get('/')
def read_root():
    return {"Hello": "World!"}

app.add_route('/graphql', graphql_app)

# app.add_websocket_route('/graphql', graphql_app)


if __name__ == "__main__":
    # web.run_app(init_app(), port=9002)
    kwargs = { "host": "0.0.0.0", "port": 9000}
    uvicorn.run("event_api:app", **kwargs)
