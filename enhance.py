# -*- coding: utf-8 -*-
"""漫剧提示词优化器：剧本 → 结构化分镜 JSON（cast 视觉锚 + 分镜 + 负面词）。

维度规则外置于 references/rules.md（活文档）：加/改维度只编辑该文件，
本脚本自动把全部 `## 维度：xxx` 小节拼进系统提示，无需改代码。

用法：
  python enhance.py --script "剧本文本" --style 国漫 --segments 6
  python enhance.py --file 剧本.txt --segments 8 --out out.json

依赖：本地 llama-server（127.0.0.1:8080，--alias gemma4-e4b，CPU 跑）。
输出：JSON {cast, master, shots:[{shot,text,action}], negative, engine, style}
      shots 可直接粘贴到工作台「结构化分镜」框；negative 可覆盖引擎默认负面词。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
RULES_PATH = SKILL_DIR / "references" / "rules.md"
NEGATIVE_PATH = SKILL_DIR / "references" / "negative.md"

_OUTPUT_SPEC = (
    "只输出一个 JSON 对象，不要输出任何其他文字：\n"
    '{"cast": "主角视觉卡+场景基调(按 cast 维度规则)", '
    '"master": "全片宏观提示词(一句话，含场景/光线/基调)", '
    '"shots": [{"shot": 1, "text": "画面描述(≤60字，按各维度规则)", "action": "画面运动(人物动作或运镜)"}]}'
)


def _load_rules() -> str:
    if not RULES_PATH.exists():
        sys.exit(f"[x] 找不到维度规则库: {RULES_PATH}")
    return RULES_PATH.read_text(encoding="utf-8")


def _load_negative() -> str:
    if NEGATIVE_PATH.exists():
        return NEGATIVE_PATH.read_text(encoding="utf-8").strip()
    return ""


def _build_system_prompt(style_hint: str) -> str:
    rules = _load_rules()
    return (
        "你是漫剧短视频的分镜提示词优化师，服务一个图生视频（TI2V）模型——"
        "它每次只能生成约 1 秒的短视频，多段接力拼成长片。\n"
        "你必须严格遵守下方《维度规则库》里的每一条规则来改写和拆分剧本。\n"
        f"\n=== 维度规则库（活文档，全部强制）===\n{rules}\n=== 规则库结束 ===\n"
        f"\n当前画风：{style_hint}\n"
        f"\n{_OUTPUT_SPEC}"
    )


def _chat(endpoint: str, model: str, system: str, user: str, timeout: float) -> str:
    import httpx

    r = httpx.post(
        f"{endpoint.rstrip('/')}/v1/chat/completions",
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.4,
            "stream": False,
        },
        timeout=timeout,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def _extract_json(text: str) -> dict | None:
    """从容错文本中提取 JSON 对象（剥 ```围栏 / 截取首尾花括号）。"""
    t = re.sub(r"```[a-z]*", "", text).strip()
    start, end = t.find("{"), t.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        return json.loads(t[start : end + 1])
    except json.JSONDecodeError:
        return None


def _normalize_shots(data: dict, segments: int) -> list[dict]:
    """宽容校验：截断/补齐 shots 到指定段数（借鉴引擎的放宽逻辑）。"""
    raw = data.get("shots") or []
    shots: list[dict] = []
    for i, s in enumerate(raw):
        if isinstance(s, dict):
            text = str(s.get("text", "")).strip()
            action = str(s.get("action", "")).strip()
        else:
            text, action = str(s).strip(), ""
        if text:
            shots.append({"shot": i + 1, "text": text[:80], "action": action[:60]})
    if not shots:
        return []
    if len(shots) > segments:
        shots = shots[:segments]
    elif len(shots) < segments:
        last = dict(shots[-1])
        while len(shots) < segments:
            nxt = dict(last)
            nxt["shot"] = len(shots) + 1
            shots.append(nxt)
    return shots


def main() -> None:
    ap = argparse.ArgumentParser(description="漫剧提示词优化器（维度规则见 references/rules.md）")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--script", help="剧本文本")
    src.add_argument("--file", help="剧本文件路径")
    ap.add_argument("--style", default="国漫", help="画风：国漫/日漫/3D/像素")
    ap.add_argument("--segments", type=int, default=6, help="分镜条数")
    ap.add_argument("--endpoint", default="http://127.0.0.1:8080", help="llama-server 地址")
    ap.add_argument("--model", default="gemma4-e4b")
    ap.add_argument("--timeout", type=float, default=300.0, help="CPU 生成较慢，默认 5 分钟")
    ap.add_argument("--out", help="输出 JSON 文件路径（默认打印 stdout）")
    args = ap.parse_args()

    script = args.script or Path(args.file).read_text(encoding="utf-8")
    script = script.strip()
    if not script:
        sys.exit("[x] 剧本为空")

    style_hints = {
        "国漫": "国漫风格，水墨线条，动态漫画分镜感",
        "日漫": "日式动画风格，赛璐璐上色，动漫质感",
        "3D": "3D 渲染，CG 质感，电影光照",
        "像素": "像素艺术风格，复古游戏画面",
    }
    style_hint = style_hints.get(args.style, args.style)
    system = _build_system_prompt(style_hint)
    user = f"剧本：{script[:1500]}\n分镜条数：{args.segments}（shots 恰好 {args.segments} 条）"

    data = None
    for attempt in (1, 2):
        try:
            raw = _chat(args.endpoint, args.model, system, user, args.timeout)
            data = _extract_json(raw)
            if data and data.get("shots"):
                break
            print(f"[!] 第 {attempt} 次尝试未得到合法 JSON，重试…", file=sys.stderr)
        except Exception as e:  # noqa: BLE001
            print(f"[!] 第 {attempt} 次尝试失败：{type(e).__name__}: {e}", file=sys.stderr)
    if not data or not data.get("shots"):
        sys.exit("[x] 优化失败：llama-server 不可达或连续两次输出非法。请确认 8080 已启动。")

    shots = _normalize_shots(data, args.segments)
    result = {
        "style": args.style,
        "cast": str(data.get("cast", "")).strip()[:200],
        "master": str(data.get("master", "")).strip()[:400],
        "shots": shots,
        "negative": _load_negative(),
        "engine": args.model,
        "endpoint": args.endpoint,
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"[OK] 已写入 {args.out}（{len(shots)} 个分镜）", file=sys.stderr)
    else:
        print(text)


if __name__ == "__main__":
    main()
