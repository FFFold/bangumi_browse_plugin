# Changelog

## v1.0.0 (2026-07-23)

### 新增

- **9 个 Tool** 供 LLM 自动调用，覆盖 Bangumi 核心浏览场景
  - `search_bangumi_subject` — 条目搜索，支持按类型筛选
  - `get_bangumi_subject` — 条目详情：评分、放送日期、集数、简介、标签
  - `get_bangumi_subject_persons` — 制作阵容：监督、脚本、CV 等
  - `get_bangumi_season` — 季度新番速览，支持 TV/OVA/Movie/WEB 分类过滤
  - `get_bangumi_calendar` — 本周每日放送时间表
  - `get_bangumi_episodes` — 剧集列表，支持本篇/SP/OP/ED 等类型筛选
  - `get_bangumi_episode_comments` — 单集吐槽箱评论
  - `get_bangumi_subject_relations` — 前传、续作、番外等关联作品
  - `get_bangumi_subject_reviews` — 长评列表 + 单篇全文阅读
- 双通道数据获取：Bangumi REST API + HTML 页面解析
- 分类/类型参数同时支持数字和文本别名（如 `"TV"` ↔ `1`）
- 代理支持，适配国内网络环境

### 技术

- httpx 异步客户端，统一超时和错误处理
- Pydantic 模型层，API 响应 int→string 自动类型转换
- BeautifulSoup + lxml HTML 解析，CSS 选择器集中管理
- 配置热重载（超时、User-Agent、代理）
- 集成测试套件（API + HTML 双通道）

### 参考

- 完整开发文档：[docs/dev/index.md](docs/dev/index.md)
- AGENTS.md 用于后续 AI 辅助开发
