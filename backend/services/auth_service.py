from typing import Dict, Optional
import logging

from repositories.auth_repository import AuthRepository

logger = logging.getLogger(__name__)

class AuthService:
    """認証サービス層"""

    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    def register_user(self, name: str, email: str, password: str) -> Dict:
        """ユーザー登録（name, email, passwordのみ）"""
        # ビジネスロジックの検証
        if not self._validate_name(name):
            return {
                'success': False,
                'error': 'InvalidNameException',
                'message': 'Name must be at least 2 characters long.'
            }

        if not self._validate_password(password):
            return {
                'success': False,
                'error': 'InvalidPasswordException',
                'message': 'Password must be at least 8 characters long and contain at least one number.'
            }

        if not self._validate_email(email):
            return {
                'success': False,
                'error': 'InvalidEmailException',
                'message': 'Please provide a valid email address.'
            }

        # Cognitoには name(username), email, password のみ送信
        return self.auth_repository.sign_up(name, email, password)

    def confirm_registration(self, username: str, confirmation_code: str) -> Dict:
        """ユーザー登録確認（メール検証スキップ）"""
        return self.auth_repository.confirm_sign_up(username, confirmation_code)

    def authenticate_user(self, username: str, password: str) -> Dict:
        """ユーザー認証"""
        if not username or not password:
            return {
                'success': False,
                'error': 'InvalidCredentialsException',
                'message': 'Username and password are required.'
            }

        return self.auth_repository.sign_in(username, password)

    def refresh_user_token(self, refresh_token: str, username: str) -> Dict:
        """トークンリフレッシュ"""
        if not refresh_token or not username:
            return {
                'success': False,
                'error': 'InvalidTokenException',
                'message': 'Refresh token and username are required.'
            }

        return self.auth_repository.refresh_token(refresh_token, username)

    def get_user_profile(self, access_token: str) -> Dict:
        """ユーザープロフィール取得"""
        if not access_token:
            return {
                'success': False,
                'error': 'InvalidTokenException',
                'message': 'Access token is required.'
            }

        return self.auth_repository.get_user_info(access_token)

    def logout_user(self, access_token: str) -> Dict:
        """ユーザーログアウト"""
        if not access_token:
            return {
                'success': False,
                'error': 'InvalidTokenException',
                'message': 'Access token is required.'
            }

        return self.auth_repository.sign_out(access_token)

    def initiate_password_reset(self, username: str) -> Dict:
        """パスワードリセット開始"""
        if not username:
            return {
                'success': False,
                'error': 'InvalidUsernameException',
                'message': 'Username is required.'
            }

        return self.auth_repository.forgot_password(username)

    def confirm_password_reset(self, username: str, confirmation_code: str, new_password: str) -> Dict:
        """パスワードリセット確認"""
        if not confirmation_code or len(confirmation_code) != 6:
            return {
                'success': False,
                'error': 'InvalidCodeException',
                'message': 'Confirmation code must be 6 digits.'
            }

        if not self._validate_password(new_password):
            return {
                'success': False,
                'error': 'InvalidPasswordException',
                'message': 'Password must be at least 8 characters long and contain at least one number.'
            }

        return self.auth_repository.confirm_forgot_password(username, confirmation_code, new_password)

    def _validate_name(self, name: str) -> bool:
        """名前のバリデーション"""
        if not name or len(name) < 2:
            return False
        return True

    def _validate_username(self, username: str) -> bool:
        """ユーザー名のバリデーション（email対応）"""
        if not username or len(username) < 3:
            return False

        # emailの場合は@を含むかチェック
        if '@' in username:
            return self._validate_email(username)

        # 通常のユーザー名の場合は英数字のみ許可
        return username.isalnum()

    def _validate_password(self, password: str) -> bool:
        """パスワードのバリデーション"""
        if not password or len(password) < 8:
            return False

        # 少なくとも1つの数字を含む
        return any(char.isdigit() for char in password)

    def _validate_email(self, email: str) -> bool:
        """メールアドレスの簡易バリデーション"""
        if not email or '@' not in email:
            return False

        parts = email.split('@')
        if len(parts) != 2:
            return False

        local, domain = parts
        if not local or not domain or '.' not in domain:
            return False

        return True
