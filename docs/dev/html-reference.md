# HTML 参考

所有 HTML 解析通过 `bangumi_html.py`，基地址 `https://bgm.tv`。

## 错误处理

```python
class BangumiHTMLError(Exception)
async def _fetch(client, url, timeout) -> str  # GET + 统一错误处理
```

## 页面结构

### 每日放送 — `/calendar`

CSS 路径：`.BgmCalendar > ul.large > li.week > dl`

```
li.week
  dt.{Sun|Mon|Tue|Wed|Thu|Fri|Sat}
    div > h3                    # 星期标题 + 日期
  dd.{Sun|...}
    ul.coverList > li           # 每部动画
      div.info_bg > div.info
        p > a.nav               # 中文名 + subject_id (/subject/{id})
        p > small > em          # 日文原名
```

解析函数：`fetch_calendar(client, timeout) -> list[CalendarDay]`

星期转换：`_WEEKDAY_EN2CN` 字典（CSS class → 中文）。

### 单集吐槽箱 — `/ep/{id}`

CSS 路径：`#comment_list > .row_reply`

```
div.row_reply[data-item-user]
  div.post_actions > div.action > small
    a.floor-anchor             # #1
     - 2026-6-25 00:07         # 时间
  a.avatar                     # 头像
  div.inner
    strong > a.l               # 用户名
    div.reply_content > div.message  # 评论正文
```

解析函数：`fetch_episode_comments(client, episode_id, limit, timeout) -> list[EpisodeComment]`

时间提取：用正则 `^#\d+\s*[-–—]\s*` 去掉楼层号前缀。

### 长评列表 — `/subject/{id}/reviews`

CSS 路径：`#entry_list > .item.clearit`

```
div.item.clearit[data-item-user]
  h2.title > a.l[href="/blog/{id}"]    # 标题 + blog_id
  a.avatar[title]                       # 作者名
  div.content > a                       # 摘要
  small.greytext                        # 时间
```

解析函数：`fetch_reviews_list(client, subject_id, limit, timeout) -> list[ReviewSummary]`

### 长评详情 — `/blog/{id}`

```
h1                          # 标题
.author, a.avatar           # 作者
.time, .date, small.greytext  # 时间
.content, .entry, article   # 正文
```

解析函数：`fetch_review_detail(client, review_id, timeout) -> ReviewDetail`

## 添加新解析器

1. 在 `bangumi_html.py` 中添加 async 函数
2. 使用 `_fetch(client, url, timeout)` 获取页面 HTML
3. 用 `BeautifulSoup(html, "lxml")` 解析
4. 返回 `models.py` 中的 Pydantic 模型
5. 在 `plugin.py` 的 handler 中调用

## 脆弱点

HTML 解析依赖 Bangumi 页面 DOM 结构。结构变更时：
- 首先用 `tests/probe_html.py` 探针脚本检查新结构
- 更新对应 CSS 选择器
- 运行 `test_html.py` 验证
