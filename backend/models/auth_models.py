# backend/models/auth_models.py

# シンプルなデータクラスとして定義します。
# FastAPIを使用する場合はpydantic.BaseModelを継承します。

class LoginRequest:
    """
    ログインリクエストのデータモデル
    """
    def __init__(self, email: str, password: str):
        if not isinstance(email, str) or not isinstance(password, str):
            raise TypeError("Email and password must be strings.")
        self.email = email
        self.password = password

    def to_dict(self):
        return {"email": self.email, "password": self.password}

# 将来的にユーザー登録リクエストやパスワードリセットリクエストのモデルもここに追加できます
class SignupRequest(LoginRequest):
    """
    新規登録リクエストのデータモデル
    (必要に応じて追加のフィールドを定義)
    """
    pass

class ResetPasswordRequest:
    """
    パスワードリセットリクエストのデータモデル
    """
    def __init__(self, email: str):
        if not isinstance(email, str):
            raise TypeError("Email must be a string.")
        self.email = email

    def to_dict(self):
        return {"email": self.email}

