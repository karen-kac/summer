import os
import re
import json
import sys
sys.path.append(os.pardir)
from typing import List
from fastapi import HTTPException
from backend.models.theme_models import ThemeRecommendation


class MakeRecommendsRepository:
    """
    プロントエンドから来た属性をプロンプトに変換するクラス
    """
    def __init__(self, text: str = None):
        try:
           self.text = text
           if not self.text:
               raise KeyError()
        except KeyError:
            raise RuntimeError("プロンプト文が設定されていません。")
        except Exception as e:
            # その他の初期化エラー
            raise RuntimeError(f"初期化中にエラーが発生しました: {e}")

    async def generate_recommend_startproject(self) -> List[ThemeRecommendation]:
        """
        テキストからJSON部分を抽出し、ThemeRecommendationのリストを生成する。
        """
        try:
            match = re.search(r'```json\s*([\s\S]*?)\s*```', self.text)
            if not match:
              raise ValueError("テキスト内にJSONブロックが見つかりません。")

            json_string = match.group(1).strip()
            if not json_string:
                 raise ValueError("テキスト内に有効なJSONコンテンツが見つかりません。")
            
            data = json.loads(json_string)
            
            recommendations = [ThemeRecommendation(**item) for item in data]
            
            return recommendations
        except json.JSONDecodeError as e:
             raise HTTPException(
                status_code=500, 
                detail=f"JSONの解析に失敗しました: {e}. 元のテキスト: '{json_string[:100]}...'"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"テキスト変換中にエラーが発生しました: {e}"
            )

        

if __name__ == "__main__":
    # テスト用の簡易実行コード
    import asyncio
    makeprompt = MakeRecommendsRepository(text="""
```json
[
  {
    "title": "弦楽器の音の秘密を探る！～弦の条件と音の高さの関係～",
    "description": "ギターやウクレレなどの弦楽器を使って、弦の長さ、太さ、張力が音の高さにどのように影 響するかを実験し、その物理的な原理を解き明かします。様々な条件で音の周波数を測定し、データに基づいて考 察を深めます。",
    "materials": [
      "ギターまたはウクレレ（弦楽器なら何でも可）",
      "音程測定アプリ（スマートフォンで可）",
      "メジャーまたは定規",
      "異なる太さの弦（可能であれば）",
      "文鎮や洗濯バサミなど（弦の張力を変える工夫に利用）",
      "記録用紙、筆記用具"
    ],
    "steps": [
      "弦楽器の弦の種類（太さ、材質）を統一し、長さを変えながら音の高さ（周波数）を測定・記録する。",
      "同じ長さの弦で、太さの異なる弦がある場合、それぞれの音の高さを測定・記録し比較する。",
      "同じ弦の長さと太さで、張力を変えながら音の高さを測定・記録する（例: 重りをぶら下げて張力を変える）。",
      "それぞれの実験結果をグラフや表にまとめ、音の高さと弦の各条件の関係について考察する。",
      "実験で得られた知識を基に、より効率的に音を出す方法や、楽器の設計について推測を立てる。"
    ],
    "estimatedDays": 10,
    "difficulty": "medium"
  },
  {
    "title": "運動と心拍数のヒミツ！～効果的な運動強度を探る～",
    "description": "ウォーキング、ジョギング、縄跳びなど、様々な種類の運動を一定時間行い、運動前、運動 中、運動後の心拍数の変化を測定・記録します。自分にとって最適な運動強度や、効率的なトレーニング方法を見 つける手がかりを探る研究です。",
    "materials": [
      "ストップウォッチ",
      "心拍数測定アプリ（スマートフォンで可）またはスマートウォッチ",
      "運動着、運動靴",
      "水分補給用の飲み物",
      "記録用紙、筆記用具",
      "運動できるスペース（室内外問わず）"
    ],
    "steps": [
      "安静時の心拍数を測定し、記録する。",
      "異なる種類の運動（例：5分間のウォーキング、5分間のジョギング、5分間の縄跳びなど）をそれぞれ計画 する。",
      "各運動を行う前後、そして運動中に一定間隔で心拍数を測定し、記録する。",
      "運動後の心拍数が安静時レベルに戻るまでの時間も記録する。",
      "得られたデータを比較し、運動の種類や強度と心拍数の変化、回復時間の関係をグラフや表にまとめる。",
      "心拍数の変化から、それぞれの運動が体にかける負荷や、効果的な運動強度について考察する。"
    ],
    "estimatedDays": 12,
    "difficulty": "medium"
  },
  {
    "title": "音楽の力で運動能力アップ！？～音楽が運動パフォーマンスに与える影響～",
    "description": "運動中に聴く音楽の種類（アップテンポ、スローテンポ、好きな曲、無音など）を変えるこ とで、集中力、持久力、疲労感、運動の効率がどのように変化するかを実験します。音楽が持つ心理的・生理的な 影響を科学的に探求する研究です。",
    "materials": [
      "スマートフォン（音楽再生用）",
      "イヤホンまたはヘッドホン",
      "ストップウォッチ",
      "簡単な運動（例：スクワット、腕立て伏せ、縄跳びなど）",
      "記録用紙、筆記用具",
      "運動できるスペース"
    ],
    "steps": [
      "実験で比較する運動の種類（例：スクワットの連続回数、縄跳びの連続回数、一定時間での走行距離など）と、聴く音楽の種類（例：アップテンポの曲、スローテンポの曲、好きな曲、無音など）を複数パターン決定する 。",
      "各条件下で、同じ運動を同じ時間または同じ回数行い、そのパフォーマンス（回数、距離、時間など）を記録する。",
      "運動中の集中力、疲労感、楽しさなどの主観的な感想も記録する。",
      "得られた客観的なデータと主観的な感想を比較分析し、音楽が運動パフォーマンスに与える影響について考察する。",
      "どのような音楽が、どのような運動に最適なのか、その理由を自分なりに分析し、発表資料にまとめる。" 
    ],
    "estimatedDays": 14,
    "difficulty": "medium"
  }
]
```
""")

    async def main_test():
        try:
            result = await makeprompt.generate_recommend_startproject()
            # 結果をJSON形式で出力
            print(json.dumps([item.model_dump() for item in result], ensure_ascii=False, indent=2))
            # もしくは、ThemeRecommendationのリストをそのまま出力
            # これはデバッグ用に便利です
            # print(f"APIからの応答: {result}")
        except Exception as e:
            print(f"エラー: {e}")
    asyncio.run(main_test())