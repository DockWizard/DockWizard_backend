from database import startup_db_client
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routes import routes_agent, routes_database, routes_auth, routes_agent_data, routes_assets, routes_user, routes_websocket
from utils.auth_helpers import user_scheme, agent_scheme, user_scheme_websocket
from fastapi.routing import APIRoute

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    startup_db_client(app)


app.include_router(
    routes_agent_data.router, dependencies=[Depends(user_scheme)]
)
app.include_router(routes_agent.router, dependencies=[Depends(agent_scheme)])
app.include_router(routes_database.router)
app.include_router(routes_auth.router)
app.include_router(routes_assets.router)
app.include_router(routes_user.router, dependencies=[Depends(user_scheme)])
app.include_router(routes_websocket.router)


def use_route_names_as_operation_ids(app: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name  # in this case, 'read_items'


use_route_names_as_operation_ids(app)
