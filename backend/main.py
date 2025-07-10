from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import theme, auth, users, projects

app = FastAPI(title="Summer Research AI API")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(theme.router, prefix="/theme", tags=["themes"])

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Summer Research AI API - Ready to help with your research!"}
