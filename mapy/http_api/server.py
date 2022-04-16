from fastapi import FastAPI, Depends
from starlette.concurrency import run_in_threadpool
from uvicorn import run


async def statistics():
    return {
        "uptime": 0,
        "population": 0,
        "login_server": {"alive": 0, "port": 0, "population": 0},
        "game_servers": {"Scania": {0: {"alive": 0, "port": 0, "population": 0}}},
    }


wsgi_app = FastAPI(title="MaPy Web API", description="Web API")


@wsgi_app.get("/status", status_code=200)
async def status(stats: dict = Depends(statistics)):
    return stats


async def app(server):

    wsgi_app.dependency_overrides[statistics] = server.statistics

    await run_in_threadpool(lambda: run("mapy.http_api.server:wsgi_app"))
