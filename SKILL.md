---
name: comic-prompt-enhancer
description: 漫剧（AI 视频）提示词优化器。把口语化剧本优化成结构化分镜 JSON——cast 视觉锚（身份锁）、单主角画面纪律、防畸变动作、时序连续、负面词基线。输出可直接粘贴到 comic-drama-platform 工作台的「结构化分镜」框，或作为长视频 prompt_plan 使用。维度规则外置于 references/rules.md（活文档：加维度只编辑规则文件，脚本零改动）。依赖本地 llama-server（127.0.0.1:8080，gemma4-e4b）。
---

# comic-prompt-enhancer — 漫剧提示词优化器

把一段口语化剧本，按「漫剧生成管线实战沉淀的维度规则」优化成结构化分镜 JSON。

## 何时用

- 要在 `http://127.0.0.1:1234/comic-drama/` 生成漫剧，想让分镜质量更高（防畸变、防幻觉路人、角色一致）
- 长视频接力前，想要一份带 cast 锁和时序连续性的分镜计划（prompt_plan）

## 用法

```bash
# 基础：剧本 → 6 条分镜 JSON（打印到终端）
python enhance.py --script "阿强在菜市场被雷劈中，重生回三天前的清晨……"

# 指定画风/段数/输出文件
python enhance.py --file 剧本.txt --style 日漫 --segments 8 --out plan.json
```

输出 JSON 结构：

```json
{
  "style": "国漫",
  "cast": "红发少年阿强，蓝色粗布衫，菜摊竹筐……（视觉锚，全片复用）",
  "master": "全片宏观提示词",
  "shots": [{"shot": 1, "text": "画面描述≤60字", "action": "缓推镜头"}],
  "negative": "（42 词负面词基线，来自 references/negative.md）"
}
```

- `shots` 直接粘贴到工作台「结构化分镜（JSON 数组）」框即可生成
- `cast` 已被管线自动前缀到每段（身份锁），无需手动带
- `negative` 可在需要时覆盖引擎默认负面词

## 如何加维度（核心设计）

**维度规则是活文档**：编辑 `references/rules.md`，每个 `## 维度：xxx` 小节是一个独立
维度，enhance.py 每次运行自动把全部小节拼进系统提示——**加维度只改这个文件，代码不动**。
删小节即停用；写法上每条规则越具体（可执行、可判定的指令），LLM 执行越稳。

## 依赖

- 本地 llama-server：`127.0.0.1:8080`（gemma4-e4b，CPU；启动脚本 `C:\Users\Administrator\llamacpp\start-llama.bat`）
- 主后端默认 venv 里已有 httpx；独立运行需 `pip install httpx`

## 排障

- `llama-server 不可达` → 跑 start-llama.bat 或检查 8080
- 连续两次非法 JSON → 降低 segments 或缩短剧本后重试（CPU 小模型长输出易破格式）
- 想换推理后端 → `--endpoint` / `--model` 参数（任何 OpenAI 兼容接口均可）
