"""Bangumi 动漫高手插件数据模型。"""

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


_PERSON_TYPE_MAP: dict[int, str] = {
    1: "个人",
    2: "组织",
    3: "组合",
}

_PERSON_RELATION_PRIORITY: dict[str, int] = {
    # 核心主创
    "导演": 0, "副导演": 1,
    "原作": 2, "原案": 3,
    "系列构成": 4, "系列构成": 4,
    # 脚本
    "脚本": 10, "剧本": 10, "脚本协力": 11,
    # 分镜 / 演出 / 构图
    "分镜": 15, "绘コンテ": 15,
    "演出": 16, "演出助理": 17,
    "构图": 18,
    # 人物 / 机械 / 道具设定
    "人物设定": 25, "角色设计": 25,
    "人物原案": 26, "角色原案": 26,
    "副人物设定": 27,
    "机械设定": 28,
    "道具设计": 29,
    # 作画
    "总作画监督": 35,
    "作画监督": 36, "动作作画监督": 36, "机械作画监督": 36,
    "作画监督助理": 37,
    "主动画师": 38,
    "原画": 39, "第二原画": 40,
    # 美术 / 背景
    "美术监督": 50, "美术设计": 51, "美术板": 52,
    "背景美术": 53, "背景": 53,
    # 色彩 / 上色
    "色彩设计": 60, "色彩指定": 61, "色彩检查": 62,
    "上色": 63, "色指定": 61,
    # 摄影 / 特效
    "摄影": 70, "摄影监督": 70,
    "特效": 71,
    # 剪辑
    "剪辑": 80, "编集": 80,
    # 音响 / 录音
    "音响监督": 85, "音响": 86,
    "音效": 87,
    "音响制作担当": 88,
    "录音": 89, "录音工作室": 90, "录音助理": 91,
    # 音乐
    "音乐": 95, "音乐监督": 96,
    "音乐制作": 97, "音乐制作人": 98,
    "主题歌作曲": 100, "主题歌作词": 101, "主题歌编曲": 102,
    "主题歌演出": 103, "插入歌演出": 104,
    # OP / ED 影像
    "OP・ED 分镜": 110, "OP・ED 演出": 111,
    # 动画制作 / 設定 / 进行
    "动画制作": 115, "动画制片人": 116,
    "设定制作": 117, "设定": 117,
    "文艺制作": 118,
    "制作进行": 119,
    # 製作 / 制片 / 管理
    "製作": 125, "制作": 126,
    "总制片人": 127, "制片人": 128,
    "执行制片人": 129,
    "助理制片人": 130,
    "制作管理": 131,
    "制作协力": 132,
    "制作统括": 133,
    # CG / 3D / 设计
    "CG 导演": 140, "3DCG": 140,
    "2D 设计": 141,
    # 补间 / 检查
    "补间动画": 150, "动画检查": 151, "动画": 150,
    # 企画 / 宣传
    "企画": 160, "宣传": 161,
    # 辅助 / 协力
    "协力": 170,
}


class SubjectPerson(BaseModel):
    """制作人员。"""

    id: int
    name: str = ""
    images: Optional[ImageInfo] = None
    relation: str = ""
    type: str = ""
    career: list[str] = []
    positions: list[str] = []
    eps: str = ""

    @field_validator("type", mode="before")
    @classmethod
    def _normalize_type(cls, v: object) -> str:
        if isinstance(v, int):
            return _PERSON_TYPE_MAP.get(v, str(v))
        return str(v or "")


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
