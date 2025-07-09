# backend/main.py

import os
from flask import Flask, jsonify
from dotenv import load_dotenv
from flask_cors import CORS # CORSを有効にするためにインポート
from routers import auth

app.include_router(auth.router)


# ルーターをインポート
from backend.routers.auth import auth_bp
# 他のルーターもここにインポートします (例: from backend.routers.theme import theme_bp)

# .env ファイルから環境変数をロード
load_dotenv()

app = Flask(__name__)

# CORS設定
# 開発用。本番環境では許可するオリジンを厳密に指定してください。
# 例: CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
CORS(app)

# ルーターを登録
app.register_blueprint(auth_bp, url_prefix='/api/auth')
# 他のルーターもここに登録します (例: app.register_blueprint(theme_bp, url_prefix='/api/theme'))

@app.route('/')
def index():
    """
    ルートパスのテストエンドポイント
    """
    return jsonify({"message": "Summer Research AI Backend is running!"})

if __name__ == '__main__':
    # 開発サーバーの起動
    # FLASK_ENV=development を設定するとデバッグモードが有効になります
    # app.run(debug=True, port=5000)
    app.run(debug=True, host='0.0.0.0', port=5000)

