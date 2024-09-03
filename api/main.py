from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import Model, engine
from .routers import pages


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(pages.router)
