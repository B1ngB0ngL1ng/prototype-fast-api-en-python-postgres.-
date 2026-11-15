# FastAPI entrypoint komt hier later.

from fastapi import FastAPI

from app.routes_and_handlers.warehouse_routes import router as warehouse_router


app = FastAPI(
    title="CargoHub API",
    description="CargoHub REST API met FastAPI en PostgreSQL",
    version="1.0.0"
)


app.include_router(warehouse_router)


@app.get("/")
def root():
    return {
        "message": "CargoHub API is running"
    }
