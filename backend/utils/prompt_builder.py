from models.theme import UserProfile, ResearchTheme


class PromptBuilder:
    def __init__(self):
        # enum値から日本語ラベルへのマッピング
        self.grade_labels = {
            'elementary1': '小学1年生',
            'elementary2': '小学2年生',
            'elementary3': '小学3年生',
            'elementary4': '小学4年生',
            'elementary5': '小学5年生',
            'elementary6': '小学6年生',
            'junior1': '中学1年生',
            'junior2': '中学2年生',
            'junior3': '中学3年生'
        }

        self.interest_labels = {
            'science': '理科・科学',
            'nature': '自然・環境',
            'animals': '動物・生物',
            'cooking': '料理・食べ物',
            'art': '美術・工作',
            'sports': 'スポーツ・運動',
            'music': '音楽・楽器',
            'history': '歴史・社会',
            'technology': 'プログラミング・技術',
            'math': '数学・計算'
        }

        self.personality_labels = {
            'curious': '好奇心旺盛',
            'patient': '根気強い',
            'creative': '創造的',
            'active': '活動的',
            'careful': '丁寧・慎重',
            'social': '協調性がある',
            'analytical': '分析的・論理的',
            'independent': '自立している'
        }

        self.strength_labels = {
            'observation': '観察',
            'writing': '文章を書く',
            'drawing': '絵を描く',
            'calculation': '計算・数学',
            'experiment': '実験・検証',
            'presentation': '発表・説明',
            'research': '読書・調査',
            'craft': 'ものづくり',
            'crafting': 'ものづくり',
            'calculating': '計算・数学',
            'reading': '読書・調査'
        }

        self.duration_labels = {
            '1week': '1週間',
            '2weeks': '2週間',
            '1month': '1ヶ月',
            '2months': '2ヶ月以上',
            'flexible': '特に決まっていない'
        }

        self.genre_labels = {
            'experiment': '実験型',
            'observation': '観察型',
            'research': '調査型'
        }

    def build_suggest_themes_prompt(self, profile: UserProfile):
        grade = self.grade_labels.get(profile.grade, profile.grade)
        interests = [self.interest_labels.get(i, i) for i in profile.interests]
        personality = [self.personality_labels.get(p, p) for p in profile.personality]
        strengths = [self.strength_labels.get(s, s) for s in profile.strengths]
        duration = self.duration_labels.get(profile.duration, profile.duration)

        prompt = (
            f"あなたは自由研究の研究テーマを提案する専門家です。\n\n"
            f"以下の子供のプロフィールに基づいて、その子に最適な自由研究テーマを3つ提案してください：\n"
            f"学年: {grade}\n"
            f"興味のある分野: {', '.join(interests)}\n"
            f"性格: {', '.join(personality)}\n"
            f"得意なこと: {', '.join(strengths)}\n"
            f"研究期間: {duration}\n"
        )

        if profile.additional_info:
            prompt += f"追加情報: {profile.additional_info}\n"

        prompt += (
            f"\n\n重要な要求事項：\n"
            f"1. 子供の興味（{', '.join(interests)}）に直接関連したテーマにしてください\n"
            f"2. 学年（{grade}）に適した難易度で、実現可能なテーマにしてください。難しすぎるものは不可です。\n"
            f"3. 期間（{duration}）内で完了できるテーマにしてください\n"
            f"4. 子供の得意分野（{', '.join(strengths)}）を活かせるテーマにしてください\n"
            f"5. 実験・観察・調査のいずれかのジャンルで多様性を持たせてください\n\n"
            f"**重要：genre値について**\n"
            f"genreフィールドには必ず以下の値のいずれかを使用してください：\n"
            f"- \"experiment\": 実験を行うテーマ（何かを作る、試す、検証する）\n"
            f"- \"observation\": 観察するテーマ（自然や現象を観察・記録する）\n"
            f"- \"research\": 調査するテーマ（文献調査、アンケート、データ収集）\n"
            f"これ以外の値は使用しないでください。\n\n"
            f"以下のJSON形式で必ず回答してください。```json ``` で囲んでください：\n\n"
            f"""```json
[
  {{
    "title": "具体的で魅力的なテーマタイトル",
    "description": "テーマの詳しい説明（何を調べるか、どんな発見が期待できるか）",
    "genre": "experiment",
    "materials": ["必要な材料1", "材料2", "材料3"],
    "steps": ["手順1", "手順2", "手順3", "手順4", "手順5"],
    "estimatedDays": 7,
    "difficulty": "medium"
  }},
  {{
    "title": "2つ目のテーマタイトル",
    "description": "2つ目のテーマの説明",
    "genre": "observation",
    "materials": ["材料1", "材料2"],
    "steps": ["手順1", "手順2", "手順3"],
    "estimatedDays": 14,
    "difficulty": "easy"
  }},
  {{
    "title": "3つ目のテーマタイトル",
    "description": "3つ目のテーマの説明",
    "genre": "research",
    "materials": ["材料1", "材料2"],
    "steps": ["手順1", "手順2", "手順3"],
    "estimatedDays": 10,
    "difficulty": "hard"
  }}
]
```"""
        )

        return prompt

    def build_research_plan_prompt(self, theme: ResearchTheme, user_profile: UserProfile = None):
        """
        保存されたテーマを基に、詳細な研究計画を生成するプロンプトを作成する
        """
        genre_label = self.genre_labels.get(theme.genre, theme.genre)

        # ユーザープロフィールがある場合は学年情報を追加
        grade_info = ""
        if user_profile:
            grade = self.grade_labels.get(user_profile.grade, user_profile.grade)
            grade_info = f"学年: {grade}\n"

        prompt = (
            f"あなたは自由研究の学習指導専門家です。\n\n"
            f"以下の自由研究テーマについて、子供が段階的に取り組めるよう詳細な研究計画を作成してください：\n\n"
            f"=== 研究テーマ情報 ===\n"
            f"テーマ: {theme.title}\n"
            f"説明: {theme.description}\n"
            f"ジャンル: {genre_label}（{theme.genre}）\n"
            f"推定日数: {theme.estimated_days}日\n"
            f"難易度: {theme.difficulty}\n"
            f"{grade_info}"
            f"必要な材料: {', '.join(theme.materials)}\n"
            f"基本手順: {', '.join(theme.steps)}\n\n"
            f"=== 作成する研究計画の要件 ===\n"
            f"1. 子供が理解しやすい段階的なステップに分割してください\n"
            f"2. 各ステップには具体的な作業内容と達成目標を含めてください\n"
            f"3. 各ステップの実践的なコツやアドバイスを含めてください\n"
            f"4. 研究の流れが自然で論理的になるよう配慮してください\n"
            f"5. 安全性や実現可能性を考慮してください\n\n"
            f"**重要**: 必ず以下のJSON形式で回答してください。```json ``` で囲んでください。\n"
            f"他の説明文は一切含めず、JSONのみを返してください：\n\n"
            f"""```json
{{
  "steps": [
    {{
      "title": "ステップ1のタイトル",
      "description": "このステップで何をするか、なぜ重要かの詳細説明",
      "tips": [
        "実践的なコツ1",
        "注意点やアドバイス2",
        "うまくいかない場合の対処法3"
      ],
      "duration": "1-2日",
      "order": 1
    }},
    {{
      "title": "ステップ2のタイトル",
      "description": "このステップの詳細説明",
      "tips": [
        "コツ1",
        "コツ2",
        "コツ3"
      ],
      "duration": "2-3日",
      "order": 2
    }}
  ]
}}
```

上記のようなJSON形式で、5-7個のステップを作成してください。"""
        )

        return prompt
