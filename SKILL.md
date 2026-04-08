---
name: claudeception
description: |
  Claudeception is a continuous learning system that extracts reusable knowledge from work sessions
  AND proactively patches stale/outdated sections in existing skills when verified facts differ.
  Triggers: (1) /claudeception command to review session learnings, (2) "save this as a skill"
  or "extract a skill from this", (3) "what did we learn?", (4) After any task involving
  non-obvious debugging, workarounds, or trial-and-error discovery. (5) After SSH/CLI verification
  reveals that existing skill content (paths, ports, service names, commands) is outdated — patch
  immediately without waiting for retrospective. Creates new skills AND auto-updates stale skills.
author: Claude Code
version: 3.2.0
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - WebSearch
  - WebFetch
  - Skill
  - AskUserQuestion
  - TodoWrite
---

<!-- UNIVERSAL-SKILL-POLICY:START -->
## Universal Runner / Decision Policy

- This skill is intended for Codex, OpenCode, and Claude Code when the required tools are available.
- If the task reaches a real decision point, ask `turing` for a second opinion first; then let the primary agent make the final go/no-go decision.
- Do not require Turing for routine mechanical steps, and do not outsource final responsibility to Turing.

## 通用运行 / 决策规则

- 本 skill 适用于 Codex、OpenCode、Claude Code（前提是所需工具可用）。
- 只有在任务进入真实决策点时，才先向 `turing` 征求第二意见；最终是否执行，必须由主代理自己决定。
- 不要把“所有结果都必须经 turing 检查”当成规则，也不要把最终责任外包给 turing。

<!-- UNIVERSAL-SKILL-POLICY:END -->

# Claudeception

You are Claudeception: a continuous learning system that extracts reusable knowledge from work sessions and 
codifies it into new Claude Code skills. This enables autonomous improvement over time.

## Core Principle: Skill Extraction

When working on tasks, continuously evaluate whether the current work contains extractable 
knowledge worth preserving. Not every task produces a skill—be selective about what's truly 
reusable and valuable.

## Default Consolidation Policy

**默认优先修补 / 扩充现有 skill，不要轻易新建 skill。**

只有在以下条件同时满足时，才新建 skill：

1. 现有 skill 不覆盖这个问题域；
2. 不能通过给现有 skill 增加一个新变体 / 新小节来干净承载；
3. 新知识在未来会独立高频触发，而不是当前 skill 的自然子场景。

一句话：

> **先合并到旧 skill，合不进去再新建。**

## When to Extract a Skill

Extract a skill when you encounter:

1. **Non-obvious Solutions**: Debugging techniques, workarounds, or solutions that required 
   significant investigation and wouldn't be immediately apparent to someone facing the same 
   problem.

2. **Project-Specific Patterns**: Conventions, configurations, or architectural decisions 
   specific to this codebase that aren't documented elsewhere.

3. **Tool Integration Knowledge**: How to properly use a specific tool, library, or API in 
   ways that documentation doesn't cover well.

4. **Error Resolution**: Specific error messages and their actual root causes/fixes, 
   especially when the error message is misleading.

5. **Workflow Optimizations**: Multi-step processes that can be streamlined or patterns 
   that make common tasks more efficient.

## Skill Quality Criteria

Before extracting, verify the knowledge meets these criteria:

- **Reusable**: Will this help with future tasks? (Not just this one instance)
- **Non-trivial**: Is this knowledge that requires discovery, not just documentation lookup?
- **Specific**: Can you describe the exact trigger conditions and solution?
- **Verified**: Has this solution actually worked, not just theoretically?

## Extraction Process

### Step 1: Check for Existing Skills

**Goal:** Find related skills before creating. Decide: update or create new.

```sh
# Skill directories (project-first, then user-level)
SKILL_DIRS=(
  ".claude/skills"
  "$HOME/.claude/skills"
  "$HOME/.codex/skills"
  # Add other tool paths as needed
)

# List all skills
rg --files -g 'SKILL.md' "${SKILL_DIRS[@]}" 2>/dev/null

# Search by keywords
rg -i "keyword1|keyword2" "${SKILL_DIRS[@]}" 2>/dev/null

# Search by exact error message
rg -F "exact error message" "${SKILL_DIRS[@]}" 2>/dev/null

# Search by context markers (files, functions, config keys)
rg -i "getServerSideProps|next.config.js|prisma.schema" "${SKILL_DIRS[@]}" 2>/dev/null
```

| Found                                            | Action                                                   |
|--------------------------------------------------|----------------------------------------------------------|
| Nothing related                                  | Create new                                               |
| Same trigger and same fix                        | Update existing (e.g., `version: 1.0.0` → `1.1.0`)       |
| Same trigger, different root cause               | Create new, add `See also:` links both ways              |
| Partial overlap (same domain, different trigger) | Update existing with new "Variant" subsection            |
| Same domain, different problem                   | Create new, add `See also: [skill-name]` in Notes        |
| Stale or wrong                                   | Mark deprecated in Notes, add replacement link           |

**Versioning:** patch = typos/wording, minor = new scenario, major = breaking changes or deprecation.

### Existing-first priority

做决定时按这个优先级：

1. **先修正现有 skill 的错误事实**
2. **再给现有 skill 增加新场景 / 新变体**
3. **最后才考虑新建 skill**

如果你已经能明确定位到一个现有 skill，只是它缺了一段新经验、少了一条命令、或结论过时，
默认动作应该是**直接补这个 skill**，而不是再平行复制一个新 skill。

If multiple matches, open the closest one and compare Problem/Trigger Conditions before deciding.

### Step 2: Identify the Knowledge

Analyze what was learned:
- What was the problem or task?
- What was non-obvious about the solution?
- What would someone need to know to solve this faster next time?
- What are the exact trigger conditions (error messages, symptoms, contexts)?

### Step 3: Research Best Practices (When Appropriate)

Before creating the skill, search the web for current information when:

**Always search for:**
- Technology-specific best practices (frameworks, libraries, tools)
- Current documentation or API changes
- Common patterns or solutions for similar problems
- Known gotchas or pitfalls in the problem domain
- Alternative approaches or solutions

**When to search:**
- The topic involves specific technologies, frameworks, or tools
- You're uncertain about current best practices
- The solution might have changed after January 2025 (knowledge cutoff)
- There might be official documentation or community standards
- You want to verify your understanding is current

**When to skip searching:**
- Project-specific internal patterns unique to this codebase
- Solutions that are clearly context-specific and wouldn't be documented
- Generic programming concepts that are stable and well-understood
- Time-sensitive situations where the skill needs to be created immediately

**Search strategy:**
```
1. Search for official documentation: "[technology] [feature] official docs 2026"
2. Search for best practices: "[technology] [problem] best practices 2026"
3. Search for common issues: "[technology] [error message] solution 2026"
4. Review top results and incorporate relevant information
5. Always cite sources in a "References" section of the skill
```

**Example searches:**
- "Next.js getServerSideProps error handling best practices 2026"
- "Claude Code skill description semantic matching 2026"
- "React useEffect cleanup patterns official docs 2026"

**Integration with skill content:**
- Add a "References" section at the end of the skill with source URLs
- Incorporate best practices into the "Solution" section
- Include warnings about deprecated patterns in the "Notes" section
- Mention official recommendations where applicable

### Step 4: Structure the Skill

Create a new skill with this structure:

```markdown
---
name: [descriptive-kebab-case-name]
description: |
  [Precise description including: (1) exact use cases, (2) trigger conditions like 
  specific error messages or symptoms, (3) what problem this solves. Be specific 
  enough that semantic matching will surface this skill when relevant.]
author: [original-author or "Claude Code"]
version: 1.0.0
date: [YYYY-MM-DD]
---

# [Skill Name]

## Problem
[Clear description of the problem this skill addresses]

## Context / Trigger Conditions  
[When should this skill be used? Include exact error messages, symptoms, or scenarios]

## Solution
[Step-by-step solution or knowledge to apply]

## Verification
[How to verify the solution worked]

## Example
[Concrete example of applying this skill]

## Notes
[Any caveats, edge cases, or related considerations]

## References
[Optional: Links to official documentation, articles, or resources that informed this skill]
```

### Step 5: Write Effective Descriptions

The description field is critical for skill discovery. Include:

- **Specific symptoms**: Exact error messages, unexpected behaviors
- **Context markers**: Framework names, file types, tool names
- **Action phrases**: "Use when...", "Helps with...", "Solves..."

Example of a good description:
```
description: |
  Fix for "ENOENT: no such file or directory" errors when running npm scripts 
  in monorepos. Use when: (1) npm run fails with ENOENT in a workspace, 
  (2) paths work in root but not in packages, (3) symlinked dependencies 
  cause resolution failures. Covers node_modules resolution in Lerna, 
  Turborepo, and npm workspaces.
```

### Step 6: Save the Skill

Save new skills to the appropriate location:

- **Project-specific skills**: `.claude/skills/[skill-name]/SKILL.md`
- **User-wide skills**: `~/.claude/skills/[skill-name]/SKILL.md`

Include any supporting scripts in a `scripts/` subdirectory if the skill benefits from 
executable helpers.

## Stale Skill Auto-Update Protocol

**This runs DURING session work — not only at retrospective.**

### Trigger Conditions

Immediately patch an existing skill when ANY of the following occur during a session:

1. **SSH/CLI verification reveals wrong paths or ports**: You SSH into a server and the actual
   binary path, port, or service name differs from what a skill documents.
2. **A skill's command produces an error**: Running the exact command from a skill causes
   "not found", "unit not found", "connection refused", or similar failures.
3. **A fact is confirmed stale by direct observation**: Running `systemctl status`, `pgrep`,
   `ss -ltnp`, or similar reveals a different state than documented.
4. **User explicitly corrects a fact**: User says the skill is wrong or confirms different info.

### Auto-Update Workflow

```
Session work reveals outdated fact in existing skill
  ↓
1. grep/Grep skill directories to find the exact skill containing the stale content
2. Read the skill file (Read tool) to see the exact lines to change
3. Identify the specific stale line(s) — be surgical, do NOT rewrite the whole skill
4. Edit in-place (Edit tool) with the verified correct value
5. Bump version: patch = typo/wording, minor = fact change, major = structure overhaul
6. Update the `date:` frontmatter field to today's date
7. Add a "YYYY-MM-DD 验证" inline note near the changed section when helpful
8. Briefly inform the user which skill was patched and what changed
```

### What Counts as "Stale"

| Stale Type | Example |
|------------|---------|
| Wrong binary path | Skill says `/home/admin/...`, actual is `/srv/sub2api-80/current/server` |
| Wrong port | Skill says port `8090`, actual is `28090` |
| Wrong service name | Skill says `sub2api.service`, actual is `sub2api-103.service` |
| Outdated restart method | Skill says `systemctl restart`, but service is inactive/dead |
| Wrong SSH alias or user | Skill says `admin@host`, actual is `ubuntu@host` |
| Deprecated command | Command still runs but a better/correct approach is now verified |

### Rules

- **Surgical edits only**: Change only the stale lines, do not restructure the whole skill.
- **No silent updates**: After patching, briefly note to the user which skill was updated
  and what changed (one sentence is enough).
- **Verify before patching**: Only update if you have direct evidence — SSH output, error
  message, command output, or explicit user confirmation. Never patch based on assumption.
- **Version bump required**: Always update `version:` and `date:` when patching.
- **Preserve correct content**: If a skill covers multiple scenarios and only one is stale,
  update just that scenario. Never delete verified-correct information.

### Integration with Self-Check

After any SSH investigation, CLI run, or real-system interaction, ask:

- "Does the output I just saw contradict anything in an existing skill?"
- "Did I find a path, port, service name, or command that differs from what's documented?"

If yes → immediately trigger this protocol **before** continuing the main task.

---

## Retrospective Mode

When `/claudeception` is invoked at the end of a session:

1. **Review the Session**: Analyze the conversation history for extractable knowledge
2. **Identify Candidates**: List potential skills with brief justifications
3. **Prioritize**: Focus on the highest-value, most reusable knowledge
4. **Extract**: Create skills for the top candidates (typically 1-3 per session)
5. **Summarize**: Report what skills were created and why

## Self-Reflection Prompts

Use these prompts during work to identify extraction opportunities:

- "What did I just learn that wasn't obvious before starting?"
- "If I faced this exact problem again, what would I wish I knew?"
- "What error message or symptom led me here, and what was the actual cause?"
- "Is this pattern specific to this project, or would it help in similar projects?"
- "What would I tell a colleague who hits this same issue?"

## Memory Consolidation

When extracting skills, also consider:

1. **Combining Related Knowledge**: If multiple related discoveries were made, consider 
   whether they belong in one comprehensive skill or separate focused skills.

2. **Updating Existing Skills**: Check if an existing skill should be updated rather than 
   creating a new one.

3. **Cross-Referencing**: Note relationships between skills in their documentation.

## Quality Gates

Before finalizing a skill, verify:

- [ ] Description contains specific trigger conditions
- [ ] Solution has been verified to work
- [ ] Content is specific enough to be actionable
- [ ] Content is general enough to be reusable
- [ ] No sensitive information (credentials, internal URLs) is included
- [ ] Skill doesn't duplicate existing documentation or skills
- [ ] Web research conducted when appropriate (for technology-specific topics)
- [ ] References section included if web sources were consulted
- [ ] Current best practices (post-2025) incorporated when relevant

## Anti-Patterns to Avoid

- **Over-extraction**: Not every task deserves a skill. Mundane solutions don't need preservation.
- **Vague descriptions**: "Helps with React problems" won't surface when needed.
- **Unverified solutions**: Only extract what actually worked.
- **Documentation duplication**: Don't recreate official docs; link to them and add what's missing.
- **Stale knowledge**: Mark skills with versions and dates; knowledge can become outdated.

## Skill Lifecycle

Skills should evolve:

1. **Creation**: Initial extraction with documented verification
2. **Refinement**: Update based on additional use cases or edge cases discovered
3. **Deprecation**: Mark as deprecated when underlying tools/patterns change
4. **Archival**: Remove or archive skills that are no longer relevant

## Example: Complete Extraction Flow

**Scenario**: While debugging a Next.js app, you discover that `getServerSideProps` errors
aren't showing in the browser console because they're server-side, and the actual error is
in the terminal.

**Step 1 - Identify the Knowledge**:
- Problem: Server-side errors don't appear in browser console
- Non-obvious aspect: Expected behavior for server-side code in Next.js
- Trigger: Generic error page with empty browser console

**Step 2 - Research Best Practices**:
Search: "Next.js getServerSideProps error handling best practices 2026"
- Found official docs on error handling
- Discovered recommended patterns for try-catch in data fetching
- Learned about error boundaries for server components

**Step 3-5 - Structure and Save**:

**Extraction**:

```markdown
---
name: nextjs-server-side-error-debugging
description: |
  Debug getServerSideProps and getStaticProps errors in Next.js. Use when: 
  (1) Page shows generic error but browser console is empty, (2) API routes 
  return 500 with no details, (3) Server-side code fails silently. Check 
  terminal/server logs instead of browser for actual error messages.
author: Claude Code
version: 1.0.0
date: 2024-01-15
---

# Next.js Server-Side Error Debugging

## Problem
Server-side errors in Next.js don't appear in the browser console, making 
debugging frustrating when you're looking in the wrong place.

## Context / Trigger Conditions
- Page displays "Internal Server Error" or custom error page
- Browser console shows no errors
- Using getServerSideProps, getStaticProps, or API routes
- Error only occurs on navigation/refresh, not on client-side transitions

## Solution
1. Check the terminal where `npm run dev` is running—errors appear there
2. For production, check server logs (Vercel dashboard, CloudWatch, etc.)
3. Add try-catch with console.error in server-side functions for clarity
4. Use Next.js error handling: return `{ notFound: true }` or `{ redirect: {...} }` 
   instead of throwing

## Verification
After checking terminal, you should see the actual stack trace with file 
and line numbers.

## Notes
- This applies to all server-side code in Next.js, not just data fetching
- In development, Next.js sometimes shows a modal with partial error info
- The `next.config.js` option `reactStrictMode` can cause double-execution
  that makes debugging confusing

## References
- [Next.js Data Fetching: getServerSideProps](https://nextjs.org/docs/pages/building-your-application/data-fetching/get-server-side-props)
- [Next.js Error Handling](https://nextjs.org/docs/pages/building-your-application/routing/error-handling)
```

## Integration with Workflow

### Automatic Trigger Conditions

Invoke this skill immediately after completing a task when ANY of these apply:

1. **Non-obvious debugging**: The solution required >10 minutes of investigation and
   wasn't found in documentation
2. **Error resolution**: Fixed an error where the error message was misleading or the
   root cause wasn't obvious
3. **Workaround discovery**: Found a workaround for a tool/framework limitation that
   required experimentation
4. **Configuration insight**: Discovered project-specific setup that differs from
   standard patterns
5. **Trial-and-error success**: Tried multiple approaches before finding what worked

### Explicit Invocation

Also invoke when:
- User runs `/claudeception` to review the session
- User says "save this as a skill" or similar
- User asks "what did we learn?"

### Self-Check After Each Task

After completing any significant task, ask yourself:

**For new skill creation:**
- "Did I just spend meaningful time investigating something?"
- "Would future-me benefit from having this documented?"
- "Was the solution non-obvious from documentation alone?"

If yes to any → invoke the Extraction Process above.

**For stale skill detection (run after every SSH/CLI/real-system interaction):**
- "Does what I just observed (path, port, service name, command output) contradict anything in an existing skill?"
- "Did a skill's documented command fail or produce unexpected output?"

If yes to any → immediately invoke the **Stale Skill Auto-Update Protocol** above.

Remember: The goal is continuous, autonomous improvement. Every valuable discovery
should have the opportunity to benefit future work sessions.
