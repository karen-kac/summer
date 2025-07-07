from models.theme import UserProfile


class PromptBuilder:
    def __init__(self):
        pass

    def build_suggest_themes_prompt(self, profile: UserProfile):
        grade = profile.grade.label
        interests = [i.label for i in profile.interests]
        personality = [p.label for p in profile.personality]
        strengths = [s.label for s in profile.strengths]
        duration = profile.duration.label

        prompt = (
            f"あなたは自由研究の研究テーマを提案する専門家です。\n"
            f"学年: {grade}\n"
            f"興味: {', '.join(interests)}\n"
            f"性格: {', '.join(personality)}\n"
            f"得意なこと: {', '.join(strengths)}\n"
            f"研究期間: {duration}\n"
            "これらの情報を基に、自由研究の研究テーマを3つ提案し、以下の例のようにjsonファイル形式に変換してください。\n"
            "ただし、difficultyは難易度に応じて'easy','medium','hard'を割り振ってください。\n"
            """
            {
                title: 'pH指示薬を使った酸性・アルカリ性の研究',
                description: '身近な食材を使って天然のpH指示薬を作り、様々な液体の酸性・アルカリ性を調べる実験です。',
                materials: ['紫キャベツ', 'レモン汁', '重曹', 'お酢', '石鹸水', 'コップ', 'スポイト'],
                steps: ['紫キャベツを煮出して指示薬を作る', '様々な液体のpHを測定', '色の変化を記録', '結果をグラフにまとめる', '考察を書く'],
                estimated_days: 5,
                difficulty: 'easy' | 'medium' | 'hard' as const
            }
            """
        )
        return prompt
