import json
from typing import List, Optional, Dict, Any
from models.chat import ChatMessage, ChatResponse, MessageType
from pathlib import Path
from utils.prompt_builder import PromptBuilder
from repositories.client.bedrock_client import BedrockClient
from repositories.theme_repository import ThemeRepository

class ChatService:
    def __init__(self):
        prompt_builder = PromptBuilder()
        bedrock_client = BedrockClient()
        self.theme_repository = ThemeRepository(prompt_builder, bedrock_client)
    
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
        ai_message = await self.theme_repository.process_chat_message(
            message, project_context, media_analysis
        )
        
        # 提案を抽出
        suggestions = self._extract_suggestions(ai_message, project_context.get('phase', 'planning'))
        
        return ChatResponse(
            message=ai_message,
            suggestions=suggestions,
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
    
    def _get_project_progress_percentage(self, project_id: str) -> float:
        """プロジェクトの進捗率を取得"""
        try:
            # 実際のプロジェクトデータからprogressPercentageを取得
            # ここではデモ用に30%を返す（実装時はDynamoDBから取得）
            return 30.0
        except Exception as e:
            print(f"進捗率取得エラー: {e}")
            return 0.0
    
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
                
                # project.progressPercentageから現在のステップを計算
                project_progress = self._get_project_progress_percentage(project_id)
                current_step_index = int((project_progress / 100) * total_steps) if total_steps > 0 else 0
                current_step_index = min(current_step_index, total_steps - 1)  # 範囲制限
                progress = project_progress
                
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
    

    
    def _extract_suggestions(self, message: str, phase: str) -> List[str]:
        # 簡単な提案抽出（実際はより高度な処理が必要）
        suggestions = {
            "theme_selection": ["興味のあることを教えて", "得意なことは何？", "どんな実験をしてみたい？"],
            "observation": ["写真を撮ってみよう", "毎日記録をつけよう", "変化に気づいたことを教えて"],
            "experiment": ["安全に実験しよう", "結果を予想してみよう", "なぜそうなったか考えてみよう"],
            "report": ["観察結果をまとめよう", "グラフを作ってみよう", "感想を書いてみよう"]
        }
        return suggestions.get(phase, ["頑張って続けよう！"])