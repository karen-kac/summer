from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import theme, auth_frontend

app = FastAPI()
app.include_router(theme.router, prefix="/theme")
app.include_router(auth_frontend.router)
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
