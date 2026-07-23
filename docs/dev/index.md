# 开发文档

## 架构概览

```
plugin.py          ── 入口：配置模型 + 9 个 @Tool handler
  ├── bangumi_api.py   ── REST API 客户端（httpx → api.bgm.tv/v0）
  ├── bangumi_html.py  ── HTML 解析器（BeautifulSoup → bgm.tv）
  └── models.py        ── Pydantic 数据模型（请求/响应边界）
```

**数据流：** LLM 触发 Tool → handler 调用 API 或 HTML 模块 → 返回 dict（content 字段为 LLM 可读文本）。

**关键约定：**
- 所有异常在 handler 层捕获并转为可读错误，不泄漏堆栈
- Tool 返回 `{"name": "...", "content": "..."}`，由框架代发消息
- 配置走 `PluginConfigBase` 的 `self.config`，无需 capability 声明

## 快速开始

```bash
cd plugins/bangumi_browse_plugin

# 创建环境
uv venv
uv pip install httpx beautifulsoup4 lxml pydantic

# 运行测试（需要代理）
$env:PYTHONPATH = "D:\Projects\MaiBot\plugins"
.venv\Scripts\python.exe tests\test_api.py
.venv\Scripts\python.exe tests\test_html.py

# 语法验证
python -c "import ast; ast.parse(open('plugin.py', encoding='utf-8').read()); print('OK')"
python -c "import json; json.load(open('_manifest.json', encoding='utf-8')); print('OK')"
```

## 文档索引

| 文档 | 内容 |
|------|------|
| [API 参考](api-reference.md) | REST API 端点、参数、类型映射 |
| [HTML 参考](html-reference.md) | 页面结构、CSS 选择器、解析逻辑 |
| [数据模型](models.md) | Pydantic 模型定义和字段说明 |
| [添加新 Tool](adding-tools.md) | 分步指南 + 代码模板 |

## 外部参考

| 资源 | 链接 |
|------|------|
| Bangumi OpenAPI v0 完整规范 | https://github.com/bangumi/server/blob/master/openapi/v0.yaml |
| Bangumi API 使用约定（UA 要求等） | https://github.com/bangumi/api/blob/master/docs-raw/user%20agent.md |
| MaiBot 插件开发指南 | https://docs.mai-mai.org/plugin/vibe-coding |
| MaiBot Manifest 字段规范 | https://docs.mai-mai.org/plugin/manifest |
| MaiBot Tool 组件文档 | https://docs.mai-mai.org/plugin/tools |
| MaiBot 配置管理文档 | https://docs.mai-mai.org/plugin/config |
