import boto3
import json
import base64
from typing import List, Optional, Dict, Any
from models.chat import ChatMessage, ChatResponse, MessageType
import os
from pathlib import Path

class ChatService:
    def __init__(self):
        self.bedrock = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('BEDROCK_REGION', 'us-east-1')
        )
        self.model_id = os.getenv('BEDROCK_MODEL_ID')
    
    async def process_chat_message(self, user_id: str, project_id: str, message: str, 
                                 message_type: MessageType = MessageType.TEXT, 
                                 media_url: Optional[str] = None) -> ChatResponse:
        
        # プロジェクト情報を取得（進捗把握のため）
        project_context = await self._get_project_context(project_id)
        
        # メディアファイルがある場合は解析
        media_analysis = None
        if media_url and message_type != MessageType.TEXT:
            media_analysis = await self._analyze_media(media_url, message_type)
        
        # AIレスポンス生成
        ai_response = await self._generate_ai_response(
            message, project_context, media_analysis
        )
        
        return ChatResponse(
            message=ai_response["message"],
            suggestions=ai_response.get("suggestions"),
            media_analysis=media_analysis
        )
    
    def _load_research_plans(self) -> List[Dict[str, Any]]:
        """JSONファイルから研究計画を読み込み"""
        try:
            json_path = Path(__file__).parent.parent / "saved_research_plans.json"
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"JSONファイル読み込みエラー: {e}")
        return []
    
    async def _get_project_context(self, project_id: str) -> dict:
        try:
            # JSONファイルから研究計画を取得
            research_plans = self._load_research_plans()
            
            # project_idに対応する研究計画を検索
            current_plan = None
            for plan_data in research_plans:
                plan = plan_data.get("plan", {})
                if plan.get("theme_id") == project_id or project_id in plan.get("theme_title", ""):
                    current_plan = plan
                    break
            
            # 最新の研究計画を使用（フォールバック）
            if not current_plan and research_plans:
                current_plan = research_plans[-1].get("plan", {})
            
            if current_plan:
                steps = current_plan.get("steps", [])
                total_steps = len(steps)
                
                # 現在のステップを仮定（実際の進捗管理がある場合はそちらを使用）
                current_step_index = 0  # デフォルトは最初のステップ
                progress = (current_step_index / total_steps) * 100 if total_steps > 0 else 0
                
                # 進捗からフェーズを判定
                if progress < 20:
                    phase = "theme_selection"
                elif progress < 50:
                    phase = "observation"
                elif progress < 80:
                    phase = "experiment"
                else:
                    phase = "report"
                
                current_step = steps[current_step_index] if current_step_index < len(steps) else {}
                
                return {
                    "phase": phase,
                    "progress": progress,
                    "theme": current_plan.get("theme_title", "研究テーマ"),
                    "title": current_plan.get("theme_title", "研究プロジェクト"),
                    "status": "in_progress",
                    "description": current_step.get("description", ""),
                    "currentStep": current_step_index,
                    "currentStepTitle": current_step.get("title", ""),
                    "currentStepTips": current_step.get("tips", []),
                    "totalSteps": total_steps,
                    "difficulty": current_plan.get("difficulty", "medium"),
                    "genre": current_plan.get("genre", "experiment"),
                    "estimatedDays": current_plan.get("total_estimated_days", 0)
                }
            
        except Exception as e:
            print(f"プロジェクト情報取得エラー: {e}")
        
        # フォールバック
        return {
            "phase": "planning",
            "progress": 0,
            "theme": "研究テーマ",
            "title": "研究プロジェクト",
            "status": "planning"
        }
    
    async def _analyze_media(self, media_url: str, media_type: MessageType) -> str:
        if media_type == MessageType.IMAGE:
            prompt = """
            この画像を自由研究の観点から分析してください。
            - 何が写っているか
            - 研究に役立つポイント
            - 改善提案
            小学生にもわかりやすく説明してください。
            """
        else:
            return "音声ファイルの解析機能は準備中です。"
        
        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 500,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            
            result = json.loads(response['body'].read())
            return result['content'][0]['text']
        except Exception as e:
            return f"画像解析でエラーが発生しました: {str(e)}"
    
    async def _generate_ai_response(self, message: str, project_context: dict, 
                                  media_analysis: Optional[str] = None) -> dict:
        
        phase = project_context.get("phase", "theme_selection")
        theme = project_context.get("theme", "未設定")
        
        # 進捗に応じたプロンプト
        phase_prompts = {
            "theme_selection": "テーマ選びをサポートする優しいAI先生として回答してください。",
            "observation": "観察記録をサポートする先生として、観察のコツやポイントを教えてください。",
            "experiment": "実験をサポートする先生として、安全で楽しい実験方法を提案してください。",
            "report": "レポート作成をサポートする先生として、まとめ方のコツを教えてください。"
        }
        
        # 現在のステップ情報を取得
        current_step_info = ""
        if project_context.get('currentStepTitle'):
            current_step_info = f"""
        【現在のステップ詳細】
        - ステップ名: {project_context.get('currentStepTitle')}
        - ステップ説明: {project_context.get('description', '')}
        - ポイント: {', '.join(project_context.get('currentStepTips', []))}
        """
        
        system_prompt = f"""
        あなたは小学生の自由研究をサポートするAI先生です。
        
        【現在の研究情報】
        - 研究タイトル: {project_context.get('title', '未設定')}
        - 研究テーマ: {theme}
        - 研究タイプ: {project_context.get('genre', 'experiment')}
        - 難易度: {project_context.get('difficulty', 'medium')}
        - 予定日数: {project_context.get('estimatedDays', 0)}日
        - 進捗状況: {project_context.get('progress', 0):.1f}%
        - 現在のフェーズ: {phase}
        - ステータス: {project_context.get('status', 'planning')}
        - 現在のステップ: {project_context.get('currentStep', 0) + 1}/{project_context.get('totalSteps', 1)}
        {current_step_info}
        
        {phase_prompts.get(phase, "優しくサポートしてください。")}
        
        以下の点を心がけてください：
        - 小学生にもわかりやすい言葉で説明
        - 現在のステップと進捗状況を考慮した具体的なアドバイス
        - 安全性を最優先
        - 子どもの好奇心を刺激する内容
        - 次に何をすべきかを明確に提案
        - 現在のステップのポイントを参考にアドバイス
        """
        
        user_content = message
        if media_analysis:
            user_content += f"\n\n画像解析結果: {media_analysis}"
        
        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 800,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_content}]
                })
            )
            
            result = json.loads(response['body'].read())
            ai_message = result['content'][0]['text']
            
            # 提案を抽出（簡単な実装）
            suggestions = self._extract_suggestions(ai_message, phase)
            
            return {
                "message": ai_message,
                "suggestions": suggestions
            }
            
        except Exception as e:
            return {
                "message": f"申し訳ありません。エラーが発生しました: {str(e)}",
                "suggestions": ["もう一度試してみてください"]
            }
    
    def _extract_suggestions(self, message: str, phase: str) -> List[str]:
        # 簡単な提案抽出（実際はより高度な処理が必要）
        suggestions = {
            "theme_selection": ["興味のあることを教えて", "得意なことは何？", "どんな実験をしてみたい？"],
            "observation": ["写真を撮ってみよう", "毎日記録をつけよう", "変化に気づいたことを教えて"],
            "experiment": ["安全に実験しよう", "結果を予想してみよう", "なぜそうなったか考えてみよう"],
            "report": ["観察結果をまとめよう", "グラフを作ってみよう", "感想を書いてみよう"]
        }
        return suggestions.get(phase, ["頑張って続けよう！"])