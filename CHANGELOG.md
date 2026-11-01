# Changelog

## v1.1.0 (2026-10-31)

### 新增

- **`[tools] force_visible` 配置项**（默认 `false`）：开启后将本插件全部 9 个 Tool 以
  `visibility="visible"` 注册，直接进入每轮工具表，模型可即时看到并调用；
  关闭时保持宿主默认的 deferred 设计哲学（工具按需 `tool_search` 检索后调用），
  与 v1.0.1 行为零差异
- 实现方式：覆写 `get_components()` 在组件声明层注入可见性，不改任何 `@Tool` 装饰器
- 开启的代价：约每次 planner 请求多 ~750 token（9 个工具的完整定义常驻上下文）
- 配置版本 bump 至 `1.1.0`，旧配置文件会自动补入 `[tools]` 新字段

### 已知限制

- 宿主仅在插件注册阶段读取一次组件声明，**修改 `force_visible` 后需重载插件才能生效**
  （配置热更新不会触发组件重新注册）

---

## v1.0.1 (2026-07-23)

### 改进

- **`get_bangumi_subject_persons` 全面增强**
  - 显示每人负责的集数（`eps` 字段），分镜/演出/脚本等分集信息不再丢失
  - 组织/公司实体加 `【】` 标识，区分个人与组织
  - 同一人担任多职时自动关联标注 `[兼任: ...]`，消除重复信息
  - 按职能重要性排序（导演→脚本→作画→美术→...），核心职位前置
  - 新增 `relation` 可选筛选参数，可按职能类型过滤
  - 每组超 20 人时显示截断提示

### 修复

- `SubjectPerson.type` 字段映射错误：原来复用条目类型映射（1→book），改为正确的人员类型映射（1→个人, 2→组织, 3→组合）
- 截断逻辑遗漏 `[:20]` 导致提示与实际不符

### 技术

- `_PERSON_RELATION_PRIORITY` 覆盖全部 75 种 Bangumi 真实职位名
- 未知职位 fallback 优先级 70，排在制作管理层附近而非沉底

---

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
