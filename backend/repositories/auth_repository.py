from abc import ABC, abstractmethod
from typing import Dict, Optional

class AuthRepository(ABC):
    """認証リポジトリのベースクラス"""

    @abstractmethod
    def sign_up(self, name: str, email: str, password: str) -> Dict:
        """新規ユーザー登録"""
        pass

    @abstractmethod
    def confirm_sign_up(self, username: str, confirmation_code: str) -> Dict:
        """メール確認コードでユーザー登録を確定"""
        pass

    @abstractmethod
    def sign_in(self, username: str, password: str) -> Dict:
        """ユーザーサインイン"""
        pass

    @abstractmethod
    def refresh_token(self, refresh_token: str, username: str) -> Dict:
        """リフレッシュトークンで新しいアクセストークンを取得"""
        pass

    @abstractmethod
    def get_user_info(self, access_token: str) -> Dict:
        """アクセストークンからユーザー情報を取得"""
        pass

    @abstractmethod
    def sign_out(self, access_token: str) -> Dict:
        """ユーザーサインアウト"""
        pass

    @abstractmethod
    def forgot_password(self, username: str) -> Dict:
        """パスワードリセット開始"""
        pass

    @abstractmethod
    def confirm_forgot_password(self, username: str, confirmation_code: str, new_password: str) -> Dict:
        """パスワードリセット確定"""
        pass
