import boto3
import os
from botocore.exceptions import ClientError
from typing import Dict, Optional
import logging
import hmac
import hashlib
import base64
from functools import lru_cache

from .auth_repository import AuthRepository

logger = logging.getLogger(__name__)

class CognitoAuthRepository(AuthRepository):
    """AWS Cognito認証リポジトリ"""

    def __init__(self):
        self.client = boto3.client(
            'cognito-idp',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.user_pool_id = os.getenv('COGNITO_USER_POOL_ID')
        self.client_id = os.getenv('COGNITO_CLIENT_ID')
        self.client_secret = os.getenv('COGNITO_CLIENT_SECRET')

    def sign_up(self, name: str, email: str, password: str) -> Dict:
        """新規ユーザー登録（メール検証なし）"""
        try:
            user_attributes = [
                {'Name': 'email', 'Value': email},
                {'Name': 'email_verified', 'Value': 'true'}  # メール検証済みとして設定
            ]

            # Admin APIを使用してユーザーを直接作成（確認済み状態で）
            response = self.client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=name,  # nameをusernameとして使用（Email alias設定に対応）
                UserAttributes=user_attributes,
                TemporaryPassword=password,
                MessageAction='SUPPRESS'  # メール送信を抑制
            )

            # 一時パスワードを永続パスワードに設定
            self.client.admin_set_user_password(
                UserPoolId=self.user_pool_id,
                Username=name,  # nameをusernameとして使用
                Password=password,
                Permanent=True
            )

            logger.info(f"User {name} (email: {email}) signed up successfully without email verification")
            return {
                'success': True,
                'user_sub': response['User']['Username'],
                'confirmation_required': False  # 確認不要
            }

        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Sign up failed for {name} (email: {email}): {error_code}")
            return {
                'success': False,
                'error': error_code,
                'message': e.response['Error']['Message']
            }

        except Exception as e:
            logger.error(f"Sign up failed for {name} (email: {email}): {str(e)}")
            return {
                'success': False,
                'error': 'InternalError',
                'message': 'An unexpected error occurred during sign up.'
            }

    def confirm_sign_up(self, username: str, confirmation_code: str) -> Dict:
        """メール確認（スキップ - 常に成功を返す）"""
        logger.info(f"Email confirmation skipped for {username}")
        return {
            'success': True,
            'message': 'Email confirmation not required'
        }

    def sign_in(self, username: str, password: str) -> Dict:
        """ユーザーサインイン（ユーザー情報も同時に取得）"""
        try:
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password,
                    'SECRET_HASH': self._get_secret_hash(username)
                }
            )

            # MFA等のチャレンジが必要な場合
            if 'ChallengeName' in response:
                return {
                    'success': True,
                    'challenge_required': True,
                    'challenge_name': response['ChallengeName'],
                    'session': response['Session']
                }

            # 正常にサインイン完了
            auth_result = response['AuthenticationResult']
            access_token = auth_result['AccessToken']
            
            # ユーザー情報も同時に取得してレスポンスに含める
            try:
                user_response = self.client.get_user(AccessToken=access_token)
                user_attributes = {}
                for attr in user_response['UserAttributes']:
                    user_attributes[attr['Name']] = attr['Value']
                
                user_info = {
                    'username': user_response['Username'],
                    'attributes': user_attributes
                }
            except ClientError as user_error:
                logger.warning(f"Failed to get user info during sign in: {user_error}")
                user_info = None

            logger.info(f"User {username} signed in successfully")

            result = {
                'success': True,
                'access_token': access_token,
                'id_token': auth_result['IdToken'],
                'refresh_token': auth_result['RefreshToken'],
                'expires_in': auth_result['ExpiresIn']
            }
            
            # ユーザー情報が取得できた場合は含める
            if user_info:
                result['user_info'] = user_info

            return result

        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Sign in failed for {username}: {error_code}")
            return {
                'success': False,
                'error': error_code,
                'message': e.response['Error']['Message']
            }

    def refresh_token(self, refresh_token: str, username: str) -> Dict:
        """リフレッシュトークンで新しいアクセストークンを取得"""
        try:
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='REFRESH_TOKEN_AUTH',
                AuthParameters={
                    'REFRESH_TOKEN': refresh_token,
                    'SECRET_HASH': self._get_secret_hash(username)
                }
            )

            auth_result = response['AuthenticationResult']
            return {
                'success': True,
                'access_token': auth_result['AccessToken'],
                'id_token': auth_result['IdToken'],
                'expires_in': auth_result['ExpiresIn']
            }

        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Token refresh failed: {error_code}")
            return {
                'success': False,
                'error': error_code,
                'message': e.response['Error']['Message']
            }

    def get_user_info(self, access_token: str) -> Dict:
        """アクセストークンからユーザー情報を取得"""
        try:
            response = self.client.get_user(AccessToken=access_token)

            user_attributes = {}
            for attr in response['UserAttributes']:
                user_attributes[attr['Name']] = attr['Value']

            return {
                'success': True,
                'username': response['Username'],
                'attributes': user_attributes
            }

        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Get user info failed: {error_code}")
            return {
                'success': False,
                'error': error_code,
                'message': e.response['Error']['Message']
            }

    def sign_out(self, access_token: str) -> Dict:
        """ユーザーサインアウト"""
        try:
            self.client.global_sign_out(AccessToken=access_token)
            return {'success': True}

        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Sign out failed: {error_code}")
            return {
                'success': False,
                'error': error_code,
                'message': e.response['Error']['Message']
            }

    def forgot_password(self, username: str) -> Dict:
        """パスワードリセット開始"""
        try:
            self.client.forgot_password(
                ClientId=self.client_id,
                Username=username,
                SecretHash=self._get_secret_hash(username)
            )

            return {'success': True}

        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Forgot password failed for {username}: {error_code}")
            return {
                'success': False,
                'error': error_code,
                'message': e.response['Error']['Message']
            }

    def confirm_forgot_password(self, username: str, confirmation_code: str, new_password: str) -> Dict:
        """パスワードリセット確定"""
        try:
            self.client.confirm_forgot_password(
                ClientId=self.client_id,
                Username=username,
                ConfirmationCode=confirmation_code,
                Password=new_password,
                SecretHash=self._get_secret_hash(username)
            )

            return {'success': True}

        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Confirm forgot password failed for {username}: {error_code}")
            return {
                'success': False,
                'error': error_code,
                'message': e.response['Error']['Message']
            }

    @lru_cache(maxsize=128)
    def _get_secret_hash(self, username: str) -> str:
        """SECRET_HASHを生成（Client Secretが設定されている場合）"""
        if not self.client_secret:
            return ""

        message = username + self.client_id
        dig = hmac.new(
            str(self.client_secret).encode('utf-8'),
            msg=str(message).encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()

        return base64.b64encode(dig).decode()
