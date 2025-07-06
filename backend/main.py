from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import theme

app = FastAPI()
app.include_router(theme.router, prefix="/theme")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # フロントのURL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello FastAPI!"}
