# Gemini API セットアップ手順

## 1. Google AI Studio でAPIキーを取得

1. [Google AI Studio](https://aistudio.google.com/app/apikey) にアクセス
2. Googleアカウントでログイン
3. "Create API key" ボタンをクリック
4. プロジェクトを選択（または新規作成）
5. APIキーをコピー

## 2. 環境変数の設定

### 方法1: .envファイルを作成（推奨）

```bash
# backend/.env ファイルを作成
cd backend
cp .env.example .env
```

`.env` ファイルに以下を記述:
```
GEMINI_API_KEY=your_actual_api_key_here
```

### 方法2: 環境変数を直接設定

```bash
# Mac/Linux
export GEMINI_API_KEY=your_actual_api_key_here

# Windows (PowerShell)
$env:GEMINI_API_KEY="your_actual_api_key_here"
```

## 3. サーバーの起動

```bash
cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

## トラブルシューティング

### エラー: "GEMINI_API_KEYが設定されていません"

- `.env` ファイルが `backend/` ディレクトリに存在することを確認
- APIキーが正しく設定されていることを確認
- サーバーを再起動

### エラー: "実際のGEMINI_API_KEYを設定してください"

- `dummy_key_for_testing` ではなく、実際のAPIキーを設定してください

### API通信エラー

- インターネット接続を確認
- APIキーが有効であることを確認
- Google AI Studioでクォータ制限に達していないかを確認

## 注意事項

- APIキーは機密情報です。GitHubなどに公開しないでください
- `.env` ファイルは `.gitignore` に含まれているため、リポジトリにコミットされません
- APIの利用には料金が発生する場合があります。Google AI Studioで利用状況を確認してください
