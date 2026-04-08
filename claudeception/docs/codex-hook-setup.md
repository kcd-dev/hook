# Codex Hook 配置文档

测试日期：2026-04-08
文档版本：v1.0.0

## 目标

本文档基于当前 `~/.codex/hooks.json` 的真实结构，说明如何把 Claudeception 的“技能沉淀自检”接入 Codex 的 `Stop` Hook，做到：

1. 每次准备结束当前请求时，自动检查本轮是否产生了可复用知识
2. 如果还没给出明确的“技能沉淀结论”，阻止本次结束
3. 要求代理在回复末尾追加统一格式的结论行
4. 若判断需要沉淀，必须先实际调用 `claudeception`

## 适用场景

适用于以下需求：

- 想把技能沉淀检查固定为 Codex 全局默认动作
- 想避免代理“口头说值得沉淀”，但实际上没有真正沉淀
- 想给团队统一一个可机读、可审计的收尾约束

## 文件清单

建议使用仓库内这两个文件：

- `scripts/codex-claudeception-stop-hook.py`
- `resources/skill-sedimentation-standard-prompt.md`

## 安装步骤

### 方案一：直接引用仓库内文件（推荐）

假设你把仓库放在：

```bash
/path/to/hook
```

那么 `~/.codex/hooks.json` 可以按你当前本机格式写成：

```json
{
  "description": "Codex 全局 hooks，模仿 ~/.claude/settings.json 的核心行为",
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /path/to/hook/scripts/codex-claudeception-stop-hook.py",
            "timeout": 30,
            "statusMessage": "正在执行技能沉淀收尾检查"
          }
        ]
      }
    ]
  }
}
```

然后把提示词文件复制到：

```bash
mkdir -p ~/.codex/prompts
cp /path/to/hook/resources/skill-sedimentation-standard-prompt.md ~/.codex/prompts/
```

### 方案二：复制到用户目录

如果你希望 Hook 不依赖仓库路径，可以把脚本和提示词复制到 `~/.codex` 下：

```bash
mkdir -p ~/.codex/hooks ~/.codex/prompts
cp /path/to/hook/scripts/codex-claudeception-stop-hook.py ~/.codex/hooks/
cp /path/to/hook/resources/skill-sedimentation-standard-prompt.md ~/.codex/prompts/
chmod +x ~/.codex/hooks/codex-claudeception-stop-hook.py
```

此时 `~/.codex/hooks.json` 也建议继续沿用你当前这套格式：

```json
{
  "description": "Codex 全局 hooks",
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.codex/hooks/codex-claudeception-stop-hook.py",
            "timeout": 30,
            "statusMessage": "正在执行技能沉淀收尾检查"
          }
        ]
      }
    ]
  }
}
```

## 工作原理

这个 Stop Hook 的逻辑是：

1. Codex 在本轮准备结束时触发 `Stop`
2. Hook 脚本从标准输入读取 Hook 上下文（即 Codex 传给 command hook 的 JSON）
3. 它会优先读取最后一条 assistant 回复
4. 如果最后一条回复里已经包含：

```text
技能沉淀结论：
```

则直接放行

5. 如果没有这个结论行，则返回一个 `block` 决策，把“技能沉淀自检”提示重新注入当前回合，要求代理补完

## 结论格式约束

代理最终必须在回复末尾追加且只追加一行：

```text
技能沉淀结论：不需要沉淀
```

或：

```text
技能沉淀结论：已调用 claudeception
```

如果判断需要沉淀，必须先真的调用 `claudeception`，不能只写字面结论。

## 自定义提示词

默认读取路径：

```text
~/.codex/prompts/skill-sedimentation-standard-prompt.md
```

如果这个文件存在，Hook 会优先使用它；如果不存在，则退回脚本内置的默认提示词。

因此推荐做法是：

- 把团队统一的沉淀规范写进这个 markdown 文件
- Hook 脚本保持稳定
- 后续只改 prompt，不改脚本

## 如何验证是否生效

### 验证 1：缺少结论时会被拦住

让代理完成一个简单请求，但不要主动输出“技能沉淀结论：...”

预期结果：

- Codex 不会直接结束
- 会收到一段“技能沉淀自检”的补充提示
- 代理被要求补写最终结论行

### 验证 2：已有结论时直接放行

让代理回复末尾明确带上：

```text
技能沉淀结论：不需要沉淀
```

预期结果：

- Stop Hook 不再阻塞
- 本轮直接正常结束

## 安全注意事项

### 不要写进文档或脚本的内容

禁止把以下内容硬编码进仓库：

- API Key
- Token
- Cookie
- Session
- 真实生产密码
- 含敏感路径的私有目录结构
- 只属于个人机器的业务凭证

### 推荐做法

1. 路径一律写成占位符，例如：`/path/to/hook`
2. 用户级路径优先写 `~/.codex/...`
3. 敏感配置放本机，不放仓库
4. Hook 脚本只做控制流判断，不直接保存任何密钥

## 常见问题

### 1）为什么文档里直接按 `~/.codex/hooks.json` 的 `Stop` 结构来写？

因为你当前本机已经验证在用的就是这套结构：

- 顶层文件：`~/.codex/hooks.json`
- 事件：`Stop`
- hook 类型：`command`
- 返回控制：`continue` / `decision=block`

所以这里不再另造一套抽象格式，直接贴着你现在真实运行态写，最稳。

### 2）为什么建议继续挂在 `Stop` 而不是更早的事件？

因为这个检查本质上是“收尾检查”，只有当代理准备结束当前请求时，才能判断它有没有真正输出最终结论。

### 3）为什么不用只提醒、不阻塞？

因为只提醒的约束力太弱，代理很容易顺口忽略。`block` 才能把“检查是否沉淀”从软提示变成硬门槛。


### 4）为什么把 prompt 单独拆文件？

因为后续最常变化的是规则文案，不是代码逻辑。拆文件后，团队只改 prompt 即可。
