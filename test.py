"""验证6个模板全部可加载 + 快速测试每个工具"""
import os, json, pathlib, dotenv
dotenv.load_dotenv()
from openai import OpenAI

_TDIR = pathlib.Path(__file__).parent / "templates"
files = [f.name for f in sorted(_TDIR.glob("*.txt"))]
print(f"模板文件 ({len(files)}个):")
for f in files:
    t = (_TDIR / f).read_text(encoding="utf-8")
    print(f"  OK {f}  ({len(t)} chars)")

def _fill(tpl, **kw):
    for k, v in kw.items(): tpl = tpl.replace("{" + k + "}", v)
    return tpl

client = OpenAI(base_url=os.getenv("OPTIMIZER_API_BASE"), api_key=os.getenv("OPTIMIZER_API_KEY"))
MODEL = os.getenv("OPTIMIZER_MODEL", "deepseek-chat")

def _llm(system, user):
    return client.chat.completions.create(
        model=MODEL,
        messages=[{"role":"system","content":system},{"role":"user","content":user}],
        temperature=0.3,
    ).choices[0].message.content

print(f"\n测试模型: {MODEL}\n")

tests = [
    ("user_optimize_basic.txt",       "帮我写个文章", "基础优化"),
    ("user_optimize_professional.txt","分析这个数据", "深度优化"),
    ("user_optimize_planning.txt",    "先搜索文献再总结最后生成报告", "规划式优化"),
    ("iterate_prompt.txt",            "你是一个翻译助手,请翻译内容|让它更正式", "迭代改进"),
    ("evaluate_prompt.txt",           "你是一个翻译助手，请翻译以下内容", "质量评估"),
    ("image_optimize.txt",            "a cat in the rain", "文生图优化"),
]

for fname, inp, desc in tests:
    tpl = (_TDIR / fname).read_text(encoding="utf-8")
    if fname == "iterate_prompt.txt":
        cur, inp_req = [x.strip() for x in inp.split("|")]
        system = _fill(_fill(tpl, current_prompt=cur), iterate_input=inp_req)
        user = json.dumps({"currentPrompt": cur, "iterateInput": inp_req}, ensure_ascii=False)
    elif fname == "evaluate_prompt.txt":
        system = _fill(tpl, prompt_text=inp)
        user = json.dumps({"promptText": inp}, ensure_ascii=False)
    else:
        system = _fill(tpl, user_prompt=inp)
        user = json.dumps({"originalPrompt": inp}, ensure_ascii=False)

    print(f"── {desc} ──")
    try:
        result = _llm(system, user)
        print(f"  -> {result[:100]}...")
    except Exception as e:
        print(f"  X {e}")
