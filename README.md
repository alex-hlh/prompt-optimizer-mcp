# Prompt Optimizer

基于 [prompt-optimizer](https://github.com/linshenkx/prompt-optimizer) 核心模板思路的提示词优化工具集，提供 **MCP 服务** 和 **零配置 Inline Skill** 两种使用方式。

📦 npm：`npx prompt-optimizer-mcp`

---

## 功能

| 工具 | 说明 | 适用场景 |
|------|------|----------|
| `optimize_user_prompt_basic` | 基础优化：消除模糊表述，补充缺失信息 | 日常对话、简单提问 |
| `optimize_user_prompt_professional` | 5维度深度分析 + 结构化优化，附带分析报告 | 需要明确改进方向 |
| `optimize_user_prompt_planning` | 多步骤任务拆解为结构化步骤序列 | 复杂工作流、数据分析 |
| `iterate_prompt` | 基于反馈迭代改进已有优化版本 | 精调已优化的 prompt |
| `evaluate_prompt` | 5维度质量评分（0-100）+ 改进建议 | 验证优化效果 |
| `optimize_image_prompt` | 中文想法 → 英文高质量文生图提示词 | Midjourney / Stable Diffusion |

---

## 快速开始

### 安装

方式一：npm 全局安装（推荐）

```bash
npm install -g prompt-optimizer-mcp
```

方式二：直接 npx 运行（无需安装）

```bash
npx prompt-optimizer-mcp
```

### 运行

```bash
npx prompt-optimizer-mcp
```

---

## 集成指南

所有 MCP 客户端配置模式一致，只需替换 `command` 和 `args`：

```json
{
  "mcpServers": {
    "prompt-optimizer": {
      "command": "npx",
      "args": ["prompt-optimizer-mcp"],
      "env": {
        "OPTIMIZER_API_BASE": "https://api.deepseek.com/v1",
        "OPTIMIZER_API_KEY": "sk-your-key",
        "OPTIMIZER_MODEL": "deepseek-chat"
      }
    }
  }
}
```

| 客户端 | 配置文件位置 |
|--------|-------------|
| Claude Desktop | `%APPDATA%\Claude\claude_desktop_config.json` |
| Claude Code (CLI) | `~/.claude/settings.json` 或项目 `./claude.json` |
| Cursor | `~/.cursor/mcp.json` |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` |
| Opencode | 项目根目录 `opencode.json` 或 `~/.config/opencode/config.json` |
| Continue (VS Code) | `~/.continue/config.json` |
| GitHub Copilot | `~/.github/copilot.json` |

配置完成后在对话中对 agent 说 **"优化这个 prompt"** 即可触发。

---

## Inline Skill（零配置）

无需配置任何外部模型，由当前对话 AI 直接执行 prompt 优化。适用场景：不想配 API Key 时快速使用。

```
prompt-optimizer-mcp/
└── skill/
    ├── SKILL.md               # 零配置 skill 指令
    └── templates/             # 优化策略模板（同 MCP 版复用一套策略）
```

配置方式：在 agent 中加载 `skill/SKILL.md` 即可，触发后 AI 读取 `skill/templates/` 中的策略自行优化。

**与 MCP 版对比：**

| | MCP 版 | Inline Skill |
|---|---|---|
| 调用方式 | 外部 LLM (DeepSeek/Ollama) | 当前对话 AI 直接执行 |
| 配置 | 需要 API_KEY + MODEL | **零配置** |
| 依赖 | mcp + openai Python 包 | 无 |
| 集成对象 | MCP 客户端 | 支持 skill 加载的 agent |

---

## 架构设计

```
用户原始 prompt
    ↓
┌─ 两种执行路径 ─────────────────┐
│                                │
├─ MCP 版 ───────────────────────┤
│ mcp_server.py (调度层)         │
│   ├── 选择模板 (templates/)    │
│   ├── 替换占位符 {user_prompt} │
│   └── 调用外部 LLM 优化        │
│                                │
├─ Inline Skill ─────────────────┤
│ skill/SKILL.md (指令层)        │
│   ├── 读取 skill/templates/    │
│   └── 当前 AI 直接优化         │
└────────────────────────────────┘
    ↓
优化后的 prompt
```

### 设计原则

- **模板与代码分离**：优化策略在 `templates/*.txt` 中，修改策略无需改代码
- **一次调用**：每个工具只调 1 次 LLM，分析和改写合并到同一个模板中
- **Evidence Framing**：用户输入包装为 JSON 字段，防止 LLM 误执行而非优化
- **变量保留**：所有模板强制保留 `{{variable}}` 占位符

---

## 模板详解

6 个模板覆盖提示词优化的主要场景，均基于 [Prompt Engineering Guide](https://www.promptingguide.ai)、Meta Prompting (Zhang et al. 2024) 等行业最佳实践编写。

### 模板文件

| 文件 | 行数 | 核心策略 | 输出格式 |
|------|------|----------|----------|
| `user_optimize_basic.txt` | ~25 | 替换模糊词 + 补充缺失要素 | 纯文本 prompt |
| `user_optimize_professional.txt` | ~45 | 5维度评分 + 结构化输出 | 分析报告 + 优化版 |
| `user_optimize_planning.txt` | ~35 | 任务分解 → 步骤结构化 | 分步执行序列 |
| `iterate_prompt.txt` | ~35 | 约束融入 + few-shot 示例 | 完整修改版 |
| `evaluate_prompt.txt` | ~40 | 5维度 0-100 评分 + JSON 输出 | JSON |
| `image_optimize.txt` | ~55 | 5框架（主体/环境/光线/构图/风格） | 英文 prompt |

### 改进来源

| 来源 | 应用 |
|------|------|
| Prompt Engineering Guide (DAIR.AI) | 角色定义、分隔符使用、任务分解 |
| Meta Prompting (Zhang et al. 2024) | 结构化输出约束、抽象示例 |
| OpenAI 最佳实践 | "说做什么不说不要做什么" |
| Few-shot Prompting | iterate 模板的正反示例 |
| 评估量化框架 | evaluate 模板的 5 维度 0-100 评分体系 |

---

## 适配模型

通过环境变量连接任意 OpenAI 兼容接口：

| 提供商 | API_BASE | MODEL 示例 | 成本 |
|--------|----------|-----------|------|
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` | 低 |
| Ollama (本地) | `http://localhost:11434/v1` | `qwen2.5:7b` | 免费 |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` | 低 |
| SiliconFlow | `https://api.siliconflow.cn/v1` | `Qwen/Qwen2.5-14B-Instruct` | 低 |
| Groq | `https://api.groq.com/openai/v1` | `llama-3.3-70b` | 免费 |
| vLLM | `http://localhost:8000/v1` | 自定义 | 自有硬件 |

> **建议**：优化任务使用小模型（如 DeepSeek Chat / qwen2.5:7b）即可，将大模型算力留给主任务。

---

## 扩展：添加新模板

1. 在 `templates/` 下创建 `.txt` 文件，使用 `{placeholder}` 作为变量占位符
2. 在 `mcp_server.py` 中添加对应的 `@mcp.tool()` 函数

示例——添加一个"翻译 prompt 优化"模板：

```python
@mcp.tool()
def optimize_translation_prompt(prompt: str) -> str:
    """优化翻译类提示词"""
    return _llm(_fill(_load("translate_optimize.txt"), user_prompt=prompt),
                json.dumps({"originalPrompt": prompt}, ensure_ascii=False))
```

---

## 与直接调用 LLM 的成本对比

| 方式 | 调用次数 | token 消耗 | 适用场景 |
|------|---------|-----------|----------|
| 直接写 prompt 调 LLM | 1 次大模型 | 少 | 一次性简单任务 |
| 大模型自己帮写 + 执行 | 可能 2 次大模型 | 多 | 不推荐 |
| 本 MCP (用小模型优化) | 1 次小模型 + 1 次大模型 | 小模型少 | 高频复用的 prompt |
| 本 MCP (用本地模型优化) | 本地免费 + 1 次大模型 | 接近零额外成本 | 推荐 |

**省成本的关键**：优化用小模型/本地模型，主任务用大模型，各司其职。

---

## 目录结构

```
prompt-optimizer-mcp/
├── package.json           # npm 包元信息
├── index.js               # Node.js 包装器 → spawn python
├── install.js             # postinstall: 自动 pip install
├── mcp_server.py          # MCP 服务入口 (73行)
├── templates/             # 提示词优化模板（MCP 版用）
│   ├── user_optimize_basic.txt
│   ├── user_optimize_professional.txt
│   ├── user_optimize_planning.txt
│   ├── iterate_prompt.txt
│   ├── evaluate_prompt.txt
│   └── image_optimize.txt
├── skill/                 # 零配置 Inline Skill
│   ├── SKILL.md
│   └── templates/         # 优化策略模板（与 MCP 版复用）
├── .gitignore
├── .env.example
├── test.py
├── requirements.txt
└── README.md
```

---

## License

AGPL-3.0
