#!/usr/bin/env python3
"""
初期データ投入スクリプト
サンプルデータをDynamoDBに投入します
"""

import asyncio
import sys
import os
from datetime import datetime, date

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.client.dynamodb_client import get_dynamodb_client
from models.project import ResearchTheme, ResearchPlan, ResearchStep
from models.user import UserProfile, UserSettings, UserStats
from models.enums import Grade, Genre, Interest, Personality, Strength, Duration


async def init_sample_themes():
    """サンプル研究テーマの投入"""
    client = get_dynamodb_client()

    themes = [
        {
            "theme_id": "sample-theme-001",
            "title": "植物の成長観察",
            "description": "種から育てる植物の成長を観察し、環境要因の影響を調べる研究です。日当たり、水やり、土の種類などの条件を変えて比較実験を行います。",
            "genre": Genre.observation,
            "difficulty": "medium",
            "estimatedDays": 14,
            "materials": ["植木鉢", "土", "種（朝顔、ひまわりなど）", "定規", "カメラ", "記録用紙"],
            "defaultSteps": ["種まき", "発芽観察", "成長記録", "条件変更実験", "データ整理", "まとめ"],
            "targetGrades": [Grade.elementary4, Grade.elementary5, Grade.elementary6],
            "keywords": ["植物", "成長", "観察", "環境", "比較実験"]
        },
        {
            "theme_id": "sample-theme-002",
            "title": "水の浄化実験",
            "description": "汚れた水を様々な方法で浄化し、その効果を比較する実験です。身近な材料を使って浄化装置を作り、水質の変化を観察します。",
            "genre": Genre.experiment,
            "difficulty": "medium",
            "estimatedDays": 10,
            "materials": ["ペットボトル", "砂利", "砂", "活性炭", "コーヒーフィルター", "泥水", "pH試験紙"],
            "defaultSteps": ["浄化装置作成", "汚れた水の準備", "浄化実験", "効果測定", "結果比較", "考察", "まとめ"],
            "targetGrades": [Grade.elementary5, Grade.elementary6, Grade.junior1],
            "keywords": ["水", "浄化", "実験", "環境", "科学"]
        },
        {
            "theme_id": "sample-theme-003",
            "title": "音の性質を調べよう",
            "description": "楽器や身近な物を使って音の高さや大きさの違いを調べる実験です。音の振動を視覚的に確認し、音の性質を理解します。",
            "genre": Genre.experiment,
            "difficulty": "easy",
            "estimatedDays": 7,
            "materials": ["ゴム", "空き缶", "水", "ストロー", "スマートフォン（録音用）"],
            "defaultSteps": ["楽器作成", "音の高さ実験", "音の大きさ実験", "振動の観察", "録音・分析", "まとめ"],
            "targetGrades": [Grade.elementary3, Grade.elementary4, Grade.elementary5],
            "keywords": ["音", "振動", "楽器", "実験", "物理"]
        },
        {
            "theme_id": "sample-theme-004",
            "title": "昆虫の観察日記",
            "description": "身近な昆虫を継続的に観察し、その行動や生態を記録する研究です。写真撮影と共に詳細な観察記録を作成します。",
            "genre": Genre.observation,
            "difficulty": "easy",
            "estimatedDays": 21,
            "materials": ["虫眼鏡", "カメラ", "観察記録用紙", "筆記用具"],
            "defaultSteps": ["観察場所決定", "昆虫の特定", "日常観察", "行動記録", "写真整理", "生態まとめ"],
            "targetGrades": [Grade.elementary2, Grade.elementary3, Grade.elementary4],
            "keywords": ["昆虫", "観察", "生態", "自然", "記録"]
        },
        {
            "theme_id": "sample-theme-005",
            "title": "天気と雲の関係調査",
            "description": "毎日の天気と雲の形を観察し、天気予報との関係を調べる研究です。気象データを収集して分析します。",
            "genre": Genre.research,
            "difficulty": "medium",
            "estimatedDays": 30,
            "materials": ["カメラ", "温度計", "記録用紙", "方位磁石", "天気予報アプリ"],
            "defaultSteps": ["観察計画立案", "毎日の記録", "雲の分類", "天気予報との比較", "データ分析", "まとめ"],
            "targetGrades": [Grade.elementary5, Grade.elementary6, Grade.junior1],
            "keywords": ["天気", "雲", "気象", "観察", "データ分析"]
        }
    ]

    print("🌱 研究テーマデータを投入中...")
    for theme_data in themes:
        theme = ResearchTheme.create(**theme_data)
        success = await client.put_item(theme.to_dynamo_item())
        if success:
            print(f"✅ テーマ投入成功: {theme.title}")
        else:
            print(f"❌ テーマ投入失敗: {theme.title}")

    print(f"📊 合計 {len(themes)} 件のテーマを投入しました")


async def init_sample_plans():
    """サンプル研究計画の投入"""
    client = get_dynamodb_client()

    plans = [
        {
            "plan_id": "plan-theme-001",
            "themeId": "sample-theme-001",
            "title": "植物成長観察計画",
            "description": "植物の成長を系統的に観察し、環境要因の影響を調べる詳細な計画です。",
            "steps": [
                ResearchStep(
                    stepId="step-1",
                    title="準備・種まき",
                    description="実験に必要な材料を準備し、複数の条件で種をまきます。",
                    tips=["種は同じ種類を使用する", "植木鉢に番号をつける", "種まき日時を記録する"],
                    estimatedDuration="1日",
                    order=1
                ),
                ResearchStep(
                    stepId="step-2",
                    title="発芽観察",
                    description="種まきから発芽までの期間を観察し、記録します。",
                    tips=["毎日同じ時間に観察する", "発芽の定義を決める", "写真を撮る"],
                    estimatedDuration="3-7日",
                    order=2
                ),
                ResearchStep(
                    stepId="step-3",
                    title="成長記録",
                    description="発芽後の成長を継続的に観察し、測定します。",
                    tips=["草丈を定規で測る", "葉の数を数える", "成長の変化を記録"],
                    estimatedDuration="7-10日",
                    order=3
                ),
                ResearchStep(
                    stepId="step-4",
                    title="まとめ・考察",
                    description="観察結果をまとめ、環境要因の影響について考察します。",
                    tips=["グラフを作成する", "写真を整理する", "なぜそうなったか考える"],
                    estimatedDuration="2-3日",
                    order=4
                )
            ],
            "totalDays": 14,
            "difficulty": "medium",
            "genre": Genre.observation
        },
        {
            "plan_id": "plan-theme-002",
            "themeId": "sample-theme-002",
            "title": "水質浄化実験計画",
            "description": "段階的に浄化装置を作成し、効果を科学的に検証する実験計画です。",
            "steps": [
                ResearchStep(
                    stepId="step-1",
                    title="浄化装置の設計・作成",
                    description="ペットボトルを使って多層の浄化装置を作成します。",
                    tips=["層の順序を考える", "材料の特性を理解する", "水の流れを確認する"],
                    estimatedDuration="2日",
                    order=1
                ),
                ResearchStep(
                    stepId="step-2",
                    title="実験準備",
                    description="汚れた水を準備し、浄化前の状態を記録します。",
                    tips=["同じ汚れ具合の水を用意", "色や濁りを観察", "pHを測定"],
                    estimatedDuration="1日",
                    order=2
                ),
                ResearchStep(
                    stepId="step-3",
                    title="浄化実験実施",
                    description="作成した装置で水を浄化し、結果を記録します。",
                    tips=["時間を計測する", "各段階での変化を記録", "複数回実験する"],
                    estimatedDuration="3-4日",
                    order=3
                ),
                ResearchStep(
                    stepId="step-4",
                    title="結果分析・まとめ",
                    description="実験結果を分析し、浄化の仕組みについて考察します。",
                    tips=["before/afterを比較", "どの材料が効果的か分析", "改善点を考える"],
                    estimatedDuration="2-3日",
                    order=4
                )
            ],
            "totalDays": 10,
            "difficulty": "medium",
            "genre": Genre.experiment
        }
    ]

    print("📋 研究計画データを投入中...")
    for plan_data in plans:
        plan = ResearchPlan.create(**plan_data)
        success = await client.put_item(plan.to_dynamo_item())
        if success:
            print(f"✅ 計画投入成功: {plan.title}")
        else:
            print(f"❌ 計画投入失敗: {plan.title}")

    print(f"📊 合計 {len(plans)} 件の計画を投入しました")


async def init_sample_users():
    """サンプルユーザーデータの投入"""
    client = get_dynamodb_client()

    users = [
        {
            "user_id": "demo-user-001",
            "email": "demo@example.com",
            "displayName": "田中太郎",
            "grade": Grade.elementary5,
            "interests": [Interest.science, Interest.nature],
            "personality": [Personality.curious, Personality.patient],
            "strengths": [Strength.observation, Strength.writing],
            "preferredDuration": Duration.two_weeks,
            "parentEmail": "parent@example.com",
            "bio": "虫や植物が大好きな小学5年生です。"
        },
        {
            "user_id": "demo-user-002",
            "email": "demo2@example.com",
            "displayName": "佐藤花子",
            "grade": Grade.elementary4,
            "interests": [Interest.art, Interest.cooking],
            "personality": [Personality.creative, Personality.active],
            "strengths": [Strength.craft, Strength.presentation],
            "preferredDuration": Duration.one_week,
            "parentEmail": "parent2@example.com",
            "bio": "工作と料理が得意な小学4年生です。"
        }
    ]

    print("👤 サンプルユーザーデータを投入中...")
    for user_data in users:
        user_id = user_data["user_id"]

        # ユーザープロフィール
        profile = UserProfile.create(**user_data)
        profile_success = await client.put_item(profile.to_dynamo_item())

        # ユーザー設定
        settings = UserSettings.create(user_id)
        settings_success = await client.put_item(settings.to_dynamo_item())

        # ユーザー統計
        stats = UserStats.create(user_id)
        stats_success = await client.put_item(stats.to_dynamo_item())

        if profile_success and settings_success and stats_success:
            print(f"✅ ユーザー投入成功: {user_data['displayName']}")
        else:
            print(f"❌ ユーザー投入失敗: {user_data['displayName']}")

    print(f"📊 合計 {len(users)} 件のユーザーを投入しました")


async def verify_data():
    """データ投入の確認"""
    client = get_dynamodb_client()

    print("\n🔍 データ投入の確認中...")

    # テーマデータの確認（全テーマをチェック）
    theme_ids = ["sample-theme-001", "sample-theme-002", "sample-theme-003", "sample-theme-004", "sample-theme-005"]
    theme_count = 0
    for theme_id in theme_ids:
        theme_result = await client.query_items(f"THEME#{theme_id}")
        if theme_result["count"] > 0:
            theme_count += theme_result["count"]

    if theme_count > 0:
        print(f"✅ テーマデータ確認成功: {theme_count} 件")
    else:
        print("❌ テーマデータが見つかりません")

    # ユーザーデータの確認（全ユーザーをチェック）
    user_ids = ["demo-user-001", "demo-user-002"]
    user_count = 0
    for user_id in user_ids:
        user_result = await client.query_items(f"USER#{user_id}")
        if user_result["count"] > 0:
            user_count += user_result["count"]

    if user_count > 0:
        print(f"✅ ユーザーデータ確認成功: {user_count} 件")
    else:
        print("❌ ユーザーデータが見つかりません")

    # 計画データの確認（全計画をチェック）
    plan_ids = ["plan-theme-001", "plan-theme-002"]
    plan_count = 0
    for plan_id in plan_ids:
        plan_result = await client.query_items(f"PLAN#{plan_id}")
        if plan_result["count"] > 0:
            plan_count += plan_result["count"]

    if plan_count > 0:
        print(f"✅ 計画データ確認成功: {plan_count} 件")
    else:
        print("❌ 計画データが見つかりません")


async def main():
    """メイン処理"""
    print("🚀 初期データ投入を開始します...")

    try:
        # DynamoDBクライアントの接続確認
        client = get_dynamodb_client()
        health_check = await client.health_check()

        if not health_check:
            print("❌ DynamoDBに接続できません。設定を確認してください。")
            return

        print("✅ DynamoDB接続確認成功")

        # データ投入
        await init_sample_themes()
        await init_sample_plans()
        await init_sample_users()

        # データ確認
        await verify_data()

        print("\n🎉 初期データ投入が完了しました！")
        print("次は以下でサーバーを起動してください：")
        print("  cd backend")
        print("  python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
