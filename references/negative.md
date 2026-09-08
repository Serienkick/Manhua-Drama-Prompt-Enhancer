# 漫剧负面提示词基线 v5（2026-09-08，75 词）

# 来源：v4 实战基线 + pixeldojo Wan2.2 官方默认模板 + whatlab/wink Wan2.2 指南
#       + CSDN《WAN2.2 长视频连贯性保障策略》推荐组合，去重整合
# 分类仅作注释用途；直接整段粘贴到引擎 negative_prompt 即可

# ── 画质噪损 ──
blurry, out of focus, low quality, worst quality, low resolution, grainy,
pixelated, jpeg artifacts, noise, overall gray, overexposed, bright colors,

# ── 形变（整体）──
distorted, warped, deformed, ugly, incomplete, mutation, bad proportions,

# ── 静止防劣化 ──
static, still picture, frozen, no motion,

# ── 时序伪影（帧间）──
flickering, jitter, jerky motion, ghosting, afterimages, duplicated frames,
morphing, unnatural movement, sudden changes, glitch, walking backwards,

# ── 画面异物 ──
watermark, logo, signature, username, subtitles, text, gibberish text,

# ── 人物解剖 ──
extra limbs, extra fingers, extra digits, too many fingers, fused fingers,
poorly drawn hands, malformed hands, missing fingers, missing limbs,
bad anatomy, disfigured, deformed face, distorted face, crossed eyes,
three legs, long neck, deformed body, distorted body, twisted limbs,
elongated body,

# ── 人物纪律（压幻觉路人/多人群）──
extra person, multiple people, many people in the background, crowd,
background people, second character,

# ── 场景稳定（长视频接力安全区：禁背景/场景擅自变化）──
background change, scene shift,

# ── 色彩退化 ──
color blocks, color bleeding, banding, posterization, flat colors,
oversaturated, chromatic aberration,

# ── 内容安全 ──
nsfw
