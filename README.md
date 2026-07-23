# Bangumi 浏览插件

为 MaiBot 提供 Bangumi (bgm.tv) 条目浏览能力，支持动画、游戏、书籍、音乐等多种类型的搜索和详情查询。

## 功能

本插件提供 9 个 Tool，LLM 可在聊天中按需调用：

| Tool | 功能 | 数据源 |
|------|------|--------|
| `search_bangumi_subject` | 搜索条目（支持按类型筛选） | REST API |
| `get_bangumi_subject` | 获取条目详情（评分、简介、标签等） | REST API |
| `get_bangumi_subject_persons` | 获取制作人员阵容 | REST API |
| `get_bangumi_season` | 获取季度放送/发售列表 | REST API |
| `get_bangumi_calendar` | 获取本周每日放送时间表 | HTML 解析 |
| `get_bangumi_episodes` | 获取剧集列表 | REST API |
| `get_bangumi_episode_comments` | 获取单集吐槽箱评论 | HTML 解析 |
| `get_bangumi_subject_relations` | 获取关联作品（前传/续作等） | REST API |
| `get_bangumi_subject_reviews` | 获取作品长评列表/详情 | HTML 解析 |

## 安装

将插件目录放入 MaiBot 的 `plugins/` 目录下：

```
plugins/bangumi_browse_plugin/
```

重启 MaiBot 或通过 WebUI 插件管理加载插件。

## 配置

首次加载后，Runner 会自动生成 `config.toml`。可配置项：

```toml
[plugin]
enabled = true
config_version = "1.0.0"

[request]
timeout = 15
user_agent = "FFFold/bangumi-browse-plugin (https://github.com/FFFold/bangumi_browse_plugin)"
proxy = ""
```

- `timeout`: HTTP 请求超时（秒）
- `user_agent`: Bangumi API 要求设置 User-Agent，建议包含项目链接
- `proxy`: 可选 HTTP 代理地址（如 `http://127.0.0.1:7890`）

## 使用

插件仅提供 Tool 接口，由 LLM 自动调用。用户在对话中询问动画/游戏相关问题时，LLM 会主动使用这些工具。

示例对话场景：

- "帮我查一下攻壳机动队的评分" → `search_bangumi_subject` + `get_bangumi_subject`
- "这季度有什么新番？" → `get_bangumi_season`
- "今天有什么动画更新？" → `get_bangumi_calendar`
- "巨人最终季第三集评价怎么样？" → `search_bangumi_subject` + `get_bangumi_episodes` + `get_bangumi_episode_comments`
- "攻壳机动队有续作吗？" → `search_bangumi_subject` + `get_bangumi_subject_relations`
- "看看攻壳机动队的长评" → `get_bangumi_subject_reviews`

## 依赖

- `httpx` >= 0.25.0
- `beautifulsoup4` >= 4.11.0
- `lxml` >= 4.9.0

以上依赖在 `_manifest.json` 中声明，MaiBot 会自动安装。

## 注意事项

- 吐槽箱评论通过解析 Bangumi 网页实现，若 Bangumi 页面结构变更可能导致暂时不可用。
- 吐槽箱评论通过 JavaScript 动态加载，HTML 直接解析可能无法获取评论内容。若返回为空，LLM 会引导用户访问 Bangumi 页面自行查看。
- 插件为只读设计，不涉及用户登录、收藏等写操作。
- 向 Bangumi API 发送请求时请遵守其使用条款，必须设置合理的 User-Agent。

## 许可证

MIT
