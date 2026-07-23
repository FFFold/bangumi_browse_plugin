"""Bangumi REST API 客户端（只读）。"""

from __future__ import annotations

from typing import Any, Optional

import httpx

from .models import Episode, Subject, SubjectDetail, SubjectPerson, SubjectRelation


API_BASE = "https://api.bgm.tv/v0"

_TYPE_MAP: dict[str, int] = {
    "anime": 2,
    "book": 1,
    "music": 3,
    "game": 4,
    "real": 6,
}


class BangumiAPIError(Exception):
    pass


class BangumiAPI:
    """Bangumi OpenAPI v0 只读客户端。"""

    def __init__(self, client: httpx.AsyncClient, timeout: int = 15) -> None:
        self._client = client
        self._timeout = timeout

    async def _get(self, path: str, **params: Any) -> Any:
        try:
            resp = await self._client.get(
                f"{API_BASE}{path}",
                params=params,
                timeout=self._timeout,
            )
        except httpx.TimeoutException:
            raise BangumiAPIError("请求 Bangumi API 超时，请稍后重试")
        except httpx.RequestError as e:
            raise BangumiAPIError(f"请求 Bangumi API 失败: {e}")
        if resp.status_code == 404:
            raise BangumiAPIError("未找到该条目，请检查 ID 是否正确")
        if resp.status_code >= 400:
            detail = ""
            try:
                detail = resp.text[:200]
            except Exception:
                pass
            raise BangumiAPIError(f"Bangumi API 返回错误 (HTTP {resp.status_code}): {detail}")
        return resp.json()

    async def _post(self, path: str, body: dict[str, Any], **params: Any) -> Any:
        try:
            resp = await self._client.post(
                f"{API_BASE}{path}",
                json=body,
                params=params,
                timeout=self._timeout,
            )
        except httpx.TimeoutException:
            raise BangumiAPIError("请求 Bangumi API 超时，请稍后重试")
        except httpx.RequestError as e:
            raise BangumiAPIError(f"请求 Bangumi API 失败: {e}")
        if resp.status_code >= 400:
            detail = ""
            try:
                detail = resp.text[:200]
            except Exception:
                pass
            raise BangumiAPIError(f"Bangumi API 返回错误 (HTTP {resp.status_code}): {detail}")
        return resp.json()

    async def search_subjects(
        self,
        keyword: str,
        subject_type: Optional[str] = None,
        sort: str = "match",
        limit: int = 10,
        offset: int = 0,
    ) -> list[Subject]:
        """搜索条目。"""
        body: dict[str, Any] = {
            "keyword": keyword,
            "sort": sort,
        }
        if subject_type:
            type_id = _TYPE_MAP.get(subject_type)
            if type_id:
                body["filter"] = {"type": [type_id]}

        data = await self._post("/search/subjects", body, limit=limit, offset=offset)
        items: list[dict[str, Any]] = data.get("data", [])
        return [Subject(**item) for item in items]

    async def get_subject(self, subject_id: int) -> SubjectDetail:
        """获取条目详情。"""
        data = await self._get(f"/subjects/{subject_id}")
        return SubjectDetail(**data)

    async def get_subject_persons(self, subject_id: int) -> list[SubjectPerson]:
        """获取条目制作人员。"""
        data = await self._get(f"/subjects/{subject_id}/persons")
        return [SubjectPerson(**item) for item in data]

    async def browse_subjects(
        self,
        subject_type: str = "anime",
        year: Optional[int] = None,
        month: Optional[int] = None,
        sort: str = "date",
        limit: int = 20,
        offset: int = 0,
        cat: Optional[int] = 1,
    ) -> list[Subject]:
        """浏览条目（按季度等筛选）。"""
        type_int = _TYPE_MAP.get(subject_type, 2)
        params: dict[str, Any] = {
            "type": type_int,
            "sort": sort,
            "limit": limit,
            "offset": offset,
        }
        if year is not None:
            params["year"] = year
        if month is not None:
            params["month"] = month
        if cat is not None:
            params["cat"] = cat

        data = await self._get("/subjects", **params)
        items: list[dict[str, Any]] = data.get("data", [])
        return [Subject(**item) for item in items]

    async def get_episodes(
        self,
        subject_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Episode]:
        """获取剧集列表。"""
        data = await self._get(
            "/episodes",
            subject_id=subject_id,
            limit=limit,
            offset=offset,
        )
        items: list[dict[str, Any]] = data.get("data", [])
        return [Episode(**item) for item in items]

    async def get_subject_relations(self, subject_id: int) -> list[SubjectRelation]:
        """获取关联作品。"""
        data = await self._get(f"/subjects/{subject_id}/subjects")
        return [SubjectRelation(**item) for item in data]
