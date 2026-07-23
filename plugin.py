"""Bangumi 浏览插件 — 为 MaiBot 提供 Bangumi 条目浏览能力。"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx

from maibot_sdk import Field, MaiBotPlugin, PluginConfigBase, Tool
from maibot_sdk.types import ToolParameterInfo, ToolParamType

from .bangumi_api import BangumiAPI, BangumiAPIError
from .bangumi_html import (
    BangumiHTMLError,
    fetch_calendar,
    fetch_episode_comments,
    fetch_review_detail,
    fetch_reviews_list,
)


# ---------------------------------------------------------------------------
# 配置模型
# ---------------------------------------------------------------------------


class PluginSection(PluginConfigBase):
    """插件基础配置。"""

    __ui_label__ = "插件"
    __ui_icon__ = "package"
    __ui_order__ = 0

    enabled: bool = Field(default=True, description="是否启用插件")
    config_version: str = Field(default="1.0.0", description="配置版本")


class RequestSection(PluginConfigBase):
    """请求配置。"""

    __ui_label__ = "请求"
    __ui_icon__ = "globe"
    __ui_order__ = 1

    timeout: int = Field(default=15, description="HTTP 请求超时（秒）")
    user_agent: str = Field(
        default="FFFold/bangumi-browse-plugin (https://github.com/FFFold/bangumi_browse_plugin)",
        description="Bangumi API 要求的 User-Agent，需包含项目链接",
    )
    proxy: str = Field(default="", description="HTTP 代理地址，留空则不使用")


class BangumiBrowseConfig(PluginConfigBase):
    """Bangumi 浏览插件配置。"""

    plugin: PluginSection = Field(default_factory=PluginSection)
    request: RequestSection = Field(default_factory=RequestSection)


# ---------------------------------------------------------------------------
# 插件类
# ---------------------------------------------------------------------------


class BangumiBrowsePlugin(MaiBotPlugin):
    """Bangumi 浏览插件。"""

    config_model = BangumiBrowseConfig

    _client: httpx.AsyncClient | None = None
    _api: BangumiAPI | None = None

    async def on_load(self) -> None:
        cfg = self.config.request
        self._client = httpx.AsyncClient(
            headers={"User-Agent": cfg.user_agent},
            proxy=cfg.proxy or None,
            follow_redirects=True,
        )
        self._api = BangumiAPI(self._client, timeout=cfg.timeout)
        self.ctx.logger.info("Bangumi 浏览插件已加载")

    async def on_unload(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
        self._api = None
        self.ctx.logger.info("Bangumi 浏览插件已卸载")

    async def on_config_update(self, scope: str, config_data: dict[str, Any], version: str) -> None:
        del scope
        del config_data
        del version
        if self._client:
            await self._client.aclose()
        cfg = self.config.request
        self._client = httpx.AsyncClient(
            headers={"User-Agent": cfg.user_agent},
            proxy=cfg.proxy or None,
            follow_redirects=True,
        )
        self._api = BangumiAPI(self._client, timeout=cfg.timeout)
        self.ctx.logger.info("Bangumi 浏览插件配置已热更新")

    # ----------------------------------------------------------------
    # Tool 1: search_bangumi_subject
    # ----------------------------------------------------------------

    @Tool(
        "search_bangumi_subject",
        description=(
            "在 Bangumi 搜索动画/游戏/书籍/音乐等条目。"
            "当用户想找某部作品、或需要获取作品 ID 以进行后续查询时使用。"
            "返回条目列表，包含 ID、名称、中文名、类型、评分等信息。"
        ),
        parameters=[
            ToolParameterInfo(
                name="keyword",
                param_type=ToolParamType.STRING,
                description="搜索关键词，例如作品名、作者名等",
                required=True,
            ),
            ToolParameterInfo(
                name="subject_type",
                param_type=ToolParamType.STRING,
                description="条目类型，可选值: anime(动画), real(真人), game(游戏), book(书籍), music(音乐)。不传则不限类型",
                required=False,
            ),
            ToolParameterInfo(
                name="sort",
                param_type=ToolParamType.STRING,
                description="排序方式: match(匹配度), heat(热度), rank(排名), score(评分)。默认 match",
                required=False,
            ),
            ToolParameterInfo(
                name="limit",
                param_type=ToolParamType.INTEGER,
                description="返回数量，默认 10",
                required=False,
            ),
        ],
    )
    async def handle_search_subject(self, keyword: str = "", **kwargs: Any) -> dict[str, str]:
        try:
            if not self._api:
                return {"name": "search_bangumi_subject", "content": "插件未初始化"}
            subject_type = kwargs.get("subject_type") or None
            sort = str(kwargs.get("sort") or "match")
            limit_val = kwargs.get("limit")
            limit = int(limit_val) if limit_val is not None else 10
            subjects = await self._api.search_subjects(
                keyword=keyword,
                subject_type=subject_type,
                sort=sort,
                limit=limit,
            )
            if not subjects:
                return {"name": "search_bangumi_subject", "content": f"未找到与「{keyword}」相关的条目。"}
            lines = [f"搜索「{keyword}」的结果："]
            for s in subjects:
                rating_str = f" 评分{s.rating.score}" if s.rating and s.rating.total > 0 else ""
                eps_str = f" {s.eps}集" if s.eps else ""
                lines.append(f"  [{s.id}] {s.name_cn or s.name} ({s.type}){rating_str}{eps_str}")
            return {"name": "search_bangumi_subject", "content": "\n".join(lines)}
        except BangumiAPIError as e:
            return {"name": "search_bangumi_subject", "content": str(e)}
        except Exception as e:
            self.ctx.logger.error("search_bangumi_subject 异常: %s", e, exc_info=True)
            return {"name": "search_bangumi_subject", "content": f"搜索失败: {e}"}

    # ----------------------------------------------------------------
    # Tool 2: get_bangumi_subject
    # ----------------------------------------------------------------

    @Tool(
        "get_bangumi_subject",
        description=(
            "获取单部作品的完整信息，包括名称、放送日期、集数、评分、排名、简介、标签等。"
            "当用户想了解某部具体作品的详细信息时使用。subject_id 可通过 search_bangumi_subject 获取。"
        ),
        parameters=[
            ToolParameterInfo(
                name="subject_id",
                param_type=ToolParamType.INTEGER,
                description="Bangumi 条目 ID",
                required=True,
            ),
        ],
    )
    async def handle_get_subject(self, subject_id: int = 0, **kwargs: Any) -> dict[str, str]:
        del kwargs
        try:
            if not self._api:
                return {"name": "get_bangumi_subject", "content": "插件未初始化"}
            s = await self._api.get_subject(subject_id)
            lines = [
                f"【{s.name_cn or s.name}】",
            ]
            if s.name_cn and s.name != s.name_cn:
                lines.append(f"原名: {s.name}")
            lines.append(f"类型: {s.type}")
            if s.date:
                lines.append(f"放送/发售日期: {s.date}")
            if s.eps:
                lines.append(f"集数: {s.eps}")
            if s.score_count:
                lines.append(f"评分: {s.score} ({s.score_count}人评分)")
            else:
                lines.append("评分: 暂无")
            if s.rank:
                lines.append(f"排名: #{s.rank}")
            if s.platform:
                lines.append(f"平台: {s.platform}")
            if s.summary:
                lines.append(f"\n简介: {s.summary}")
            if s.tags:
                tag_names = [t.get("name", "") for t in s.tags[:10] if isinstance(t, dict) and t.get("name")]
                if tag_names:
                    lines.append(f"\n标签: {', '.join(tag_names)}")
            return {"name": "get_bangumi_subject", "content": "\n".join(lines)}
        except BangumiAPIError as e:
            return {"name": "get_bangumi_subject", "content": str(e)}
        except Exception as e:
            self.ctx.logger.error("get_bangumi_subject 异常: %s", e, exc_info=True)
            return {"name": "get_bangumi_subject", "content": f"获取条目信息失败: {e}"}

    # ----------------------------------------------------------------
    # Tool 3: get_bangumi_subject_persons
    # ----------------------------------------------------------------

    @Tool(
        "get_bangumi_subject_persons",
        description=(
            "获取某部作品的制作人员阵容，包括监督、脚本、音乐、原画、CV 等。"
            "当用户想了解某部作品是谁制作的、或谈论制作团队时使用。"
        ),
        parameters=[
            ToolParameterInfo(
                name="subject_id",
                param_type=ToolParamType.INTEGER,
                description="Bangumi 条目 ID",
                required=True,
            ),
        ],
    )
    async def handle_get_persons(self, subject_id: int = 0, **kwargs: Any) -> dict[str, str]:
        del kwargs
        try:
            if not self._api:
                return {"name": "get_bangumi_subject_persons", "content": "插件未初始化"}
            persons = await self._api.get_subject_persons(subject_id)
            if not persons:
                return {"name": "get_bangumi_subject_persons", "content": "未找到该条目的人员信息。"}

            by_relation: dict[str, list[str]] = {}
            for p in persons:
                rel = p.relation or "其他"
                line = p.name
                if p.positions:
                    line += f"（{'/'.join(p.positions)}）"
                by_relation.setdefault(rel, []).append(line)

            lines = ["制作人员："]
            for rel, names in by_relation.items():
                lines.append(f"\n{rel}:")
                for name in names[:20]:
                    lines.append(f"  {name}")
            return {"name": "get_bangumi_subject_persons", "content": "\n".join(lines)}
        except BangumiAPIError as e:
            return {"name": "get_bangumi_subject_persons", "content": str(e)}
        except Exception as e:
            self.ctx.logger.error("get_bangumi_subject_persons 异常: %s", e, exc_info=True)
            return {"name": "get_bangumi_subject_persons", "content": f"获取人员信息失败: {e}"}

    # ----------------------------------------------------------------
    # Tool 4: get_bangumi_season
    # ----------------------------------------------------------------

    @Tool(
        "get_bangumi_season",
        description=(
            "获取某季度的放送/发售列表，默认按放送日期排序，默认仅返回 TV 动画。"
            "当用户问'这季度有什么新番'、'某年某月有什么动画'时使用。"
        ),
        parameters=[
            ToolParameterInfo(
                name="year",
                param_type=ToolParamType.INTEGER,
                description="年份，例如 2026",
                required=True,
            ),
            ToolParameterInfo(
                name="month",
                param_type=ToolParamType.INTEGER,
                description="月份（1-12），不传则查全年",
                required=False,
            ),
            ToolParameterInfo(
                name="subject_type",
                param_type=ToolParamType.STRING,
                description="条目类型，可选: anime(动画), game(游戏), book(书籍), music(音乐)。默认 anime",
                required=False,
            ),
            ToolParameterInfo(
                name="category",
                param_type=ToolParamType.STRING,
                description="分类 (仅 anime 有效): 0=Other, 1=TV(默认), 2=OVA, 3=Movie, 5=WEB, all=全部",
                required=False,
            ),
            ToolParameterInfo(
                name="limit",
                param_type=ToolParamType.INTEGER,
                description="返回数量，默认 20",
                required=False,
            ),
        ],
    )
    async def handle_get_season(self, year: int = 0, **kwargs: Any) -> dict[str, str]:
        try:
            if not self._api:
                return {"name": "get_bangumi_season", "content": "插件未初始化"}
            if not year:
                year = datetime.now().year
            month = kwargs.get("month")
            month_int = int(month) if month is not None else None
            subject_type = str(kwargs.get("subject_type") or "anime")
            _cat_raw = kwargs.get("category")
            if _cat_raw is not None and str(_cat_raw).strip().lower() == "all":
                cat = None
            else:
                cat = int(_cat_raw) if _cat_raw is not None else 1
            limit_val = kwargs.get("limit")
            limit = int(limit_val) if limit_val is not None else 20

            subjects = await self._api.browse_subjects(
                subject_type=subject_type,
                year=year,
                month=month_int,
                cat=cat,
                limit=limit,
            )
            if not subjects:
                period = f"{year}年{month_int}月" if month_int else f"{year}年"
                return {"name": "get_bangumi_season", "content": f"未找到 {period} 的{subject_type}条目。"}

            period = f"{year}年{month_int}月" if month_int else f"{year}年"
            lines = [f"{period} {subject_type} 放送/发售列表："]
            for s in subjects:
                rating_str = f" 评分{s.rating.score}" if s.rating and s.rating.total > 0 else ""
                eps_str = f" {s.eps}集" if s.eps else ""
                date_str = f" ({s.date})" if s.date else ""
                lines.append(f"  [{s.id}] {s.name_cn or s.name}{eps_str}{rating_str}{date_str}")
            return {"name": "get_bangumi_season", "content": "\n".join(lines)}
        except BangumiAPIError as e:
            return {"name": "get_bangumi_season", "content": str(e)}
        except Exception as e:
            self.ctx.logger.error("get_bangumi_season 异常: %s", e, exc_info=True)
            return {"name": "get_bangumi_season", "content": f"获取季度列表失败: {e}"}

    # ----------------------------------------------------------------
    # Tool 5: get_bangumi_calendar
    # ----------------------------------------------------------------

    @Tool(
        "get_bangumi_calendar",
        description=(
            "获取本周（周一到周日）的每日动画放送时间表。"
            "当用户问'今天有什么动画更新'、'这周放什么'时使用。"
            "注意：该功能通过解析 Bangumi 网页实现，页面结构变更可能导致暂时不可用。"
        ),
        parameters=[],
    )
    async def handle_get_calendar(self, **kwargs: Any) -> dict[str, str]:
        del kwargs
        try:
            if not self._client:
                return {"name": "get_bangumi_calendar", "content": "插件未初始化"}
            cfg = self.config.request
            days = await fetch_calendar(self._client, timeout=cfg.timeout)
            if not days:
                return {"name": "get_bangumi_calendar", "content": "未获取到本周放送信息。"}

            lines = ["本周动画放送时间表："]
            for day in days:
                if not day.items:
                    continue
                lines.append(f"\n{'='*4} {day.weekday} {'='*4}")
                for item in day.items:
                    name = item.name_cn or item.name or "未知"
                    lines.append(f"  [{item.subject_id}] {name}")
            return {"name": "get_bangumi_calendar", "content": "\n".join(lines)}
        except BangumiHTMLError as e:
            return {"name": "get_bangumi_calendar", "content": str(e)}
        except Exception as e:
            self.ctx.logger.error("get_bangumi_calendar 异常: %s", e, exc_info=True)
            return {"name": "get_bangumi_calendar", "content": f"获取放送表失败: {e}"}

    # ----------------------------------------------------------------
    # Tool 6: get_bangumi_episodes
    # ----------------------------------------------------------------

    @Tool(
        "get_bangumi_episodes",
        description=(
            "获取某部作品的剧集列表，包含集号、日文名、中文名、放送日期、评论数等信息。"
            "当用户想了解一部动画有哪些集数、或通过集数找到 episode_id 以查看吐槽箱时使用。"
        ),
        parameters=[
            ToolParameterInfo(
                name="subject_id",
                param_type=ToolParamType.INTEGER,
                description="Bangumi 条目 ID",
                required=True,
            ),
            ToolParameterInfo(
                name="ep_type",
                param_type=ToolParamType.STRING,
                description="剧集类型: 0=本篇, 1=SP, 2=OP, 3=ED, 4=PV, 5=MAD, 6=Other, all=全部(默认)",
                required=False,
            ),
            ToolParameterInfo(
                name="limit",
                param_type=ToolParamType.INTEGER,
                description="返回数量，默认 50",
                required=False,
            ),
        ],
    )
    async def handle_get_episodes(self, subject_id: int = 0, **kwargs: Any) -> dict[str, str]:
        try:
            if not self._api:
                return {"name": "get_bangumi_episodes", "content": "插件未初始化"}
            _ep_raw = kwargs.get("ep_type")
            if _ep_raw is not None and str(_ep_raw).strip().lower() == "all":
                ep_type = None
            else:
                ep_type = int(_ep_raw) if _ep_raw is not None else None
            limit_val = kwargs.get("limit")
            limit = int(limit_val) if limit_val is not None else 50
            episodes = await self._api.get_episodes(subject_id, limit=limit, ep_type=ep_type)
            if not episodes:
                return {"name": "get_bangumi_episodes", "content": "未找到该条目的剧集信息。"}

            lines = ["剧集列表："]
            for ep in episodes:
                ep_label = f"EP{ep.ep}" if ep.ep is not None else f"SP{int(ep.sort)}" if ep.type > 0 else f"#{int(ep.sort)}"
                name = ep.name_cn or ep.name
                airdate_str = f" 放送: {ep.airdate}" if ep.airdate else ""
                comment_str = f" {ep.comment}条评论" if ep.comment else ""
                type_str = f" [{ep.type}]" if ep.type else ""
                lines.append(f"  [{ep.id}] {ep_label} {name}{type_str}{airdate_str}{comment_str}")
            return {"name": "get_bangumi_episodes", "content": "\n".join(lines)}
        except BangumiAPIError as e:
            return {"name": "get_bangumi_episodes", "content": str(e)}
        except Exception as e:
            self.ctx.logger.error("get_bangumi_episodes 异常: %s", e, exc_info=True)
            return {"name": "get_bangumi_episodes", "content": f"获取剧集列表失败: {e}"}

    # ----------------------------------------------------------------
    # Tool 7: get_bangumi_episode_comments
    # ----------------------------------------------------------------

    @Tool(
        "get_bangumi_episode_comments",
        description=(
            "获取单集动画的吐槽箱评论。episode_id 可通过 get_bangumi_episodes 获取。"
            "当用户想了解某集的口碑、他人评价时使用。"
            "注意：该功能通过解析 Bangumi 网页实现，页面结构变更可能导致暂时不可用。"
        ),
        parameters=[
            ToolParameterInfo(
                name="episode_id",
                param_type=ToolParamType.INTEGER,
                description="Bangumi 剧集 ID（非 subject_id）",
                required=True,
            ),
            ToolParameterInfo(
                name="limit",
                param_type=ToolParamType.INTEGER,
                description="返回评论数量，默认 20",
                required=False,
            ),
        ],
    )
    async def handle_get_episode_comments(self, episode_id: int = 0, **kwargs: Any) -> dict[str, str]:
        try:
            if not self._client:
                return {"name": "get_bangumi_episode_comments", "content": "插件未初始化"}
            cfg = self.config.request
            limit_val = kwargs.get("limit")
            limit = int(limit_val) if limit_val is not None else 20
            comments = await fetch_episode_comments(
                self._client,
                episode_id=episode_id,
                limit=limit,
                timeout=cfg.timeout,
            )
            if not comments:
                return {
                    "name": "get_bangumi_episode_comments",
                    "content": "该集暂无吐槽箱评论。",
                }

            lines = [f"吐槽箱评论（{len(comments)}条）："]
            for i, c in enumerate(comments, 1):
                score_str = f" [{c.score}]" if c.score else ""
                lines.append(f"\n#{i} {c.username}{score_str} {c.time}")
                lines.append(f"  {c.content}")
            return {"name": "get_bangumi_episode_comments", "content": "\n".join(lines)}
        except BangumiHTMLError as e:
            return {"name": "get_bangumi_episode_comments", "content": str(e)}
        except Exception as e:
            self.ctx.logger.error("get_bangumi_episode_comments 异常: %s", e, exc_info=True)
            return {"name": "get_bangumi_episode_comments", "content": f"获取吐槽箱失败: {e}"}

    # ----------------------------------------------------------------
    # Tool 8: get_bangumi_subject_relations
    # ----------------------------------------------------------------

    @Tool(
        "get_bangumi_subject_relations",
        description=(
            "获取某部作品的关联作品，如前传、续作、番外、系列作品等。"
            "当用户问'这部有没有续作'、'观看顺序是什么'时使用。"
        ),
        parameters=[
            ToolParameterInfo(
                name="subject_id",
                param_type=ToolParamType.INTEGER,
                description="Bangumi 条目 ID",
                required=True,
            ),
        ],
    )
    async def handle_get_relations(self, subject_id: int = 0, **kwargs: Any) -> dict[str, str]:
        del kwargs
        try:
            if not self._api:
                return {"name": "get_bangumi_subject_relations", "content": "插件未初始化"}
            relations = await self._api.get_subject_relations(subject_id)
            if not relations:
                return {"name": "get_bangumi_subject_relations", "content": "该条目没有关联作品。"}

            by_rel: dict[str, list[str]] = {}
            for r in relations:
                rel_type = r.relation or "相关"
                line = f"[{r.id}] {r.name_cn or r.name}"
                by_rel.setdefault(rel_type, []).append(line)

            lines = ["关联作品："]
            for rel_type, items in by_rel.items():
                lines.append(f"\n{rel_type}:")
                for item in items:
                    lines.append(f"  {item}")
            return {"name": "get_bangumi_subject_relations", "content": "\n".join(lines)}
        except BangumiAPIError as e:
            return {"name": "get_bangumi_subject_relations", "content": str(e)}
        except Exception as e:
            self.ctx.logger.error("get_bangumi_subject_relations 异常: %s", e, exc_info=True)
            return {"name": "get_bangumi_subject_relations", "content": f"获取关联作品失败: {e}"}

    # ----------------------------------------------------------------
    # Tool 9: get_bangumi_subject_reviews
    # ----------------------------------------------------------------

    @Tool(
        "get_bangumi_subject_reviews",
        description=(
            "获取作品的长评列表，或查看单篇长评完整内容。"
            "列表模式：只传 subject_id，返回评论摘要（含 review_id）。"
            "详情模式：传 subject_id + review_id，返回该篇长评完整正文。"
            "当用户想看某部作品的长评、或想深入阅读某篇评论时使用。"
            "注意：该功能通过解析 Bangumi 网页实现，页面结构变更可能导致暂时不可用。"
        ),
        parameters=[
            ToolParameterInfo(
                name="subject_id",
                param_type=ToolParamType.INTEGER,
                description="Bangumi 条目 ID",
                required=True,
            ),
            ToolParameterInfo(
                name="review_id",
                param_type=ToolParamType.INTEGER,
                description="（详情模式）长评 ID。传此参数则返回该长评的完整内容而非列表",
                required=False,
            ),
            ToolParameterInfo(
                name="limit",
                param_type=ToolParamType.INTEGER,
                description="（列表模式）返回评论摘要数量，默认 10",
                required=False,
            ),
        ],
    )
    async def handle_get_reviews(self, subject_id: int = 0, **kwargs: Any) -> dict[str, str]:
        try:
            if not self._client:
                return {"name": "get_bangumi_subject_reviews", "content": "插件未初始化"}
            cfg = self.config.request

            review_id = kwargs.get("review_id")

            if review_id is not None:
                review = await fetch_review_detail(
                    self._client,
                    review_id=int(review_id),
                    timeout=cfg.timeout,
                )
                lines = [
                    f"【{review.title}】",
                    f"作者: {review.author}  {review.time}",
                    "",
                    review.content,
                ]
                return {"name": "get_bangumi_subject_reviews", "content": "\n".join(lines)}

            limit_val = kwargs.get("limit")
            limit = int(limit_val) if limit_val is not None else 10
            reviews = await fetch_reviews_list(
                self._client,
                subject_id=subject_id,
                limit=limit,
                timeout=cfg.timeout,
            )
            if not reviews:
                return {"name": "get_bangumi_subject_reviews", "content": "该条目暂无长评。"}

            lines = [f"长评列表（{len(reviews)}篇）："]
            for i, r in enumerate(reviews, 1):
                lines.append(f"\n#{i} [{r.review_id}] {r.title}")
                lines.append(f"  作者: {r.author}  {r.time}")
                if r.summary:
                    summary = r.summary[:200] + ("..." if len(r.summary) > 200 else "")
                    lines.append(f"  {summary}")
            return {"name": "get_bangumi_subject_reviews", "content": "\n".join(lines)}
        except BangumiHTMLError as e:
            return {"name": "get_bangumi_subject_reviews", "content": str(e)}
        except Exception as e:
            self.ctx.logger.error("get_bangumi_subject_reviews 异常: %s", e, exc_info=True)
            return {"name": "get_bangumi_subject_reviews", "content": f"获取长评失败: {e}"}


def create_plugin() -> BangumiBrowsePlugin:
    return BangumiBrowsePlugin()
