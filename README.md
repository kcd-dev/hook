# Claudeception

Every time you use an AI coding agent, it starts from zero. You spend an hour debugging some obscure error, the agent figures it out, session ends. Next time you hit the same issue? Another hour.

This skill fixes that. When Claude Code discovers something non-obvious (a debugging technique, a workaround, some project-specific pattern), it saves that knowledge as a new skill. Next time a similar problem comes up, the skill gets loaded automatically.

## Installation

### Step 1: Clone the skill

**User-level (recommended)**

```bash
git clone https://github.com/blader/Claudeception.git ~/.claude/skills/claudeception
```

**Project-level**

```bash
git clone https://github.com/blader/Claudeception.git .claude/skills/claudeception
```

### Step 2: Set up the activation hook (recommended)

The skill can activate via semantic matching, but a hook ensures it evaluates every session for extractable knowledge.

#### Option A: Use the built-in activator script

##### User-level setup (recommended)

1. Create the hooks directory and copy the script:

```bash
mkdir -p ~/.claude/hooks
cp ~/.claude/skills/claudeception/scripts/claudeception-activator.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/claudeception-activator.sh
```

2. Add the hook to your global Claude settings (`~/.claude/settings.json`):

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/claudeception-activator.sh"
          }
        ]
      }
    ]
  }
}
```

##### Project-level setup

1. Create the hooks directory inside your project and copy the script:

```bash
mkdir -p .claude/hooks
cp .claude/skills/claudeception/scripts/claudeception-activator.sh .claude/hooks/
chmod +x .claude/hooks/claudeception-activator.sh
```

2. Add the hook to your project settings (`.claude/settings.json` in the repo):

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/claudeception-activator.sh"
          }
        ]
      }
    ]
  }
}
```

If you already have a `settings.json`, merge the `hooks` configuration into it.

#### Option B: Use [`kcd-dev/hook`](https://github.com/kcd-dev/hook)

If you already use `hook` as your centralized hook runner, you can register the same reminder there instead of copying the standalone shell script around.

Repository:

```text
https://github.com/kcd-dev/hook
```

Recommended use: keep Claudeception's knowledge-consolidation reminder as one managed hook prompt inside your shared hook system, then trigger `claudeception` only when the reminder determines there is reusable knowledge to preserve.

#### Practical integration guidance

When wiring this into a generic hook runner such as `kcd-dev/hook`, the safest pattern is:

1. attach the reminder to your **end-of-request / stop / final-response** stage, not the very beginning of the run
2. use the prompt below as a **post-run self-check**, so the model must explicitly classify whether the result should become a skill, workflow, or prompt rule
3. keep the final one-line verdict requirement, so every run ends with a machine-checkable consolidation status
4. if the verdict is `技能沉淀结论：已调用 claudeception`, require the agent to actually invoke `claudeception` before finishing

This avoids the common failure mode where a hook only says "remember to learn from this" but never forces an actual yes/no consolidation decision.

Full Codex setup guide:

- `docs/codex-hook-setup.md`
- `scripts/codex-claudeception-stop-hook.py`
- `resources/skill-sedimentation-standard-prompt.md`

## Recommended knowledge-consolidation prompt

You can place the following prompt into your hook system or agent reminder configuration. This is the exact self-check prompt used to force an explicit consolidation decision at the end of each request.

```text
完成当前请求后，不要急着结束，
先检查这次是否产生了可复用知识。若有，先明确判断该落到哪一类：①跨仓库
通用方法、规则、判断框架 → skill②当前仓库固定动作、命令、验收步骤 → 脚
本 / workflow / 文档③长期约束、默认行为、提示词边界 → prompt /
AGENTS.md以下情况默认优先判断需要沉淀：- 出现了非直觉排障或试错后才定
位到的根因- 发现旧 skill / 旧提示词 / 旧文档已经过期，需要修补- 形成了
以后会复用的部署、验收、排查、发布、Hook、工作流步骤- 发现了“以前以为
是这样，其实真实运行态不是这样”的新事实如果命中任一类型，并且需要做经
验归纳、技能提炼、旧 skill 修补或知识回灌，必须明确调用 claudeception
来完成归纳或修补，而不是只在总结里顺口说一句“值得沉淀”。若都不命中，明
确写“不需要沉淀”，再结束。你这次还没有给出明确的技能沉淀结论，先不要结
束。请在完成自检后，在本次回复末尾明确追加且只追加一行：技能沉淀结论：
不需要沉淀或技能沉淀结论：已调用 claudeception如果需要沉淀，先实际调用
claudeception，再结束。
```

What this prompt enforces:

- classify the learning target first: skill / workflow / prompt
- prefer patching stale knowledge instead of casually mentioning it
- require an explicit final consolidation verdict on every run
- force an actual `claudeception` call before claiming consolidation happened

The hook injects a reminder on every prompt that tells Claude to evaluate whether the current task produced extractable knowledge. This achieves higher activation rates than relying on semantic description matching alone.

## Usage

### Automatic Mode

The skill activates automatically when Claude Code:
- Just completed debugging and discovered a non-obvious solution
- Found a workaround through investigation or trial-and-error
- Resolved an error where the root cause wasn't immediately apparent
- Learned project-specific patterns or configurations through investigation
- Completed any task where the solution required meaningful discovery

### Explicit Mode

Trigger a learning retrospective:

```
/claudeception
```

Or explicitly request skill extraction:

```
Save what we just learned as a skill
```

### What Gets Extracted

Not every task produces a skill. It only extracts knowledge that required actual discovery (not just reading docs), will help with future tasks, has clear trigger conditions, and has been verified to work.

## Research

The idea comes from academic work on skill libraries for AI agents.

[Voyager](https://arxiv.org/abs/2305.16291) (Wang et al., 2023) showed that game-playing agents can build up libraries of reusable skills over time, and that this helps them avoid re-learning things they already figured out. [CASCADE](https://arxiv.org/abs/2512.23880) (2024) introduced "meta-skills" (skills for acquiring skills), which is what this is. [SEAgent](https://arxiv.org/abs/2508.04700) (2025) showed agents can learn new software environments through trial and error, which inspired the retrospective feature. [Reflexion](https://arxiv.org/abs/2303.11366) (Shinn et al., 2023) showed that self-reflection helps.

Agents that persist what they learn do better than agents that start fresh.

## How It Works

Claude Code has a native skills system. At startup, it loads skill names and descriptions (about 100 tokens each). When you're working, it matches your current context against those descriptions and pulls in relevant skills.

But this retrieval system can be written to, not just read from. So when this skill notices extractable knowledge, it writes a new skill with a description optimized for future retrieval.

The description matters a lot. "Helps with database problems" won't match anything useful. "Fix for PrismaClientKnownRequestError in serverless" will match when someone hits that error.

More on the skills architecture [here](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills).

## Skill Format

Extracted skills are markdown files with YAML frontmatter:

```yaml
---
name: prisma-connection-pool-exhaustion
description: |
  Fix for PrismaClientKnownRequestError: Too many database connections 
  in serverless environments (Vercel, AWS Lambda). Use when connection 
  count errors appear after ~5 concurrent requests.
author: Claude Code
version: 1.0.0
date: 2024-01-15
---

# Prisma Connection Pool Exhaustion

## Problem
[What this skill solves]

## Context / Trigger Conditions
[Exact error messages, symptoms, scenarios]

## Solution
[Step-by-step fix]

## Verification
[How to confirm it worked]
```

See `resources/skill-template.md` for the full template.

## Quality Gates

The skill is picky about what it extracts. If something is just a documentation lookup, or only useful for this one case, or hasn't actually been tested, it won't create a skill. Would this actually help someone who hits this problem in six months? If not, no skill.

## Examples

See `examples/` for sample skills:

- `nextjs-server-side-error-debugging/`: errors that don't show in browser console
- `prisma-connection-pool-exhaustion/`: the "too many connections" serverless problem
- `typescript-circular-dependency/`: detecting and fixing import cycles

## Contributing

Contributions welcome. Fork, make changes, submit a PR.

## License

MIT
