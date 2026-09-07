# comic-prompt-enhancer

漫剧（AI 视频分段生成）提示词优化器 —— 把口语化剧本，按「漫剧生成管线实战沉淀的维度规则」，优化成结构化分镜 JSON。

> 配套平台：[comic-drama-platform](https://github.com/Serienkick)（Wan2.2 TI2V 本地视频生成）的提示词层。
> 输出可直接粘贴到工作台「结构化分镜」框，或作为长视频接力的 `prompt_plan`。

## 它能做什么

输入一段剧本文本，输出：

```json
{
  "style": "国漫",
  "cast": "主角视觉卡 + 场景基调（全片身份锁）",
  "master": "全片宏观提示词",
  "shots": [{"shot": 1, "text": "画面描述", "action": "运镜/动作"}],
  "negative": "负面词基线 v4（42 词）"
}
```

`cast` 被管线自动前缀到每一段生成（身份锁，治「同一角色不同素材」）；`negative` 与引擎 v4 负面词同源（治色块/畸变/幻觉路人）。

## 内置维度

| 维度 | 作用 |
|------|------|
| cast 视觉锚 | 主角恒定外观 + 场景基调，全片一致 |
| 单主角画面纪律 | 其他角色只提及不画入，禁人群（治「未知人物」） |
| 动作幅度与景别 | 中近景 + 小中幅动作（治「人物大变形」） |
| 时序连续性 | 相邻分镜动作递进、「承接上一段」句式 |
| 动感与画面健康 | 禁静止/纯色，每镜必有运动元素 |
| 运动三分法 | 镜头运动为主 + 主角小动作 + 环境运动点睛 |
| 输出适配 | text≤60 字、action 运镜、段数对齐 |

## 用法

```bash
# 剧本 → 6 条分镜 JSON
python enhance.py --script "阿强在菜市场被雷劈中，重生回三天前的清晨……"

# 指定画风/段数/输出文件
python enhance.py --file 剧本.txt --style 日漫 --segments 8 --out plan.json
```

依赖：本地 llama-server（`127.0.0.1:8080`，gemma-4-E4B，CPU）。任何 OpenAI 兼容接口均可通过 `--endpoint` / `--model` 替换。

## 加维度（核心设计）

**维度规则是活文档**：编辑 `references/rules.md`，新增 `## 维度：你的维度名` 小节即可——
`enhance.py` 每次运行自动把全部小节拼进系统提示，**代码零改动**。删小节即停用。

## 目录结构

```
comic-prompt-enhancer/
├── SKILL.md              # WorkBuddy 技能说明
├── enhance.py            # 入口脚本
├── README.md
└── references/
    ├── rules.md          # ⭐ 维度规则库（活文档）
    └── negative.md       # 负面词基线
```

## 许可

Apache-2.0
