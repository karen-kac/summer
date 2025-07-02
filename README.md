# 🧪 夏休み自由研究サポートAI

AIが子どもと一緒に自由研究を進めてくれる、**伴奏型の自由研究支援アプリ**です。  
小学生〜中学生向けに、自由研究の**テーマ決め → 観察記録・実験など → レポート作成**までをAIがやさしくサポートします。

---

## 🎯 機能概要

### ✅ 子ども向け
- **自由研究テーマ提案**（学年・興味・得意分野などからAIが生成）
- **観察記録・実験支援（カレンダー機能付き）**（日ごとの記録をAIが要約・整理/実験の手伝い）
- **レポート作成支援**（記録をもとに子供達のレポート作成をAIが支援）

### ✅ 保護者向け
- **進捗通知機能**（定期的に報告）

---

## 🏗️ 技術構成

### Frontend（React + TypeScript）
- Vite + React + React Router
- Axios でバックエンド呼び出し
- 状態管理は React Context API

### Backend（Python + FastAPI）
- Claude (AWS Bedrock) にプロンプトを送って生成系処理
- DynamoDB：観察記録・ユーザー進捗の保存
- S3：画像やレポートの保存
- SES：保護者への通知メール・LINE送信

---

## 📁 ディレクトリ構成（イメージ）

```
summer-research-ai/
├── frontend/                        # React (Vite or CRA)
│   ├── public/
│   │   └── logo.png
│   ├── src/
│   │   ├── components/              # 再利用可能なUI部品
│   │   │   ├── ChatBox.tsx
│   │   │   ├── ThemeSelector.tsx
│   │   │   ├── DailyLogForm.tsx
│   │   │   └── ReportViewer.tsx
│   │   ├── pages/                   # React Routerページ
│   │   │   ├── Home.tsx
│   │   │   ├── NewProject.tsx
│   │   │   ├── RecordPage.tsx
│   │   │   └── ReportPage.tsx
│   │   ├── api/                     # バックエンド呼び出し
│   │   │   ├── generateTheme.ts
│   │   │   ├── summarizeLog.ts
│   │   │   ├── generateReport.ts
│   │   │   └── notifyGuardian.ts
│   │   ├── types/                   # TypeScript型定義
│   │   └── App.tsx
│   ├── .env                         # API URL など
│   └── vite.config.ts               # または CRA の設定
│
├── backend/                         # Python API（FastAPIまたはFlask）
│   ├── main.py                      # エントリーポイント
│   ├── routers/                     # エンドポイントごとに分割
│   │   ├── theme.py                 # Claude テーマ生成
│   │   ├── log.py                   # 観察記録の要約・保存
│   │   ├── report.py                # レポート生成
│   │   └── notify.py                # 保護者通知
│   ├── services/                    # Claude・DBなどのロジック層
│   │   ├── bedrock_client.py        # Claudeへのリクエスト
│   │   ├── s3_client.py             # S3アップロード
│   │   ├── dynamodb_client.py       # DynamoDB操作
│   │   └── email_sender.py          # SES送信処理
│   ├── prompts/                     # Claude用プロンプト
│   │   ├── theme.txt
│   │   ├── log_summary.txt
│   │   └── report.txt
│   ├── models/                      # Pydanticモデル（リクエスト/レスポンス）
│   │   ├── project.py
│   │   ├── log.py
│   │   └── report.py
│   ├── requirements.txt
│   └── .env                         # AWSキー、エンドポイントなど
│
├── shared/                          # 共有（プロンプトなど）
│   └── constants.py
│
├── README.md
├── .gitignore
└── docker-compose.yml              # 開発用（必要なら）
```

---

## 🚀 セットアップ手順

### 1. フロントエンド

```bash
cd frontend
npm install
npm run dev
```

環境変数 `.env` に API エンドポイントを指定：

```
VITE_API_BASE_URL=http://localhost:8000
```

---

### 2. バックエンド（FastAPI）

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

`.env` ファイルに AWS キー・Region を記述：

```
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-v2
```

---

## 🧠 Claude利用プロンプト（例）

### 🎓 テーマ提案用（`prompts/theme.txt`）

```
あなたは小学生の自由研究の先生です。
学年：{grade}、興味：{interest}、得意なこと：{strength}
これらをふまえて、夏休みにぴったりの研究テーマを3つ提案してください。
やさしい言葉で、準備・手順・必要日数を含めてください。
```

---

## 📦 今後の実装優先順（開発ロードマップ）

1. テーマ提案機能（Claude連携）
2. レポート生成支援（対話型？）
3. 観察記録の入力とAI要約（伴奏型UX）
4. 保護者通知機能（SES連携）


