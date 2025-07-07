from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import theme

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(theme.router, prefix="/theme")


@app.get("/")
def read_root():
    return {"message": "Hello FastAPI!"}



#python -m uvicorn main:app --reload
#http://localhost:8000
