# LLM Council Direct

![llmcouncil](header.jpg)

这是一个基于 [karpathy/llm-council](https://github.com/karpathy/llm-council) 的直连厂商 API 版本。项目绕过 OpenRouter，直接调用国内外大模型厂商 API，支持通过 `backend/config.py` 自由配置任意模型，组成一个灵活的 3 阶段 LLM Council 审议系统。

## 核心特性

- 支持 9 个国内外 Provider：OpenAI、Anthropic、Google、xAI、DeepSeek、通义千问、智谱清言、月之暗面 Kimi、阶跃星辰。
- Council 模型列表灵活可配：用户只需要修改 `backend/config.py` 中的 `COUNCIL_MODELS` 和 `CHAIRMAN_MODEL`，无需改业务代码。
- 3 阶段审议流程：独立回答 -> 盲审互评 -> 主席综合。
- 直连厂商 API：请求从本机直接发送到对应 Provider，避免中间代理。
- 支持 OpenAI-compatible 接口，同时保留 Anthropic Messages API 支持。

## 支持的 Provider

| Provider | 厂商 | API Key 环境变量 |
|----------|------|-----------------|
| openai | OpenAI | OPENAI_API_KEY |
| anthropic | Anthropic | ANTHROPIC_API_KEY |
| google | Google | GOOGLE_API_KEY |
| xai | xAI | XAI_API_KEY |
| deepseek | DeepSeek 深度求索 | DEEPSEEK_API_KEY |
| qwen | 阿里通义千问 | QWEN_API_KEY |
| glm | 智谱清言 | GLM_API_KEY |
| moonshot | 月之暗面 Kimi | MOONSHOT_API_KEY |
| stepfun | 阶跃星辰 | STEPFUN_API_KEY |

## 快速开始

```bash
# 安装
uv sync
cd frontend && npm install && cd ..

# 配置 API Key（填入你有 Key 的厂商即可，不需要全部）
cp .env.example .env
nano .env

# 编辑 Council 模型列表（可选，默认已配好国内外混合）
nano backend/config.py

# 启动
./start.sh
```

启动后打开前端地址，通常是 `http://localhost:5173`。

## 自定义 Council

所有模型都使用 `provider/model-name` 格式。只需要修改 `backend/config.py`：

```python
COUNCIL_MODELS = [
    "deepseek/deepseek-chat",
    "openai/gpt-4o",
    "google/gemini-2.5-flash",
    "qwen/qwen-plus",
    "glm/glm-4-flash",
]

CHAIRMAN_MODEL = "deepseek/deepseek-reasoner"
```

你可以自由增删模型。只要 Provider 已在 `PROVIDERS` 注册，并且 `.env` 中配置了对应 API Key，就可以加入 Council。

如需新增 Provider，在 `PROVIDERS` 中添加一项即可：

```python
"provider_name": {
    "base_url": "https://example.com/v1/chat/completions",
    "api_key": os.getenv("PROVIDER_API_KEY"),
    "format": "openai",
}
```

## 3 阶段审议流程

1. 独立回答：用户问题会并行发送给 `COUNCIL_MODELS` 中的所有模型，每个模型独立给出第一轮答案。
2. 盲审互评：每个模型会看到匿名化后的其他模型答案，并基于准确性、完整性和洞察力进行排序与评价。
3. 主席综合：`CHAIRMAN_MODEL` 会读取第一轮答案和互评结果，综合生成最终回答。

## 技术栈

- Backend：FastAPI、async httpx、直接厂商 API
- Frontend：React、Vite、react-markdown
- Storage：`data/conversations/` 下的 JSON 文件

## Credits

- 原始项目：[Karpathy/llm-council](https://github.com/karpathy/llm-council)
- 直连 API 版本：[cyrilleroux/llm-council-direct](https://github.com/cyrilleroux/llm-council-direct)
- 本项目：在直连架构基础上扩展为支持国内外任意大模型的灵活 LLM Council
