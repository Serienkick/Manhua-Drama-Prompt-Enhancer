# -*- coding: utf-8 -*-
"""sync.py — 本地 skill 目录 → GitHub 全量同步（Contents API）。

用法：
    python sync.py <github_token> [owner repo]

token 从命令行传（当次使用，不落盘）。脚本会把本目录下所有文件
（排除 .git）逐个推到仓库，已存在的文件自动带 sha 更新。

依赖：Python 标准库（urllib），无需 pip 安装。
"""
from __future__ import annotations

import base64
import json
import sys
import urllib.request
from pathlib import Path

SKIP_DIRS = {".git"}
FILES = ["README.md", "SKILL.md", "enhance.py", "references/rules.md", "references/negative.md"]


def api_request(token: str, url: str, method: str = "GET", body: dict | None = None) -> dict:
    headers = {
        "Authorization": "token " + token,
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def put_file(token: str, owner: str, repo: str, path: str, content: str) -> None:
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    try:
        cur = api_request(token, url)
        sha = cur.get("sha", "")
    except urllib.error.HTTPError:
        sha = ""  # 文件不存在 → 新建
    body = {"message": "sync " + path, "content": base64.b64encode(content.encode()).decode()}
    if sha:
        body["sha"] = sha
    api_request(token, url, "PUT", body)


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("用法: python sync.py <github_token> [owner repo]")
    token = sys.argv[1]
    owner = sys.argv[2] if len(sys.argv) > 2 else "Serienkick"
    repo = sys.argv[3] if len(sys.argv) > 3 else "Manhua-Drama-Prompt-Enhancer"
    for f in FILES:
        p = Path(__file__).parent / f
        if not p.exists():
            print(f"[skip] {f} 不存在")
            continue
        try:
            put_file(token, owner, repo, f, p.read_text(encoding="utf-8"))
            print(f"[OK] {f}")
        except Exception as e:  # noqa: BLE001
            print(f"[FAIL] {f}: {e}")
    print(f"同步完成 → https://github.com/{owner}/{repo}")


if __name__ == "__main__":
    main()
