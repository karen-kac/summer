import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid

from models.line_models import LineUserConnection, LineUserProfile

logger = logging.getLogger(__name__)


class LineRepository:
    """LINE連携データを管理するリポジトリ"""

    def __init__(self):
        # 本来はデータベース接続を行うが、ここでは一時的にメモリストレージを使用
        self._connections: Dict[str, LineUserConnection] = {}
        self._user_line_map: Dict[str, str] = {}  # user_id -> line_user_id
        self._line_user_map: Dict[str, str] = {}  # line_user_id -> user_id

    async def create_connection(
        self,
        user_id: str,
        line_user_id: str,
        display_name: Optional[str] = None,
        picture_url: Optional[str] = None
    ) -> LineUserConnection:
        """新しいLINE連携を作成"""
        connection_id = str(uuid.uuid4())
        connection = LineUserConnection(
            id=connection_id,
            user_id=user_id,
            line_user_id=line_user_id,
            display_name=display_name,
            picture_url=picture_url,
            is_active=True,
            connected_at=datetime.now(timezone.utc),
            last_interaction_at=datetime.now(timezone.utc)
        )

        # 既存の連携があれば無効化
        existing_connection = await self.get_connection_by_user_id(user_id)
        if existing_connection:
            await self.deactivate_connection(existing_connection.id)

        # 新しい連携を保存
        self._connections[connection_id] = connection
        self._user_line_map[user_id] = line_user_id
        self._line_user_map[line_user_id] = user_id

        logger.info(f"LINE connection created: user_id={user_id}, line_user_id={line_user_id}")
        return connection

    async def get_connection_by_id(self, connection_id: str) -> Optional[LineUserConnection]:
        """ID で連携情報を取得"""
        return self._connections.get(connection_id)

    async def get_connection_by_user_id(self, user_id: str) -> Optional[LineUserConnection]:
        """ユーザーID で連携情報を取得"""
        line_user_id = self._user_line_map.get(user_id)
        if not line_user_id:
            return None

        # アクティブな連携のみを返す
        for connection in self._connections.values():
            if connection.user_id == user_id and connection.line_user_id == line_user_id and connection.is_active:
                return connection

        return None

    async def get_connection_by_line_user_id(self, line_user_id: str) -> Optional[LineUserConnection]:
        """LINE ユーザーID で連携情報を取得"""
        user_id = self._line_user_map.get(line_user_id)
        if not user_id:
            return None

        # アクティブな連携のみを返す
        for connection in self._connections.values():
            if connection.line_user_id == line_user_id and connection.user_id == user_id and connection.is_active:
                return connection

        return None

    async def update_last_interaction(self, connection_id: str) -> bool:
        """最終インタラクション時刻を更新"""
        connection = self._connections.get(connection_id)
        if not connection:
            return False

        connection.last_interaction_at = datetime.now(timezone.utc)
        logger.debug(f"Updated last interaction for connection: {connection_id}")
        return True

    async def update_profile_info(
        self,
        connection_id: str,
        display_name: Optional[str] = None,
        picture_url: Optional[str] = None
    ) -> bool:
        """プロフィール情報を更新"""
        connection = self._connections.get(connection_id)
        if not connection:
            return False

        if display_name is not None:
            connection.display_name = display_name
        if picture_url is not None:
            connection.picture_url = picture_url

        logger.debug(f"Updated profile info for connection: {connection_id}")
        return True

    async def deactivate_connection(self, connection_id: str) -> bool:
        """連携を無効化"""
        connection = self._connections.get(connection_id)
        if not connection:
            return False

        connection.is_active = False

        # マップからも削除
        if connection.user_id in self._user_line_map:
            del self._user_line_map[connection.user_id]
        if connection.line_user_id in self._line_user_map:
            del self._line_user_map[connection.line_user_id]

        logger.info(f"LINE connection deactivated: {connection_id}")
        return True

    async def get_all_active_connections(self) -> List[LineUserConnection]:
        """すべてのアクティブな連携を取得"""
        return [conn for conn in self._connections.values() if conn.is_active]

    async def get_connections_by_user_ids(self, user_ids: List[str]) -> List[LineUserConnection]:
        """指定したユーザーIDの連携情報を取得"""
        connections = []
        for user_id in user_ids:
            connection = await self.get_connection_by_user_id(user_id)
            if connection:
                connections.append(connection)
        return connections

    async def is_user_connected(self, user_id: str) -> bool:
        """ユーザーがLINEに連携済みかチェック"""
        connection = await self.get_connection_by_user_id(user_id)
        return connection is not None and connection.is_active

    async def is_line_user_connected(self, line_user_id: str) -> bool:
        """LINEユーザーが連携済みかチェック"""
        connection = await self.get_connection_by_line_user_id(line_user_id)
        return connection is not None and connection.is_active


# グローバルインスタンス（本来はDIコンテナで管理）
line_repository = LineRepository()
