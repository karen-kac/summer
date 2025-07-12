from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routers import theme, user, record
from repositories.client.dynamodb_client import get_dynamodb_client
from repositories.client.s3_client import get_s3_client
import asyncio
import logging
from datetime import datetime

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="夏休み自由研究AI",
    description="AI が子どもの自由研究をサポートするアプリケーション",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(theme.router, prefix="/theme", tags=["テーマ"])
app.include_router(user.router, prefix="/user", tags=["ユーザー"])
app.include_router(record.router, prefix="/record", tags=["記録"])


@app.get("/")
def read_root():
    """ルートエンドポイント"""
    return {
        "message": "夏休み自由研究AI",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "services": {}
        }

        # DynamoDBヘルスチェック
        try:
            dynamodb_client = get_dynamodb_client()
            dynamodb_health = await dynamodb_client.health_check()
            health_status["services"]["dynamodb"] = {
                "status": "healthy" if dynamodb_health else "unhealthy",
                "details": "接続確認済み" if dynamodb_health else "接続失敗"
            }
        except Exception as e:
            health_status["services"]["dynamodb"] = {
                "status": "error",
                "details": str(e)
            }

        # S3ヘルスチェック
        try:
            s3_client = get_s3_client()
            s3_health = await s3_client.health_check()
            health_status["services"]["s3"] = {
                "status": "healthy" if s3_health else "unhealthy",
                "details": "接続確認済み" if s3_health else "接続失敗"
            }
        except Exception as e:
            health_status["services"]["s3"] = {
                "status": "error",
                "details": str(e)
            }

        # 全体のステータス決定
        all_healthy = all(
            service["status"] == "healthy"
            for service in health_status["services"].values()
        )

        if not all_healthy:
            health_status["status"] = "degraded"

        return health_status

    except Exception as e:
        logger.error(f"ヘルスチェックエラー: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"ヘルスチェック失敗: {str(e)}"
        )


@app.get("/info")
def get_info():
    """アプリケーション情報"""
    return {
        "name": "夏休み自由研究AI",
        "description": "AIが子どもの自由研究をサポートするアプリケーション",
        "version": "1.0.0",
        "features": [
            "AI による研究テーマ提案",
            "研究計画の自動生成",
            "観察記録・実験データの管理",
            "画像アップロード・解析",
            "レポート自動生成",
            "LINE通知機能",
            "保護者向け進捗報告"
        ],
        "technologies": [
            "FastAPI",
            "DynamoDB",
            "S3",
            "AWS Bedrock (Claude)",
            "LINE Messaging API",
            "React (Frontend)"
        ]
    }


@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時の処理"""
    logger.info("🚀 夏休み自由研究AI を起動中...")

    # AWS接続確認
    try:
        # DynamoDB接続確認
        dynamodb_client = get_dynamodb_client()
        dynamodb_health = await dynamodb_client.health_check()
        if dynamodb_health:
            logger.info("✅ DynamoDB接続確認成功")
        else:
            logger.warning("⚠️  DynamoDB接続に問題があります")

        # S3接続確認
        s3_client = get_s3_client()
        s3_health = await s3_client.health_check()
        if s3_health:
            logger.info("✅ S3接続確認成功")
        else:
            logger.warning("⚠️  S3接続に問題があります")

    except Exception as e:
        logger.error(f"❌ AWS接続確認でエラー: {e}")

    logger.info("🎉 アプリケーション起動完了")


@app.on_event("shutdown")
async def shutdown_event():
    """アプリケーション終了時の処理"""
    logger.info("🛑 夏休み自由研究AI を終了中...")
    # 必要に応じてクリーンアップ処理を追加
    logger.info("👋 アプリケーション終了完了")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
