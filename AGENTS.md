# Bangumi 浏览插件

## 仓库结构

- `plugin.py` — 入口，`create_plugin()` 工厂，配置模型 + 9 个 `@Tool`
- `bangumi_api.py` — Bangumi REST API 客户端（httpx）
- `bangumi_html.py` — HTML 页面解析（BeautifulSoup + lxml）
- `models.py` — Pydantic 数据模型
- `_manifest.json` — 插件元信息，`capabilities` 为空数组
- `tests/` — 集成测试，需代理 `127.0.0.1:7897`

## 数据源

| 来源 | 端点 | 用途 |
|------|------|------|
| REST API | `api.bgm.tv/v0/` | 搜索、详情、人员、剧集、季度浏览、关联作品 |
| HTML 解析 | `bgm.tv/` | 每日放送日历、单集吐槽箱、长评列表/详情 |

## 关键约定

### 类型映射

Bangumi API 的 `type` 字段返回整数（2=anime），`SubjectType` 查询参数也需整数。
- API 请求：使用 `_TYPE_MAP` 将字符串转为 int（`"anime"` → 2）
- API 响应：`models.py` 中 `field_validator("type", mode="before")` 将 int 转回字符串
- `search_subjects` 的 `filter.type` 必须传整数数组 `[2]`，不能传 `["anime"]`

### 分类参数

`get_bangumi_season` 的 `category` 和 `get_bangumi_episodes` 的 `ep_type` 同时接受数字和文本：
- category: `"1"` / `"TV"` / `"tv"` / `"all"` → 内部 map + `_safe_int` 兜底
- ep_type: `"0"` / `"main"` / `"本篇"` / `"all"` → 同上
- `"all"` → `None`，API 不传过滤参数；`None` 缺省 → category 默认 1(TV)，ep_type 默认不过滤

### 季度放送按开播月筛选

`get_bangumi_season` 的 `year`/`month` 是按条目首播日期（`date` 字段）过滤，不是"当月在播"。日本动画季（1/4/7/10 月）应连查 3 个月。

### 能力声明

Tool 返回 dict 由框架代发消息，配置用 `PluginConfigBase` 的 `self.config`，均不需要 capability 声明。`_manifest.json` 的 `capabilities` 为空数组。

## 测试

需要代理 `127.0.0.1:7897`（已设环境变量）：

```bash
cd plugins
$env:PYTHONPATH = "D:\Projects\MaiBot\plugins"
bangumi_browse_plugin\.venv\Scripts\python.exe bangumi_browse_plugin\tests\test_api.py
bangumi_browse_plugin\.venv\Scripts\python.exe bangumi_browse_plugin\tests\test_html.py
```

uv 环境已创建在 `.venv/`，包含 httpx、beautifulsoup4、lxml、pydantic。

## 验证

```bash
python -c "import ast; ast.parse(open('plugin.py', encoding='utf-8').read()); print('syntax OK')"
python -c "import json; json.load(open('_manifest.json', encoding='utf-8')); print('manifest OK')"
```

## 依赖

`_manifest.json` 声明：httpx>=0.25.0、beautifulsoup4>=4.11.0、lxml>=4.9.0。pydantic 由 MaiBot 主程序提供，无需声明。

## Git

独立仓库，主分支 `main`，不修改 MaiBot 主程序代码。
