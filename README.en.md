# Prompt Optimizer

A prompt optimization toolkit based on [prompt-optimizer](https://github.com/linshenkx/prompt-optimizer) templates, offering both an **MCP server** and a **zero-config Inline Skill**.

📦 npm: `npx prompt-optimizer-mcp`

---

## Tools

| Tool | Description | Use Case |
|------|-------------|----------|
| `optimize_user_prompt_basic` | Basic optimization: remove ambiguity, fill missing info | Daily chat, simple queries |
| `optimize_user_prompt_professional` | 5-dimension deep analysis + structured optimization | Need clear improvement direction |
| `optimize_user_prompt_planning` | Decompose multi-step tasks into structured steps | Complex workflows, data analysis |
| `iterate_prompt` | Iterate on existing optimized version with feedback | Fine-tuning optimized prompts |
| `evaluate_prompt` | 5-dimension quality score (0-100) + suggestions | Validate optimization results |
| `optimize_image_prompt` | Simple idea → high-quality English image prompt | Midjourney / Stable Diffusion |

---

## Quick Start (MCP Server)

### Install

```bash
# Option 1: global npm install
npm install -g prompt-optimizer-mcp

# Option 2: run with npx (no install)
npx prompt-optimizer-mcp
```

### Run

```bash
npx prompt-optimizer-mcp
```

---

## Integration

All MCP clients share the same config pattern:

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

| Client | Config File Location |
|--------|---------------------|
| Claude Desktop | `%APPDATA%\Claude\claude_desktop_config.json` |
| Claude Code (CLI) | `~/.claude/settings.json` or project `./claude.json` |
| Cursor | `~/.cursor/mcp.json` |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` |
| Opencode | project root `opencode.json` or `~/.config/opencode/config.json` |
| Continue (VS Code) | `~/.continue/config.json` |
| GitHub Copilot | `~/.github/copilot.json` |

After config, just tell your agent **"optimize this prompt"** to trigger.

---

## Inline Skill (Zero Config)

Uses the current conversation AI to optimize prompts directly — no external API key needed.

```
prompt-optimizer-mcp/
└── prompt-optimizer-skill/
    ├── SKILL.md               # Skill instructions
    └── templates/             # Optimization templates (same strategy as MCP)
```

### Installation

```bash
# Option 1: copy to global skills directory
cp -r prompt-optimizer-skill ~/.agents/skills/prompt-optimizer-1.0.0

# Option 2: copy to Claude Code skills
cp -r prompt-optimizer-skill ~/.claude/skills/prompt-optimizer
```

Once installed, the AI will automatically read the templates and optimize prompts when mentioned. No API key or model config required.

**Comparison with MCP version:**

| | MCP | Inline Skill |
|---|---|---|
| Execution | External LLM (DeepSeek/Ollama) | Current AI directly |
| Config | API_KEY + MODEL required | **Zero config** |
| Dependencies | mcp + openai Python packages | None |
| Integration target | MCP clients | Skill-capable agents |

---

## Architecture

```
User raw prompt
    ↓
┌─ Two execution paths ────────────┐
│                                  │
├─ MCP ────────────────────────────┤
│ mcp_server.py (dispatcher)       │
│   ├── select template (templates/)│
│   ├── replace {user_prompt}      │
│   └── call external LLM          │
│                                  │
├─ Inline Skill ───────────────────┤
│ prompt-optimizer-skill/SKILL.md  │
│   ├── read prompts-optimizer-skill/templates/  │
│   └── current AI optimizes      │
└──────────────────────────────────┘
    ↓
Optimized prompt
```

### Design Principles

- **Template-code separation**: optimization strategies in `templates/*.txt`, change strategies without touching code
- **Single call**: each tool calls LLM once, combining analysis and rewrite in one template
- **Evidence Framing**: user input wrapped as JSON field to prevent LLM from executing it
- **Variable preservation**: all `{{variable}}` placeholders are kept as-is

---

## Templates

6 templates covering major prompt optimization scenarios, based on [Prompt Engineering Guide](https://www.promptingguide.ai), Meta Prompting (Zhang et al. 2024) and industry best practices.

### Template Files

| File | Lines | Core Strategy | Output Format |
|------|-------|---------------|---------------|
| `user_optimize_basic.txt` | ~25 | Replace vague terms + add missing elements | Plain text prompt |
| `user_optimize_professional.txt` | ~45 | 5-dimension scoring + structured output | Analysis + optimized version |
| `user_optimize_planning.txt` | ~35 | Task decomposition → structured steps | Step-by-step sequence |
| `iterate_prompt.txt` | ~35 | Constraint integration + few-shot examples | Full modified version |
| `evaluate_prompt.txt` | ~40 | 5-dimension 0-100 scoring + JSON output | JSON |
| `image_optimize.txt` | ~55 | 5 frameworks (subject/environment/lighting/composition/style) | English prompt |

### References

| Source | Application |
|--------|-------------|
| Prompt Engineering Guide (DAIR.AI) | Role definition, delimiters, task decomposition |
| Meta Prompting (Zhang et al. 2024) | Structured output constraints, abstract examples |
| OpenAI Best Practices | "Say what to do, not what not to do" |
| Few-shot Prompting | Positive/negative examples in iterate template |
| Evaluation Framework | 5-dimension 0-100 scoring in evaluate template |

---

## Supported Models

Connect any OpenAI-compatible API via environment variables:

| Provider | API_BASE | MODEL Example | Cost |
|----------|----------|---------------|------|
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` | Low |
| Ollama (local) | `http://localhost:11434/v1` | `qwen2.5:7b` | Free |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` | Low |
| SiliconFlow | `https://api.siliconflow.cn/v1` | `Qwen/Qwen2.5-14B-Instruct` | Low |
| Groq | `https://api.groq.com/openai/v1` | `llama-3.3-70b` | Free |
| vLLM | `http://localhost:8000/v1` | Custom | Own hardware |

> **Tip**: Use small models (DeepSeek Chat / qwen2.5:7b) for optimization tasks, save large model capacity for main tasks.

---

## Extending: Add New Templates

1. Create a `.txt` file in `templates/`, use `{placeholder}` for variables
2. Add a corresponding `@mcp.tool()` function in `mcp_server.py`

Example — adding a translation prompt optimizer:

```python
@mcp.tool()
def optimize_translation_prompt(prompt: str) -> str:
    """Optimize translation prompts"""
    return _llm(_fill(_load("translate_optimize.txt"), user_prompt=prompt),
                json.dumps({"originalPrompt": prompt}, ensure_ascii=False))
```

---

## Cost Comparison vs Direct LLM Calls

| Approach | Calls | Token Cost | Use Case |
|----------|-------|------------|----------|
| Write prompt → call LLM | 1 large model | Low | One-shot simple tasks |
| Large model self-write + execute | Possibly 2 large model calls | High | Not recommended |
| This MCP (small model for optimization) | 1 small + 1 large model | Small model is cheap | Frequently reused prompts |
| This MCP (local model for optimization) | Local free + 1 large model | Near zero extra cost | Recommended |

**Key to cost saving**: small/local model for optimization, large model for main task.

---

## Directory Structure

```
prompt-optimizer-mcp/
├── package.json                # npm package metadata
├── index.js                    # Node.js wrapper → spawn python
├── install.js                  # postinstall: auto pip install
├── mcp_server.py               # MCP server entry (73 lines)
├── templates/                  # Optimization templates (for MCP)
│   ├── user_optimize_basic.txt
│   ├── user_optimize_professional.txt
│   ├── user_optimize_planning.txt
│   ├── iterate_prompt.txt
│   ├── evaluate_prompt.txt
│   └── image_optimize.txt
├── prompt-optimizer-skill/     # Zero-config Inline Skill
│   ├── SKILL.md
│   └── templates/              # Same strategy as MCP templates
├── .gitignore
├── .env.example
├── test.py
├── requirements.txt
├── README.md                   # Chinese
└── README.en.md                # English
```

---

## License

AGPL-3.0
