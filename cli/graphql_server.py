from time import time
from config import GRAPHQL_PROT
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from strawberry.asgi import GraphQL
import uvicorn
import strawberry
from subgraph.resolver import Query

origins = [
        'http://localhost:3000',
        '*',
        ]

schema = strawberry.Schema(query=Query)

graphql_app = GraphQL(schema)

app = FastAPI()

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
# app.mount('/static', StaticFiles(directory='static'), name='static')
# app.add_websocket_route('/graphql', graphql_app)


if __name__ == "__main__":
    kwargs = { "host": "0.0.0.0", "port": GRAPHQL_PROT}
    uvicorn.run("event_api:app", **kwargs)
