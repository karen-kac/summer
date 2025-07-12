from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import theme, line

app = FastAPI()
app.include_router(theme.router, prefix="/theme")
app.include_router(line.router, prefix="/line")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello FastAPI!"}
