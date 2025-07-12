# AWS設定手順

夏休み自由研究AIアプリケーション用のAWS環境構築手順です。

## 🚀 前提条件

- AWSアカウントの取得
- AWS CLI インストール（推奨）
- 適切なIAMユーザーとアクセスキーの準備

## 1. IAM設定

### 1.1 IAMユーザーの作成

1. **AWS Console > IAM > Users** にアクセス
2. **Add users** をクリック
3. ユーザー名: `research-app-user`
4. Access type: **Programmatic access** を選択
5. **Next: Permissions** をクリック

### 1.2 IAMポリシーの作成

カスタムポリシーを作成します：

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:Query",
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:BatchGetItem",
                "dynamodb:BatchWriteItem",
                "dynamodb:DescribeTable"
            ],
            "Resource": [
                "arn:aws:dynamodb:*:*:table/ResearchApp",
                "arn:aws:dynamodb:*:*:table/ResearchApp/index/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket",
                "s3:GetObjectMetadata",
                "s3:HeadBucket"
            ],
            "Resource": [
                "arn:aws:s3:::research-app-storage",
                "arn:aws:s3:::research-app-storage/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-sonnet-*",
                "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-haiku-*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "ses:SendEmail",
                "ses:SendRawEmail"
            ],
            "Resource": "*"
        }
    ]
}
```

### 1.3 ポリシーをユーザーに付与

1. 作成したポリシーを選択
2. **Attach existing policies directly** を選択
3. **Next: Tags** → **Next: Review** → **Create user**
4. **Access Key ID** と **Secret Access Key** を保存

## 2. DynamoDB設定

### 2.1 テーブル作成

```bash
aws dynamodb create-table \
    --table-name ResearchApp \
    --attribute-definitions \
        AttributeName=PK,AttributeType=S \
        AttributeName=SK,AttributeType=S \
        AttributeName=GSI1PK,AttributeType=S \
        AttributeName=GSI1SK,AttributeType=S \
        AttributeName=GSI2PK,AttributeType=S \
        AttributeName=GSI2SK,AttributeType=S \
        AttributeName=GSI3PK,AttributeType=S \
        AttributeName=GSI3SK,AttributeType=S \
        AttributeName=GSI4PK,AttributeType=S \
        AttributeName=GSI4SK,AttributeType=S \
    --key-schema \
        AttributeName=PK,KeyType=HASH \
        AttributeName=SK,KeyType=RANGE \
    --global-secondary-indexes \
        IndexName=GSI1,KeySchema='[{AttributeName=GSI1PK,KeyType=HASH},{AttributeName=GSI1SK,KeyType=RANGE}]',Projection='{ProjectionType=ALL}',ProvisionedThroughput='{ReadCapacityUnits=5,WriteCapacityUnits=5}' \
        IndexName=GSI2,KeySchema='[{AttributeName=GSI2PK,KeyType=HASH},{AttributeName=GSI2SK,KeyType=RANGE}]',Projection='{ProjectionType=ALL}',ProvisionedThroughput='{ReadCapacityUnits=5,WriteCapacityUnits=5}' \
        IndexName=GSI3,KeySchema='[{AttributeName=GSI3PK,KeyType=HASH},{AttributeName=GSI3SK,KeyType=RANGE}]',Projection='{ProjectionType=ALL}',ProvisionedThroughput='{ReadCapacityUnits=5,WriteCapacityUnits=5}' \
        IndexName=GSI4,KeySchema='[{AttributeName=GSI4PK,KeyType=HASH},{AttributeName=GSI4SK,KeyType=RANGE}]',Projection='{ProjectionType=ALL}',ProvisionedThroughput='{ReadCapacityUnits=5,WriteCapacityUnits=5}' \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region ap-northeast-1
```

### 2.2 テーブル設定の確認

```bash
aws dynamodb describe-table --table-name ResearchApp --region ap-northeast-1
```

### 2.3 オンデマンド課金に変更（推奨）

```bash
aws dynamodb modify-table \
    --table-name ResearchApp \
    --billing-mode PAY_PER_REQUEST \
    --region ap-northeast-1
```

## 3. S3設定

### 3.1 バケット作成

```bash
aws s3 mb s3://research-app-storage --region ap-northeast-1
```

### 3.2 バケットポリシー設定

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowResearchAppAccess",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::YOUR_ACCOUNT_ID:user/research-app-user"
            },
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::research-app-storage",
                "arn:aws:s3:::research-app-storage/*"
            ]
        }
    ]
}
```

### 3.3 CORS設定

```json
[
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "GET",
            "PUT",
            "POST",
            "DELETE",
            "HEAD"
        ],
        "AllowedOrigins": [
            "http://localhost:5173",
            "https://your-frontend-domain.com"
        ],
        "ExposeHeaders": [
            "ETag",
            "x-amz-meta-custom-header"
        ],
        "MaxAgeSeconds": 3000
    }
]
```

### 3.4 バケットの暗号化設定

```bash
aws s3api put-bucket-encryption \
    --bucket research-app-storage \
    --server-side-encryption-configuration '{
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                }
            }
        ]
    }'
```

## 4. AWS Bedrock設定

### 4.1 Bedrockモデルアクセス申請

1. **AWS Console > Bedrock > Model access** にアクセス
2. **Request model access** をクリック
3. 以下のモデルへのアクセスを申請：
   - **Anthropic Claude 3 Sonnet**
   - **Anthropic Claude 3 Haiku**
4. 申請理由を記入して送信

### 4.2 モデルの利用可能確認

```bash
aws bedrock list-foundation-models --region us-east-1
```

## 5. SES設定（メール通知用）

### 5.1 SESの設定

1. **AWS Console > SES** にアクセス
2. **Verified identities** で送信者メールアドレスを検証
3. **Sending statistics** でサンドボックスモードを解除（本番環境の場合）

### 5.2 送信制限の設定

```bash
aws sesv2 put-account-sending-enabled --enabled
aws sesv2 put-sending-quota --max-send-rate 10 --max-24-hour-send 200
```

## 6. 環境変数の設定

### 6.1 backend/.env ファイル作成

```bash
# AWS設定
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=ap-northeast-1

# DynamoDB設定
DYNAMODB_TABLE_NAME=ResearchApp

# S3設定
S3_BUCKET_NAME=research-app-storage

# Bedrock設定
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_REGION=us-east-1

# SES設定
SES_FROM_EMAIL=noreply@yourdomain.com
SES_REGION=ap-northeast-1

# その他の設定
GEMINI_API_KEY=your_gemini_api_key_here
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
LINE_CHANNEL_SECRET=your_line_channel_secret
```

### 6.2 環境変数の検証

```bash
# バックエンドディレクトリに移動
cd backend

# 環境変数の読み込み確認
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('AWS_ACCESS_KEY_ID:', os.getenv('AWS_ACCESS_KEY_ID')[:10] + '...')
print('S3_BUCKET_NAME:', os.getenv('S3_BUCKET_NAME'))
print('DYNAMODB_TABLE_NAME:', os.getenv('DYNAMODB_TABLE_NAME'))
"
```

## 7. データベースマイグレーション

### 7.1 初期データの投入

```python
# scripts/init_data.py
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.client.dynamodb_client import get_dynamodb_client
from models.project import ResearchTheme
from models.user import UserProfile
from models.enums import Grade, Genre, Interest, Personality, Strength, Duration

async def init_sample_data():
    """サンプルデータの投入"""
    client = get_dynamodb_client()

    # サンプルテーマの作成
    theme = ResearchTheme.create(
        theme_id="sample-theme-001",
        title="植物の成長観察",
        description="種から育てる植物の成長を観察し、環境要因の影響を調べる研究",
        genre=Genre.observation,
        difficulty="medium",
        estimatedDays=14,
        materials=["植木鉢", "土", "種", "定規"],
        defaultSteps=["種まき", "発芽観察", "成長記録", "まとめ"],
        targetGrades=[Grade.elementary4, Grade.elementary5],
        keywords=["植物", "成長", "観察", "環境"]
    )

    await client.put_item(theme.to_dynamo_item())
    print("サンプルデータ投入完了")

if __name__ == "__main__":
    asyncio.run(init_sample_data())
```

### 7.2 実行

```bash
cd backend
python scripts/init_data.py
```

## 8. 動作確認

### 8.1 DynamoDB接続確認

```bash
python -c "
import asyncio
from repositories.client.dynamodb_client import get_dynamodb_client

async def test():
    client = get_dynamodb_client()
    result = await client.health_check()
    print('DynamoDB接続:', '✅' if result else '❌')

asyncio.run(test())
"
```

### 8.2 S3接続確認

```bash
python -c "
import asyncio
from repositories.client.s3_client import get_s3_client

async def test():
    client = get_s3_client()
    result = await client.health_check()
    print('S3接続:', '✅' if result else '❌')

asyncio.run(test())
"
```

### 8.3 サーバー起動

```bash
cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 8.4 ヘルスチェック

```bash
curl http://localhost:8000/health
```

## 9. 本番環境デプロイ

### 9.1 ECS Fargateを使用する場合

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_REGION=${AWS_REGION}
      - DYNAMODB_TABLE_NAME=${DYNAMODB_TABLE_NAME}
      - S3_BUCKET_NAME=${S3_BUCKET_NAME}

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    environment:
      - VITE_API_BASE_URL=https://your-api-domain.com
```

### 9.2 AWS App Runnerを使用する場合

```yaml
# apprunner.yaml
version: 1.0
runtime: python3
build:
  commands:
    build:
      - pip install -r requirements.txt
run:
  runtime-version: 3.9
  command: uvicorn main:app --host 0.0.0.0 --port 8000
  network:
    port: 8000
    env: PORT
  env:
    - name: AWS_ACCESS_KEY_ID
      value: ${AWS_ACCESS_KEY_ID}
    - name: AWS_SECRET_ACCESS_KEY
      value: ${AWS_SECRET_ACCESS_KEY}
```

## 10. 監視・アラート設定

### 10.1 CloudWatch Logs

```bash
aws logs create-log-group --log-group-name /aws/lambda/research-app
```

### 10.2 CloudWatch Alarms

```bash
aws cloudwatch put-metric-alarm \
    --alarm-name "ResearchApp-DynamoDB-Errors" \
    --alarm-description "DynamoDB errors" \
    --metric-name UserErrors \
    --namespace AWS/DynamoDB \
    --statistic Sum \
    --period 300 \
    --threshold 1 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2
```

## 11. セキュリティ設定

### 11.1 WAF設定（本番環境）

```json
{
    "Name": "ResearchAppWAF",
    "Scope": "CLOUDFRONT",
    "DefaultAction": {
        "Allow": {}
    },
    "Rules": [
        {
            "Name": "AWSManagedRulesCommonRuleSet",
            "Priority": 1,
            "OverrideAction": {
                "None": {}
            },
            "Statement": {
                "ManagedRuleGroupStatement": {
                    "VendorName": "AWS",
                    "Name": "AWSManagedRulesCommonRuleSet"
                }
            }
        }
    ]
}
```

### 11.2 VPC設定（セキュアな環境）

```yaml
# vpc-config.yaml
Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true

  PrivateSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']

  PrivateSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.2.0/24
      AvailabilityZone: !Select [1, !GetAZs '']
```

## 12. コスト管理

### 12.1 予算設定

```bash
aws budgets create-budget \
    --account-id YOUR_ACCOUNT_ID \
    --budget '{
        "BudgetName": "ResearchAppBudget",
        "BudgetLimit": {
            "Amount": "50",
            "Unit": "USD"
        },
        "TimeUnit": "MONTHLY",
        "BudgetType": "COST"
    }'
```

### 12.2 コスト監視

- **DynamoDB**: オンデマンド課金で約 $0.25/100万リクエスト
- **S3**: 標準ストレージで約 $0.023/GB/月
- **Bedrock**: Claude使用で約 $0.015/1000トークン
- **データ転送**: 月1GB無料、その後 $0.09/GB

## 13. バックアップ設定

### 13.1 DynamoDB バックアップ

```bash
aws dynamodb put-backup-policy \
    --table-name ResearchApp \
    --backup-policy PointInTimeRecoveryEnabled=true
```

### 13.2 S3 バックアップ

```json
{
    "Rules": [
        {
            "ID": "ResearchAppBackup",
            "Status": "Enabled",
            "Transitions": [
                {
                    "Days": 30,
                    "StorageClass": "STANDARD_IA"
                },
                {
                    "Days": 90,
                    "StorageClass": "GLACIER"
                }
            ]
        }
    ]
}
```

## 🔧 トラブルシューティング

### よくある問題

1. **DynamoDB接続エラー**
   - IAM権限の確認
   - リージョンの確認
   - テーブル名の確認

2. **S3アップロードエラー**
   - CORS設定の確認
   - バケットポリシーの確認
   - 署名付きURLの有効期限確認

3. **Bedrock利用できない**
   - モデルアクセス申請の確認
   - リージョンの確認（us-east-1推奨）
   - IAM権限の確認

4. **高額請求**
   - CloudWatchでコスト監視
   - 予算アラートの設定
   - 不要なリソースの削除

---

これで、AWS環境でのアプリケーション実行準備が完了です！
