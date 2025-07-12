# LINE API セットアップ手順

## 1. LINE Developers コンソールでChannelを作成

1. [LINE Developers](https://developers.line.biz/) にアクセス
2. LINEアカウントでログイン
3. 「Create a provider」で新しいプロバイダーを作成
4. 「Create a channel」で「Messaging API」channelを作成
5. Channel情報を入力:
   - Channel name: `夏休み自由研究AI`
   - Channel description: `子どもの自由研究をサポートするAI`
   - Category: `Education`
   - Subcategory: `Education - Primary education`

## 2. Channel設定

### 基本設定
1. Channel基本設定タブで以下を確認:
   - Channel ID
   - Channel secret
   - Channel access token (long-lived)

### Messaging API設定
1. Messaging APIタブで以下を設定:
   - 「Use webhooks」を有効化
   - Webhook URL: `https://your-domain.com/line/webhook` (実際のデプロイURL)
   - 「Auto-reply messages」を無効化
   - 「Greeting messages」を無効化

## 3. 環境変数の設定

### 方法1: .envファイルを作成（推奨）

```bash
# backend/.env ファイルを作成
cd backend
touch .env
```

`.env` ファイルに以下を記述:
```
GEMINI_API_KEY=your_actual_gemini_api_key_here
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token_here
LINE_CHANNEL_SECRET=your_channel_secret_here
```

## 4. 必要な依存関係のインストール

```bash
cd backend
pip install -r requirements.txt
```

## 5. サーバーの起動

```bash
cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

## 6. 動作確認

### APIの健康状態をチェック
```bash
curl http://localhost:8000/line/health
```

### LINE連携テスト
1. フロントエンドアプリで設定 > LINE連携ページにアクセス
2. 「LINE連携する」ボタンをクリック
3. LINE友達追加を完了
4. 連携状態が「✅ 連携済み」になることを確認

## 注意事項

- Channel Access Tokenは機密情報です。GitHubなどに公開しないでください
- `.env` ファイルは `.gitignore` に含まれているため、リポジトリにコミットされません
- LINE Messaging APIの利用には料金が発生する場合があります
