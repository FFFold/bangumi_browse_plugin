<div align="center">

# 🎬 Bangumi 浏览插件

[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![Manifest](https://img.shields.io/badge/manifest-v2-7c3aed?style=flat-square)](_manifest.json)
[![MaiBot](https://img.shields.io/badge/MaiBot-plugin-f97316?style=flat-square)](https://github.com/AnotiaWang/MaiBot)
[![Python](https://img.shields.io/badge/python-3.11%2B-22c55e?style=flat-square)]()

接入 [Bangumi](https://bgm.tv) 🎯 让你的 MaiBot 变身动画高手——新番速览、每日放送、单集吐槽、长评阅读、制作阵容，动画·游戏·书籍一网打尽。

</div>

---

## ✨ 功能一览

| Tool | 能力 | 数据源 |
|------|------|--------|
| `search_bangumi_subject` | 关键词搜索，支持类型筛选 | API |
| `get_bangumi_subject` | 完整详情：评分·放送时间·集数·简介·标签 | API |
| `get_bangumi_subject_persons` | 制作阵容：监督·脚本·音乐·CV | API |
| `get_bangumi_season` | 当季新番速览，可按分类过滤 | API |
| `get_bangumi_calendar` | 🗓 本周每日放送时间表 | 网页 |
| `get_bangumi_episodes` | 剧集列表，支持本篇/SP/OP/ED 筛选 | API |
| `get_bangumi_episode_comments` | 💬 单集吐槽箱——看看大家怎么说 | 网页 |
| `get_bangumi_subject_relations` | 前传·续作·番外等关联作品 | API |
| `get_bangumi_subject_reviews` | 📝 长评列表 + 全文阅读 | 网页 |

---

## 📦 安装

```bash
cd MaiBot/plugins
git clone https://github.com/FFFold/bangumi_browse_plugin
```

重启 MaiBot 或通过 WebUI 加载即可 🚀

---

## ⚙️ 配置

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

---

## 💡 对话示例

| 你说 | Bot 会做 |
|------|----------|
| _"帮我查一下攻壳机动队的评分"_ | `search_bangumi_subject` → `get_bangumi_subject` |
| _"这季度有什么新番？"_ | `get_bangumi_season`（7+8+9 月） |
| _"今天有什么动画更新？"_ | `get_bangumi_calendar` |
| _"巨人最终季第三集评价怎么样？"_ | `search_bangumi_subject` → `get_bangumi_episodes` → `get_bangumi_episode_comments` |
| _"攻壳机动队有续作吗？"_ | `search_bangumi_subject` → `get_bangumi_subject_relations` |
| _"看看攻壳的长评"_ | `get_bangumi_subject_reviews` |

---

## 📋 依赖

| 包 | 版本 |
|----|------|
| `httpx` | >= 0.25.0 |
| `beautifulsoup4` | >= 4.11.0 |
| `lxml` | >= 4.9.0 |

已声明在 `_manifest.json`，MaiBot 会自动安装 ✅

---

## ⚠️ 注意事项

- 🕸 每日放送、吐槽箱、长评通过解析网页实现，页面结构变更可能导致暂时不可用
- 🔒 纯只读设计，无需登录，不涉及收藏等写操作
- 📖 请遵守 [Bangumi API 使用条款](https://github.com/bangumi/api/blob/master/docs-raw/user%20agent.md)

---

<div align="center">

**MIT © [FFFold](https://github.com/FFFold)**

</div>
