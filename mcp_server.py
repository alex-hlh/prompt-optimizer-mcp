import os, json, pathlib
from openai import OpenAI
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("prompt-optimizer", instructions="AI提示词优化服务 - 优化/迭代/评估/图片提示词")

_TDIR = pathlib.Path(__file__).parent / "templates"
def _load(name: str) -> str: return (_TDIR / name).read_text(encoding="utf-8")

client = OpenAI(
    base_url=os.getenv("OPTIMIZER_API_BASE", "https://api.openai.com/v1"),
    api_key=os.getenv("OPTIMIZER_API_KEY", ""),
)
MODEL = os.getenv("OPTIMIZER_MODEL", "gpt-4o-mini")

def _fill(tpl: str, **kw) -> str:
    for k, v in kw.items(): tpl = tpl.replace("{" + k + "}", v)
    return tpl

def _llm(system: str, user: str) -> str:
    return client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.3,
    ).choices[0].message.content

# ── 用户提示词优化 ────────────────────────────────────

@mcp.tool()
def optimize_user_prompt_basic(prompt: str) -> str:
    """基础优化：消除模糊表述，补充缺失信息，提升清晰度"""
    return _llm(_fill(_load("user_optimize_basic.txt"), user_prompt=prompt),
                json.dumps({"originalPrompt": prompt}, ensure_ascii=False))

@mcp.tool()
def optimize_user_prompt_professional(prompt: str) -> str:
    """深度优化：结构化分析5个维度后输出优化版，附带优化分析"""
    return _llm(_fill(_load("user_optimize_professional.txt"), user_prompt=prompt),
                json.dumps({"originalPrompt": prompt}, ensure_ascii=False))

@mcp.tool()
def optimize_user_prompt_planning(prompt: str) -> str:
    """规划式优化：将复杂多步骤任务拆解为结构化步骤序列"""
    return _llm(_fill(_load("user_optimize_planning.txt"), user_prompt=prompt),
                json.dumps({"originalPrompt": prompt}, ensure_ascii=False))

# ── 迭代改进 ──────────────────────────────────────────

@mcp.tool()
def iterate_prompt(current_prompt: str, iterate_input: str) -> str:
    """基于改进需求对当前优化版本进行迭代优化"""
    tpl = _load("iterate_prompt.txt")
    return _llm(_fill(_fill(tpl, current_prompt=current_prompt), iterate_input=iterate_input),
                json.dumps({"currentPrompt": current_prompt, "iterateInput": iterate_input}, ensure_ascii=False))

# ── 评估 ──────────────────────────────────────────────

@mcp.tool()
def evaluate_prompt(prompt_text: str) -> str:
    """对提示词进行5维度质量评分（目标清晰度/指令完整性/结构可执行性/歧义控制/鲁棒性）"""
    return _llm(_fill(_load("evaluate_prompt.txt"), prompt_text=prompt_text),
                json.dumps({"promptText": prompt_text}, ensure_ascii=False))

# ── 文生图提示词优化 ─────────────────────────────────

@mcp.tool()
def optimize_image_prompt(prompt: str) -> str:
    """将简单的想法优化为高质量的文生图英文提示词（含主体/环境/光线/风格）"""
    return _llm(_fill(_load("image_optimize.txt"), user_prompt=prompt),
                json.dumps({"originalPrompt": prompt}, ensure_ascii=False))

if __name__ == "__main__":
    mcp.run()
