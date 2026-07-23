# API 参考

所有 REST API 调用通过 `bangumi_api.py` 的 `BangumiAPI` 类，基地址 `https://api.bgm.tv/v0`。

## 类型映射

Bangumi API 使用整数表示条目类型，请求和响应需互转：

| 字符串 | 整数 | 含义 |
|--------|------|------|
| `book` | 1 | 书籍 |
| `anime` | 2 | 动画 |
| `music` | 3 | 音乐 |
| `game` | 4 | 游戏 |
| `real` | 6 | 真人 |

- **请求侧**：`bangumi_api.py` 的 `_TYPE_MAP` 将字符串 → 整数（`"anime"` → 2）
- **响应侧**：`models.py` 的 `field_validator("type", mode="before")` 将整数 → 字符串（2 → `"anime"`）

## HTTP 客户端

```python
class BangumiAPI:
    def __init__(self, client: httpx.AsyncClient, timeout: int = 15)
    async def _get(path, **params)   # GET + 错误处理
    async def _post(path, body, **params)  # POST + 错误处理
```

错误处理：
- 超时 → `"请求 Bangumi API 超时，请稍后重试"`
- 404 → `"未找到该条目，请检查 ID 是否正确"`
- 其他 4xx/5xx → 含状态码和响应体的可读错误

## 端点

### `search_subjects` → `POST /v0/search/subjects`

```python
async def search_subjects(
    keyword: str,
    subject_type: str | None = None,   # "anime" → 2
    sort: str = "match",               # match / heat / rank / score
    limit: int = 10,
    offset: int = 0,
) -> list[Subject]
```

**注意：** `filter.type` 必须传整数数组 `[2]`，不能传 `["anime"]`。

### `get_subject` → `GET /v0/subjects/{id}`

```python
async def get_subject(subject_id: int) -> SubjectDetail
```

返回完整信息：评分（score + total）、排名、简介、标签、infobox 等。

### `get_subject_persons` → `GET /v0/subjects/{id}/persons`

```python
async def get_subject_persons(subject_id: int) -> list[SubjectPerson]
```

每人包含 `relation`（职位关系如"监督"）、`positions`（具体职位）、`career`（职业标签）。

### `browse_subjects` → `GET /v0/subjects`

```python
async def browse_subjects(
    subject_type: str = "anime",       # 字符串，内部转 int
    year: int | None = None,
    month: int | None = None,
    sort: str = "date",
    limit: int = 20,
    offset: int = 0,
    cat: int | None = 1,              # SubjectAnimeCategory: 0/1/2/3/5
) -> list[Subject]
```

**重要：** `year`/`month` 按条目**首播日期**（`date` 字段）筛选，不是"当月在播"。日本动画季（1/4/7/10 月）应连查 3 个月。

`cat` 分类值（仅 anime 有效）：
| 值 | 含义 |
|----|------|
| 0 | Other（含 CM/PV） |
| 1 | TV（默认） |
| 2 | OVA |
| 3 | Movie |
| 5 | WEB |
| None | 不过滤 |

### `get_episodes` → `GET /v0/episodes`

```python
async def get_episodes(
    subject_id: int,
    limit: int = 100,
    offset: int = 0,
    ep_type: int | None = None,       # EpType: 0-6
) -> list[Episode]
```

`ep_type` 章节类型：
| 值 | 含义 |
|----|------|
| 0 | 本篇 |
| 1 | SP |
| 2 | OP |
| 3 | ED |
| 4 | PV |
| 5 | MAD |
| 6 | Other |
| None | 不过滤（默认） |

### `get_subject_relations` → `GET /v0/subjects/{id}/subjects`

```python
async def get_subject_relations(subject_id: int) -> list[SubjectRelation]
```

返回关联关系列表，每条含 `relation`（如"前传"、"续作"、"番外篇"）和关联条目信息。
