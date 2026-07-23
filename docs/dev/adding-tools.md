# 添加新 Tool

逐步指南，附带代码模板。

## 1. 判断数据源

| 来源 | 在哪写 | 用什么 |
|------|--------|--------|
| Bangumi REST API | `bangumi_api.py` 添加方法 | `_get()` / `_post()` |
| Bangumi HTML 页面 | `bangumi_html.py` 添加解析函数 | `_fetch()` + BeautifulSoup |
| 纯计算/组合 | 直接在 handler 中处理 | — |

## 2. API 类 Tool

```python
# bangumi_api.py
class BangumiAPI:
    async def your_new_method(self, ...) -> ...:
        data = await self._get("/your/endpoint", **params)
        # 或 self._post(...)
        return [YourModel(**item) for item in data]
```

## 3. HTML 类 Tool

```python
# bangumi_html.py
async def fetch_your_page(client, ..., timeout=15) -> ...:
    html = await _fetch(client, f"{BGM_BASE}/your/url", timeout)
    soup = BeautifulSoup(html, "lxml")
    # 提取数据...
    return results
```

## 4. 注册 Tool

在 `plugin.py` 的 `BangumiBrowsePlugin` 类中：

```python
@Tool(
    "your_tool_name",
    description="工具用途、使用场景、参数说明、限制和副作用",
    parameters=[
        ToolParameterInfo(
            name="param_name",
            param_type=ToolParamType.STRING,   # STRING / INTEGER / FLOAT / BOOLEAN
            description="参数说明",
            required=True,
        ),
    ],
)
async def handle_your_tool(self, ...) -> dict[str, str]:
    try:
        # 参数解析
        # 调用 API 或 HTML 模块
        # 格式化输出
        return {"name": "your_tool_name", "content": "..."}
    except BangumiAPIError as e:
        return {"name": "your_tool_name", "content": str(e)}
    except BangumiHTMLError as e:
        return {"name": "your_tool_name", "content": str(e)}
    except Exception as e:
        self.ctx.logger.error("your_tool_name 异常: %s", e, exc_info=True)
        return {"name": "your_tool_name", "content": f"操作失败: {e}"}
```

## 5. 需要模型时

在 `models.py` 中添加 Pydantic 模型：

```python
class YourNewModel(BaseModel):
    id: int
    name: str = ""
    # ...其他字段
```

## 6. 测试

- API 类 Tool：在 `tests/test_api.py` 中添加测试用例
- HTML 类 Tool：先用 `tests/probe_html.py` 探针检查页面结构，再在 `tests/test_html.py` 中添加测试

## 注意事项

- **错误处理**：必须捕获 `BangumiAPIError` / `BangumiHTMLError` 和通用 `Exception`
- **类型转换**：API 请求的 `type` 参数用 `_TYPE_MAP` 转 int，响应用 `field_validator` 转回 string
- **参数别名**：分类类参数（如 `ep_type`）应同时支持数字和文本，使用 `_resolve_*` 函数
- **capabilities**：只声明实际使用的。Tool 返回 dict + `self.config` 不走 capability 通道
- **描述文字**：简体中文，写清使用场景和限制
- **资源管理**：httpx client 由 `on_load` 创建、`on_unload` 关闭，不自行管理
