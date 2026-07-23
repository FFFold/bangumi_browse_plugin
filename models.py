"""Bangumi 浏览插件数据模型。"""

from __future__ import annotations

from typing import Any, Optional, Union

from pydantic import BaseModel, field_validator


_SUBJECT_TYPE_MAP: dict[int, str] = {
    1: "book",
    2: "anime",
    3: "music",
    4: "game",
    6: "real",
}


def _to_type_name(v: object) -> str:
    if isinstance(v, int):
        return _SUBJECT_TYPE_MAP.get(v, str(v))
    return str(v or "")


class RatingInfo(BaseModel):
    score: float = 0.0
    total: int = 0


class ImageInfo(BaseModel):
    large: str = ""
    common: str = ""
    medium: str = ""
    small: str = ""
    grid: str = ""


class Subject(BaseModel):
    """搜索结果/列表中的条目摘要。"""

    id: int
    name: str = ""
    name_cn: str = ""
    type: str = ""
    summary: str = ""
    date: str = ""
    eps: int = 0
    rating: Optional[RatingInfo] = None
    rank: int = 0
    images: Optional[ImageInfo] = None

    @field_validator("type", mode="before")
    @classmethod
    def _normalize_type(cls, v: object) -> str:
        return _to_type_name(v)


class SubjectDetail(Subject):
    """单部作品完整信息。"""

    platform: str = ""
    infobox: list[dict[str, Any]] = []
    tags: list[dict[str, Any]] = []
    collection: dict[str, int] = {}

    @property
    def score(self) -> float:
        if self.rating:
            return self.rating.score
        return 0.0

    @property
    def score_count(self) -> int:
        if self.rating:
            return self.rating.total
        return 0


class SubjectPerson(BaseModel):
    """制作人员。"""

    id: int
    name: str = ""
    images: Optional[ImageInfo] = None
    relation: str = ""
    type: str = ""
    career: list[str] = []
    positions: list[str] = []

    @field_validator("type", mode="before")
    @classmethod
    def _normalize_type(cls, v: object) -> str:
        return _to_type_name(v)


class Episode(BaseModel):
    """剧集列表项。"""

    id: int
    type: int = 0
    name: str = ""
    name_cn: str = ""
    sort: float = 0.0
    ep: Optional[int] = None
    airdate: str = ""
    comment: int = 0
    duration: str = ""
    desc: str = ""
    subject_id: int = 0


class SubjectRelation(BaseModel):
    """关联作品。"""

    id: int
    name: str = ""
    name_cn: str = ""
    images: Optional[ImageInfo] = None
    relation: str = ""


class CalendarItem(BaseModel):
    """每日放送中的单部动画。"""

    subject_id: int
    name: str = ""
    name_cn: str = ""
    time: str = ""
    cover: str = ""


class CalendarDay(BaseModel):
    """单日放送安排。"""

    weekday: str = ""
    date: str = ""
    items: list[CalendarItem] = []


class EpisodeComment(BaseModel):
    """单集吐槽箱评论。"""

    username: str = ""
    score: str = ""
    content: str = ""
    time: str = ""


class ReviewSummary(BaseModel):
    """作品长评列表项。"""

    review_id: int
    title: str = ""
    author: str = ""
    time: str = ""
    score: int = 0
    summary: str = ""


class ReviewDetail(BaseModel):
    """单篇长评完整内容。"""

    review_id: int
    title: str = ""
    author: str = ""
    time: str = ""
    score: int = 0
    content: str = ""
