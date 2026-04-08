#!/usr/bin/env python3
# 作用：在 Codex 准备结束当前请求时，强制做一次“技能沉淀自检”。
# 规则：
# 1. 若最后一条 assistant 回复里还没有“技能沉淀结论：...”标记，则阻止结束并要求补充。
# 2. 若已经有明确结论，则允许结束。

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

RESULT_PREFIX = '技能沉淀结论：'
PROMPT_FILE = Path.home() / '.codex' / 'prompts' / 'skill-sedimentation-standard-prompt.md'


def load_hook_input() -> dict[str, Any]:
    try:
        return json.load(os.sys.stdin)
    except Exception:
        return {}


def load_prompt_text() -> str:
    if PROMPT_FILE.is_file():
        return PROMPT_FILE.read_text()
    return (
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
        '🧠 技能沉淀自检\n'
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
        '完成当前请求后，不要急着结束，先检查这次是否产生了可复用知识。\n\n'
        '若有，先明确判断该落到哪一类：\n'
        '①跨仓库通用方法、规则、判断框架 → skill\n'
        '②当前仓库固定动作、命令、验收步骤 → 脚本 / workflow / 文档\n'
        '③长期约束、默认行为、提示词边界 → prompt / AGENTS.md\n\n'
        '如果命中任一类型，并且需要做经验归纳、技能提炼、旧 skill 修补或知识回灌，必须明确调用 claudeception 来完成归纳或修补，而不是只口头说明“值得沉淀”。\n\n'
        '若都不命中，明确写“不需要沉淀”，再结束。'
    )


def extract_last_assistant_text(hook_input: dict[str, Any]) -> str:
    direct_message = hook_input.get('last_assistant_message')
    if isinstance(direct_message, str) and direct_message.strip():
        return direct_message.strip()

    transcript_path = str(hook_input.get('transcript_path', '') or '')
    path = Path(transcript_path)
    if not path.is_file():
        return ''

    last_text = ''
    for raw_line in path.read_text(errors='ignore').splitlines():
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            obj = json.loads(raw_line)
        except Exception:
            continue

        message = obj.get('message') if isinstance(obj, dict) else None
        if not isinstance(message, dict):
            continue
        if message.get('role') != 'assistant':
            continue

        content = message.get('content', [])
        if not isinstance(content, list):
            continue

        texts: list[str] = []
        for item in content:
            if not isinstance(item, dict):
                continue
            if item.get('type') == 'text' and isinstance(item.get('text'), str):
                texts.append(item['text'])
        if texts:
            last_text = '\n'.join(texts)

    return last_text.strip()


def build_block_prompt(base_prompt: str) -> str:
    return (
        f'{base_prompt}\n\n'
        '你这次还没有给出明确的技能沉淀结论，先不要结束。\n'
        '请在完成自检后，在本次回复末尾明确追加且只追加一行：\n'
        '技能沉淀结论：不需要沉淀\n'
        '或\n'
        '技能沉淀结论：已调用 claudeception\n\n'
        '如果需要沉淀，先实际调用 claudeception，再结束。'
    )


def main() -> None:
    hook_input = load_hook_input()
    event_name = str(hook_input.get('hook_event_name', '') or '')

    if event_name != 'Stop':
        print(json.dumps({'continue': True}, ensure_ascii=False))
        return

    last_assistant_text = extract_last_assistant_text(hook_input)
    if RESULT_PREFIX in last_assistant_text:
        print(json.dumps({'continue': True}, ensure_ascii=False))
        return

    prompt_text = load_prompt_text()
    print(json.dumps({
        'decision': 'block',
        'reason': build_block_prompt(prompt_text),
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
