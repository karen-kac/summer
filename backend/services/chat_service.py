import json
from typing import List, Optional, Dict, Any
from models.chat import ChatMessage, ChatResponse, MessageType
from pathlib import Path
from utils.prompt_builder import PromptBuilder
from repositories.client.bedrock_client import BedrockClient
from repositories.client.dynamodb_client import get_dynamodb_client
from repositories.theme_repository import ThemeRepository

class ChatService:
    def __init__(self):
        prompt_builder = PromptBuilder()
        bedrock_client = BedrockClient()
        self.db_client = get_dynamodb_client()
        self.theme_repository = ThemeRepository(prompt_builder, bedrock_client, self.db_client)
    
    async def process_chat_message(self, user_id: str, project_id: str, message: str, 
                                 message_type: MessageType = MessageType.TEXT, 
                                 media_url: Optional[str] = None) -> ChatResponse:
        
        try:
            print(f"チャットメッセージ処理開始: user_id={user_id}, project_id={project_id}, message={message[:50]}...")
            
            # プロジェクト情報を取得（進捗把握のため）
            project_context = await self._get_project_context(project_id)
            print(f"プロジェクトコンテキスト取得完了: {project_context}")
            
            # メディアファイルがある場合は解析
            media_analysis = None
            if media_url and message_type != MessageType.TEXT:
                media_analysis = await self._analyze_media(media_url, message_type)
            
            # AIレスポンス生成
            print("AIレスポンス生成開始")
            ai_message = await self.theme_repository.process_chat_message(
                message, project_context, media_analysis
            )
            print(f"AIレスポンス生成完了: {ai_message[:100]}...")
            
            # 提案を抽出
            suggestions = self._extract_suggestions(ai_message, project_context.get('phase', 'planning'))
            
            return ChatResponse(
                message=ai_message,
                suggestions=suggestions,
                media_analysis=media_analysis
            )
            
        except Exception as e:
            print(f"チャットメッセージ処理エラー: {e}")
            import traceback
            traceback.print_exc()
            
            return ChatResponse(
                message="申し訳ありません。エラーが発生しました。もう一度お試しください。",
                suggestions=["もう一度試してみてください"],
                media_analysis=None
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
    
    async def _get_project_progress_percentage(self, project_id: str) -> float:
        """プロジェクトの進捗率をDynamoDBから取得"""
        try:
            # DynamoDBからプロジェクト情報を取得
            project_key = f"PROJECT#{project_id}"
            project_data = await self.db_client.get_item(
                pk=project_key,
                sk="METADATA"
            )
            
            if project_data:
                return project_data.get("progressPercentage", 0.0)
            else:
                print(f"プロジェクトが見つかりません: {project_id}")
                return 0.0
                
        except Exception as e:
            print(f"進捗率取得エラー: {e}")
            return 0.0
    
    async def _get_project_context(self, project_id: str) -> dict:
        try:
            print(f"プロジェクト情報取得開始: {project_id}")
            
            # DynamoDBからプロジェクト情報を取得
            project_key = f"PROJECT#{project_id}"
            project_data = await self.db_client.get_item(
                pk=project_key,
                sk="METADATA"
            )
            
            print(f"DynamoDBから取得したプロジェクトデータ: {project_data}")
            
            if not project_data:
                print(f"プロジェクトが見つかりません: {project_id}")
                return self._get_fallback_context()
            
            # 基本情報を取得
            progress = float(project_data.get("progressPercentage", 0.0))
            current_step_index = int(project_data.get("currentStepIndex", 0))
            title = project_data.get("title", "研究プロジェクト")
            status = project_data.get("status", "in_progress")
            theme_id = project_data.get("themeId", "")
            
            print(f"基本情報: progress={progress}, step={current_step_index}, title={title}")
            
            # JSONファイルから研究計画を取得
            research_plans = self._load_research_plans()
            current_plan = None
            
            # テーマIDで研究計画を検索
            for plan_data in research_plans:
                plan = plan_data.get("plan", {})
                if plan.get("theme_id") == theme_id:
                    current_plan = plan
                    break
            
            # 見つからない場合は最新の計画を使用
            if not current_plan and research_plans:
                current_plan = research_plans[-1].get("plan", {})
                print(f"最新の研究計画を使用: {current_plan.get('theme_title', 'Unknown')}")
            
            if not current_plan:
                print("研究計画が見つかりません")
                return self._get_fallback_context()
            
            steps = current_plan.get("steps", [])
            total_steps = len(steps)
            
            # インデックスの安全な範囲チェック
            print(f"ステップ情報: total_steps={total_steps}, current_step_index={current_step_index}")
            if total_steps > 0:
                current_step_index = max(0, min(int(current_step_index), total_steps - 1))
            else:
                current_step_index = 0
            print(f"調整後のステップインデックス: {current_step_index}")
            
            # 進捗からフェーズを判定
            if progress < 20:
                phase = "theme_selection"
            elif progress < 50:
                phase = "observation"
            elif progress < 80:
                phase = "experiment"
            else:
                phase = "report"
            
            # 現在のステップ情報を安全に取得
            current_step = {"title": "", "description": "", "tips": []}
            try:
                print(f"ステップデータ確認: steps type={type(steps)}, length={len(steps) if isinstance(steps, list) else 'N/A'}")
                if steps and isinstance(steps, list) and len(steps) > 0:
                    safe_index = max(0, min(int(current_step_index), len(steps) - 1))
                    step_data = steps[safe_index]
                    print(f"取得したステップデータ: {step_data}")
                    if isinstance(step_data, dict):
                        current_step = {
                            "title": step_data.get("title", ""),
                            "description": step_data.get("description", ""),
                            "tips": step_data.get("tips", [])
                        }
                    print(f"ステップ情報取得: index={safe_index}, step={current_step.get('title', 'Unknown')}")
            except Exception as step_error:
                print(f"ステップ情報取得エラー: {step_error}")
                current_step = {"title": "", "description": "", "tips": []}
            
            result = {
                "phase": phase,
                "progress": progress,
                "theme": current_plan.get("theme_title", "研究テーマ"),
                "title": title,
                "status": status,
                "description": current_step.get("description", ""),
                "currentStep": current_step_index,
                "currentStepTitle": current_step.get("title", ""),
                "currentStepTips": current_step.get("tips", []),
                "totalSteps": total_steps,
                "difficulty": current_plan.get("difficulty", "medium"),
                "genre": current_plan.get("genre", "experiment"),
                "estimatedDays": current_plan.get("total_estimated_days", 0)
            }
            
            print(f"プロジェクト情報取得成功: {result}")
            return result
            
        except Exception as e:
            print(f"プロジェクト情報取得エラー: {e}")
            import traceback
            traceback.print_exc()
            return self._get_fallback_context()
    
    def _get_fallback_context(self) -> dict:
        """フォールバック用のコンテキスト"""
        return {
            "phase": "planning",
            "progress": 0.0,
            "theme": "研究テーマ",
            "title": "研究プロジェクト",
            "status": "planning",
            "description": "",
            "currentStep": 0,
            "currentStepTitle": "",
            "currentStepTips": [],
            "totalSteps": 1,
            "difficulty": "medium",
            "genre": "experiment",
            "estimatedDays": 0
        }
    
    async def _analyze_media(self, media_url: str, media_type: MessageType) -> str:
        if media_type == MessageType.IMAGE:
            return "画像解析機能は現在準備中です。"
        else:
            return "音声ファイルの解析機能は準備中です。"
    

    
    def _extract_suggestions(self, message: str, phase: str) -> List[str]:
        # 簡単な提案抽出（実際はより高度な処理が必要）
        suggestions = {
            "theme_selection": ["興味のあることを教えて", "得意なことは何？", "どんな実験をしてみたい？"],
            "observation": ["写真を撮ってみよう", "毎日記録をつけよう", "変化に気づいたことを教えて"],
            "experiment": ["安全に実験しよう", "結果を予想してみよう", "なぜそうなったか考えてみよう"],
            "report": ["観察結果をまとめよう", "グラフを作ってみよう", "感想を書いてみよう"]
        }
        return suggestions.get(phase, ["頑張って続けよう！"])