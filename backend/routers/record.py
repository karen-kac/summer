from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
from datetime import date, datetime
from repositories.repository_factory import get_repository_factory
from repositories.record_repository import RecordRepository
from models.record import (
    CreateRecordRequest, UpdateRecordRequest, RecordResponse, RecordListResponse,
    WeatherInfo, LocationInfo
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def get_record_repository() -> RecordRepository:
    """記録リポジトリを取得"""
    factory = get_repository_factory()
    return factory.get_record_repository()


@router.post("/create", response_model=RecordResponse)
async def create_record(
    request: CreateRecordRequest,
    user_id: str = Query(..., description="ユーザーID"),
    record_repo: RecordRepository = Depends(get_record_repository)
) -> RecordResponse:
    """
    新しい研究記録を作成

    Args:
        request: 記録作成リクエスト
        user_id: ユーザーID（クエリパラメータ）
        record_repo: 記録リポジトリ

    Returns:
        RecordResponse: 作成された記録情報
    """
    try:
        # 記録日付が未指定の場合は今日の日付を使用
        if not request.recordDate:
            request.recordDate = date.today()

        # 記録時間が未指定の場合は現在時刻を使用
        if not request.recordTime:
            request.recordTime = datetime.now().strftime("%H:%M")

        # 記録を作成
        record_response = await record_repo.create_record(user_id, request)

        if not record_response:
            logger.error(f"記録作成失敗: ユーザーID={user_id}, プロジェクトID={request.projectId}")
            raise HTTPException(
                status_code=500,
                detail="記録の作成に失敗しました"
            )

        logger.info(f"記録作成成功: {record_response.record.recordId}")
        return record_response

    except Exception as e:
        logger.error(f"記録作成エラー: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"記録作成中にエラーが発生しました: {str(e)}"
        )


@router.get("/project/{project_id}", response_model=RecordListResponse)
async def get_records_by_project(
    project_id: str,
    limit: int = Query(20, description="取得件数の上限"),
    last_evaluated_key: Optional[str] = Query(None, description="ページネーション用キー"),
    record_repo: RecordRepository = Depends(get_record_repository)
) -> RecordListResponse:
    """
    プロジェクトの記録一覧を取得

    Args:
        project_id: プロジェクトID
        limit: 取得件数の上限
        last_evaluated_key: ページネーション用キー
        record_repo: 記録リポジトリ

    Returns:
        RecordListResponse: 記録一覧
    """
    try:
        # ページネーション用キーを処理
        pagination_key = None
        if last_evaluated_key:
            try:
                import ast
                pagination_key = ast.literal_eval(last_evaluated_key)
            except Exception:
                logger.warning(f"無効なページネーション用キー: {last_evaluated_key}")

        # 記録一覧を取得
        records_response = await record_repo.get_records_by_project(
            project_id=project_id,
            limit=limit,
            last_evaluated_key=pagination_key
        )

        logger.info(f"プロジェクト記録取得成功: {project_id} - {len(records_response.records)}件")
        return records_response

    except Exception as e:
        logger.error(f"プロジェクト記録取得エラー: {project_id}, {e}")
        raise HTTPException(
            status_code=500,
            detail=f"記録取得中にエラーが発生しました: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=RecordListResponse)
async def get_records_by_user(
    user_id: str,
    limit: int = Query(20, description="取得件数の上限"),
    last_evaluated_key: Optional[str] = Query(None, description="ページネーション用キー"),
    record_repo: RecordRepository = Depends(get_record_repository)
) -> RecordListResponse:
    """
    ユーザーの記録一覧を取得

    Args:
        user_id: ユーザーID
        limit: 取得件数の上限
        last_evaluated_key: ページネーション用キー
        record_repo: 記録リポジトリ

    Returns:
        RecordListResponse: 記録一覧
    """
    try:
        # ページネーション用キーを処理
        pagination_key = None
        if last_evaluated_key:
            try:
                import ast
                pagination_key = ast.literal_eval(last_evaluated_key)
            except Exception:
                logger.warning(f"無効なページネーション用キー: {last_evaluated_key}")

        # 記録一覧を取得
        records_response = await record_repo.get_records_by_user(
            user_id=user_id,
            limit=limit,
            last_evaluated_key=pagination_key
        )

        logger.info(f"ユーザー記録取得成功: {user_id} - {len(records_response.records)}件")
        return records_response

    except Exception as e:
        logger.error(f"ユーザー記録取得エラー: {user_id}, {e}")
        raise HTTPException(
            status_code=500,
            detail=f"記録取得中にエラーが発生しました: {str(e)}"
        )


@router.get("/date/{record_date}", response_model=RecordListResponse)
async def get_records_by_date(
    record_date: date,
    limit: int = Query(20, description="取得件数の上限"),
    last_evaluated_key: Optional[str] = Query(None, description="ページネーション用キー"),
    record_repo: RecordRepository = Depends(get_record_repository)
) -> RecordListResponse:
    """
    日付の記録一覧を取得

    Args:
        record_date: 記録日付
        limit: 取得件数の上限
        last_evaluated_key: ページネーション用キー
        record_repo: 記録リポジトリ

    Returns:
        RecordListResponse: 記録一覧
    """
    try:
        # ページネーション用キーを処理
        pagination_key = None
        if last_evaluated_key:
            try:
                import ast
                pagination_key = ast.literal_eval(last_evaluated_key)
            except Exception:
                logger.warning(f"無効なページネーション用キー: {last_evaluated_key}")

        # 記録一覧を取得
        records_response = await record_repo.get_records_by_date(
            record_date=record_date,
            limit=limit,
            last_evaluated_key=pagination_key
        )

        logger.info(f"日付記録取得成功: {record_date} - {len(records_response.records)}件")
        return records_response

    except Exception as e:
        logger.error(f"日付記録取得エラー: {record_date}, {e}")
        raise HTTPException(
            status_code=500,
            detail=f"記録取得中にエラーが発生しました: {str(e)}"
        )


@router.put("/update", response_model=Dict[str, Any])
async def update_record(
    project_id: str = Query(..., description="プロジェクトID"),
    record_date: date = Query(..., description="記録日付"),
    sequence: str = Query(..., description="シーケンス番号"),
    request: UpdateRecordRequest = ...,
    record_repo: RecordRepository = Depends(get_record_repository)
) -> Dict[str, Any]:
    """
    記録を更新

    Args:
        project_id: プロジェクトID
        record_date: 記録日付
        sequence: シーケンス番号
        request: 更新リクエスト
        record_repo: 記録リポジトリ

    Returns:
        Dict[str, Any]: 更新結果
    """
    try:
        # 記録を更新
        success = await record_repo.update_record(project_id, record_date, sequence, request)

        if not success:
            raise HTTPException(
                status_code=500,
                detail="記録の更新に失敗しました"
            )

        logger.info(f"記録更新成功: {project_id} - {record_date} - {sequence}")
        return {
            "success": True,
            "message": "記録が正常に更新されました"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"記録更新エラー: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"記録更新中にエラーが発生しました: {str(e)}"
        )


@router.delete("/delete", response_model=Dict[str, Any])
async def delete_record(
    project_id: str = Query(..., description="プロジェクトID"),
    record_date: date = Query(..., description="記録日付"),
    sequence: str = Query(..., description="シーケンス番号"),
    record_repo: RecordRepository = Depends(get_record_repository)
) -> Dict[str, Any]:
    """
    記録を削除

    Args:
        project_id: プロジェクトID
        record_date: 記録日付
        sequence: シーケンス番号
        record_repo: 記録リポジトリ

    Returns:
        Dict[str, Any]: 削除結果
    """
    try:
        # 記録を削除
        success = await record_repo.delete_record(project_id, record_date, sequence)

        if not success:
            raise HTTPException(
                status_code=500,
                detail="記録の削除に失敗しました"
            )

        logger.info(f"記録削除成功: {project_id} - {record_date} - {sequence}")
        return {
            "success": True,
            "message": "記録が正常に削除されました"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"記録削除エラー: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"記録削除中にエラーが発生しました: {str(e)}"
        )
