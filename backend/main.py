from fastapi import FastAPI
from routers import theme

app = FastAPI()
app.include_router(theme.router, prefix="/theme")


@app.get("/")
def read_root():
    return {"message": "Hello FastAPI!"}
