from database import startup_db_client
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routes import routes_agent, routes_database, routes_auth, routes_agent_data, routes_assets, routes_user
from utils.auth_helpers import user_scheme, agent_scheme

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
