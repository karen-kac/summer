from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# 環境変数の読み込み
load_dotenv()

# アプリケーションの初期化
app = FastAPI(
    title="Summer Research AI Backend",
    description="研究支援ツールのバックエンドAPI（FastAPI）",
    version="0.1.0"
)

# CORS設定（フロントエンドとの連携のため）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 認証ルーターを登録
from backend.routers import auth
app.include_router(auth.router, prefix="/api/auth", tags=["認証"])

# 起動確認用ルート
@app.get("/", tags=["起動確認"])
async def root():
    return {"message": "Summer Research AI Backend is running with FastAPI!"}

# 直接実行用（Pythonから）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
