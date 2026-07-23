# Bangumi 浏览插件

[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Manifest](https://img.shields.io/badge/manifest-v2-green)](_manifest.json)

接入 [Bangumi](https://bgm.tv)，让你的 MaiBot 变身动画高手。新番速览、每日放送、单集吐槽、长评阅读、制作阵容——动画、游戏、书籍一网打尽。

## 功能一览

| Tool | 能做什么 | 来源 |
|------|---------|------|
| `search_bangumi_subject` | 按关键词搜索条目，支持按类型筛选 | API |
| `get_bangumi_subject` | 查看完整详情：评分、放送时间、集数、简介、标签 | API |
| `get_bangumi_subject_persons` | 制作阵容：监督、脚本、音乐、CV 等 | API |
| `get_bangumi_season` | 某季新番速览，默认 TV，可按分类过滤 | API |
| `get_bangumi_calendar` | 本周每日放送时间表 | 网页 |
| `get_bangumi_episodes` | 剧集列表，可按本篇/SP/OP 等类型筛选 | API |
| `get_bangumi_episode_comments` | 单集吐槽箱——看大家怎么评价这一集 | 网页 |
| `get_bangumi_subject_relations` | 前传、续作、番外等关联作品 | API |
| `get_bangumi_subject_reviews` | 作品长评列表 + 单篇全文阅读 | 网页 |

## 安装

```bash
cd MaiBot/plugins
git clone https://github.com/FFFold/bangumi_browse_plugin
```

重启 MaiBot 或通过 WebUI 加载即可。

## 配置

首次加载后自动生成 `config.toml`：

```toml
[plugin]
enabled = true

[request]
timeout = 15
user_agent = "FFFold/bangumi-browse-plugin (https://github.com/FFFold/bangumi_browse_plugin)"
proxy = ""
```

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `timeout` | HTTP 请求超时（秒） | `15` |
| `user_agent` | Bangumi API 要求的 UA，须含项目链接 | 见上 |
| `proxy` | HTTP 代理，如 `http://127.0.0.1:7890` | 空 |

## 对话示例

| 用户说 | Bot 会调用 |
|--------|-----------|
| "帮我查一下攻壳机动队的评分" | `search_bangumi_subject` → `get_bangumi_subject` |
| "这季度有什么新番？" | `get_bangumi_season`（7+8+9 月） |
| "今天有什么动画更新？" | `get_bangumi_calendar` |
| "巨人最终季第三集评价怎么样？" | `search_bangumi_subject` → `get_bangumi_episodes` → `get_bangumi_episode_comments` |
| "攻壳机动队有续作吗？" | `search_bangumi_subject` → `get_bangumi_subject_relations` |
| "看看攻壳的长评" | `get_bangumi_subject_reviews` |

## 依赖

- `httpx` >= 0.25.0
- `beautifulsoup4` >= 4.11.0
- `lxml` >= 4.9.0

已声明在 `_manifest.json`，MaiBot 自动安装。

## 注意事项

- 每日放送、吐槽箱、长评通过解析网页实现，页面结构变更可能暂时不可用
- 纯只读设计，无需登录，不涉及收藏等写操作
- 请遵守 [Bangumi API 使用条款](https://github.com/bangumi/api/blob/master/docs-raw/user%20agent.md)

## 许可证

MIT © FFFold
