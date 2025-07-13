#!/usr/bin/env python3
"""
初期実績データを作成するスクリプト
"""
import asyncio
import sys
import os
from datetime import datetime

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.repository_factory import get_repository_factory
from models.achievement import Achievement


async def create_initial_achievements():
    """初期実績データを作成"""
    factory = get_repository_factory()
    achievement_repo = factory.get_achievement_repository()

    # 初期実績の定義
    initial_achievements = [
        {
            "achievementId": "first_theme",
            "name": "はじめの一歩",
            "description": "初めて研究テーマを選択しました",
            "icon": "🌟",
            "category": "beginner",
            "requirements": {"theme_selections": 1},
            "points": 10
        },
        {
            "achievementId": "first_step",
            "name": "研究開始",
            "description": "初めて研究ステップを完了しました",
            "icon": "🔬",
            "category": "beginner",
            "requirements": {"steps_completed": 1},
            "points": 10
        },
        {
            "achievementId": "first_project",
            "name": "研究完了者",
            "description": "初めて研究プロジェクトを完了しました",
            "icon": "🏆",
            "category": "completion",
            "requirements": {"projects_completed": 1},
            "points": 50
        },
        {
            "achievementId": "first_record",
            "name": "記録の達人",
            "description": "初めて研究記録を作成しました",
            "icon": "📝",
            "category": "beginner",
            "requirements": {"records_created": 1},
            "points": 10
        },
        {
            "achievementId": "record_keeper",
            "name": "記録係",
            "description": "10件の記録を作成しました",
            "icon": "📚",
            "category": "progress",
            "requirements": {"records_created": 10},
            "points": 25
        },
        {
            "achievementId": "record_master",
            "name": "記録マスター",
            "description": "50件の記録を作成しました",
            "icon": "📖",
            "category": "progress",
            "requirements": {"records_created": 50},
            "points": 100
        },
        {
            "achievementId": "first_photo",
            "name": "写真家",
            "description": "初めて写真を記録しました",
            "icon": "📸",
            "category": "beginner",
            "requirements": {"photos_uploaded": 1},
            "points": 10
        },
        {
            "achievementId": "photo_collector",
            "name": "写真コレクター",
            "description": "10枚の写真を記録しました",
            "icon": "🖼️",
            "category": "progress",
            "requirements": {"photos_uploaded": 10},
            "points": 25
        },
        {
            "achievementId": "level_master",
            "name": "レベルマスター",
            "description": "レベル10に到達しました",
            "icon": "🎯",
            "category": "special",
            "requirements": {"level": 10},
            "points": 200
        },
        {
            "achievementId": "points_collector",
            "name": "ポイントコレクター",
            "description": "1000ポイントを獲得しました",
            "icon": "💎",
            "category": "special",
            "requirements": {"total_points": 1000},
            "points": 100
        }
    ]

    print("🚀 初期実績データを作成しています...")
    created_count = 0

    for achievement_data in initial_achievements:
        try:
            # 既存チェック
            existing = await achievement_repo.get_achievement(achievement_data["achievementId"])
            if existing:
                print(f"⏭️  実績が既に存在します: {achievement_data['name']}")
                continue

            # 実績を作成
            achievement_id = achievement_data.pop("achievementId")  # achievementIdを取り出す
            achievement = Achievement.create(achievement_id, **achievement_data)
            success = await achievement_repo.create_achievement(achievement)

            if success:
                created_count += 1
                print(f"✅ 実績を作成しました: {achievement_data['name']}")
            else:
                print(f"❌ 実績作成に失敗しました: {achievement_data['name']}")

        except Exception as e:
            print(f"❌ 実績作成エラー: {achievement_data['name']}, {e}")

    print(f"\n🎉 初期実績データの作成が完了しました！")
    print(f"   作成された実績: {created_count}件")
    print(f"   合計実績数: {len(initial_achievements)}件")


async def main():
    """メイン関数"""
    try:
        print("=" * 60)
        print("🎯 実績システム初期化スクリプト")
        print("=" * 60)

        await create_initial_achievements()

        print("\n" + "=" * 60)
        print("🎊 実績システムの初期化が完了しました！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 初期化中にエラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
