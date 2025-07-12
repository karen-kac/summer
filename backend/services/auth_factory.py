import os
from typing import Optional

from repositories.cognito_auth_repository import CognitoAuthRepository
from services.auth_service import AuthService

# Import mock repository only when needed for testing
def _get_mock_repository():
    """Lazy import of mock repository to avoid production dependencies"""
    try:
        from tests.repositories.mock_auth_repository import MockAuthRepository
        return MockAuthRepository()
    except ImportError:
        raise ImportError("Mock repository not available. This should only be used in test environment.")

class AuthServiceFactory:
    """認証サービスのファクトリークラス"""
    
    _instance: Optional[AuthService] = None
    _test_instance: Optional[AuthService] = None
    
    @classmethod
    def get_auth_service(cls, use_mock: bool = False) -> AuthService:
        """認証サービスのインスタンスを取得"""
        if use_mock:
            if cls._test_instance is None:
                mock_repository = _get_mock_repository()
                cls._test_instance = AuthService(mock_repository)
            return cls._test_instance
        else:
            if cls._instance is None:
                cognito_repository = CognitoAuthRepository()
                cls._instance = AuthService(cognito_repository)
            return cls._instance
    
    @classmethod
    def get_production_service(cls) -> AuthService:
        """本番用認証サービスを取得"""
        return cls.get_auth_service(use_mock=False)
    
    @classmethod
    def get_test_service(cls) -> AuthService:
        """テスト用認証サービスを取得"""
        return cls.get_auth_service(use_mock=True)
    
    @classmethod
    def reset_instances(cls):
        """インスタンスをリセット（テスト用）"""
        cls._instance = None
        cls._test_instance = None
