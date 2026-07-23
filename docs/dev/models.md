# 数据模型

所有模型定义在 `models.py`，使用 Pydantic `BaseModel`。

## API 响应模型

### Subject — 搜索/列表中的条目摘要

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `int` | 条目 ID |
| `name` | `str` | 日文名 |
| `name_cn` | `str` | 中文名 |
| `type` | `str` | 类型：anime/book/game/music/real（已从 int 转换） |
| `summary` | `str` | 简介 |
| `date` | `str` | 首播/发售日期 |
| `eps` | `int` | 集数 |
| `rating` | `RatingInfo \| None` | 评分信息 |
| `rank` | `int` | 排名 |
| `images` | `ImageInfo \| None` | 封面图（large/common/medium/small/grid） |

### SubjectDetail — 条目完整信息

继承 `Subject`，额外字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `platform` | `str` | 平台（游戏类） |
| `infobox` | `list[dict]` | 信息框键值对 |
| `tags` | `list[dict]` | 标签（`name`/`count`） |
| `collection` | `dict[str, int]` | 收藏统计 |
| `score` | `property float` | 评分（快捷属性，从 rating.score 取） |
| `score_count` | `property int` | 评分人数 |

### SubjectPerson — 制作人员

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `int` | 人员 ID |
| `name` | `str` | 姓名 |
| `relation` | `str` | 职位关系（如"监督"、"脚本"） |
| `type` | `str` | 人员类型（已从 int 转换） |
| `positions` | `list[str]` | 具体职位 |
| `career` | `list[str]` | 职业标签 |

### Episode — 剧集项

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `int` | 剧集 ID |
| `type` | `int` | EpType：0=本篇 1=SP 2=OP 3=ED 4=PV 5=MAD 6=Other |
| `name` / `name_cn` | `str` | 标题 |
| `sort` | `float` | 排序号 |
| `ep` | `int \| None` | 集数（本篇有效） |
| `airdate` | `str` | 放送日期 |
| `comment` | `int` | 评论数（非内容！） |
| `subject_id` | `int` | 所属条目 ID |

### SubjectRelation — 关联作品

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `int` | 关联条目 ID |
| `name` / `name_cn` | `str` | 名称 |
| `relation` | `str` | 关系类型（前传/续作/番外等） |

## HTML 解析模型

### CalendarDay / CalendarItem — 每日放送

```python
class CalendarItem:
    subject_id: int
    name: str           # 日文名
    name_cn: str        # 中文名
    time: str           # 放送时间（当前未提取）
    cover: str          # 封面 URL

class CalendarDay:
    weekday: str        # "周一" ~ "周日"
    date: str           # 日期文本
    items: list[CalendarItem]
```

### EpisodeComment — 吐槽箱评论

| 字段 | 类型 | 说明 |
|------|------|------|
| `username` | `str` | 用户名 |
| `score` | `str` | 评分（当前未提取，吐槽箱不带分数） |
| `content` | `str` | 评论内容 |
| `time` | `str` | 发布时间 |

### ReviewSummary / ReviewDetail — 长评

```python
class ReviewSummary:
    review_id: int      # blog ID
    title: str
    author: str
    time: str
    score: int          # 长评页面不含评分，始终为 0
    summary: str

class ReviewDetail:
    review_id: int
    title: str
    author: str
    time: str
    score: int          # 同上
    content: str        # 完整正文
```

## 类型转换

`Subject` 和 `SubjectPerson` 的 `type` 字段使用 `field_validator("type", mode="before")` 自动将 API 返回的 int 转为字符串。映射关系见 `_SUBJECT_TYPE_MAP`。
