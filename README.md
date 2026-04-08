# hook

> Codex / OpenCode / Claude Code 通用的技能沉淀与 Hook 工作流仓库。  
> 当前公开仓库：`https://github.com/kcd-dev/hook`

## 项目说明

这个仓库现在已经是**你们自己的自动化版本**，默认面向 **Codex** 使用，不再把历史上的第三方仓库地址当成主安装入口。

如果你之前在文档里看到过：

```text
https://github.com/blader/Claudeception.git
```

那是这个项目早期 README 沿袭下来的历史引用，不代表当前正式仓库入口。现在请统一以：

```text
https://github.com/kcd-dev/hook
```

为准。

## 快速开始

### 1）克隆当前仓库

**HTTPS**

```bash
git clone https://github.com/kcd-dev/hook.git
```

**SSH**

```bash
git clone git@github.com:kcd-dev/hook.git
```

## 中文文档入口

如果你主要想看中文说明，直接看这两个文件：

- `README.zh-CN.md`：中文总览与快速使用说明
- `docs/codex-hook-setup.md`：Codex Hook 详细配置文档

## Codex 版本（推荐）

当前仓库优先推荐 **Codex Stop Hook** 方案，用来在每次回复结束前做一次“技能沉淀自检”。

相关文件：

- `docs/codex-hook-setup.md`
- `scripts/codex-claudeception-stop-hook.py`
- `resources/skill-sedimentation-standard-prompt.md`

### Codex 版适合什么场景

- 想把“技能沉淀检查”设成 Codex 全局默认收尾动作
- 想强制要求代理输出统一的沉淀结论
- 想把 prompt 和 hook 脚本拆开管理，避免每次都改代码
- 想避免泄漏密钥、Cookie、Session 等本机敏感信息

### Codex 版核心能力

1. 在 `Stop` 事件触发时检查最后一条 assistant 回复
2. 如果没有出现 `技能沉淀结论：...`，则阻止结束
3. 重新注入“技能沉淀自检”提示，要求代理补完
4. 如果判断需要沉淀，必须先实际调用 `claudeception`

## 推荐知识沉淀提示词

你可以把下面这段提示词放进 Codex 的 prompt 文件或你自己的 hook 系统中：

```text
完成当前请求后，不要急着结束，先检查这次是否产生了可复用知识。

若有，先明确判断该落到哪一类：
①跨仓库通用方法、规则、判断框架 → skill
②当前仓库固定动作、命令、验收步骤 → 脚本 / workflow / 文档
③长期约束、默认行为、提示词边界 → prompt / AGENTS.md

以下情况默认优先判断需要沉淀：
- 出现了非直觉排障或试错后才定位到的根因
- 发现旧 skill / 旧提示词 / 旧文档已经过期，需要修补
- 形成了以后会复用的部署、验收、排查、发布、Hook、工作流步骤
- 发现了“以前以为是这样，其实真实运行态不是这样”的新事实

如果命中任一类型，并且需要做经验归纳、技能提炼、旧 skill 修补或知识回灌，必须明确调用 claudeception 来完成归纳或修补，而不是只在总结里顺口说一句“值得沉淀”。

若都不命中，明确写“不需要沉淀”，再结束。

你这次还没有给出明确的技能沉淀结论，先不要结束。
请在完成自检后，在本次回复末尾明确追加且只追加一行：
技能沉淀结论：不需要沉淀
或
技能沉淀结论：已调用 claudeception

如果需要沉淀，先实际调用 claudeception，再结束。
```

## Hook Runner 集成

如果你已经在用通用 Hook Runner（例如你们自己的 `kcd-dev/hook` 工作流），推荐把这段提示词挂到：

- `Stop`
- `final-response`
- `end-of-request`

这种**收尾阶段**，不要挂在最前面。

原因很简单：

- 这是一个“收尾检查”，不是前置检查
- 只有在模型准备结束时，才能判断它有没有真正输出最终结论
- 用 `block` 比纯提醒更可靠，能把软约束变成硬门槛

## Claude / 兼容入口（历史兼容）

仓库里仍保留了一部分面向 Claude 生态的历史说明和脚本，是为了兼容旧用法，不代表当前主推荐入口。

如果你只关心当前正式方案：

> **请优先使用 Codex 版本文档，不要再按旧的 `~/.claude/...` 安装说明作为主路径。**

## 安全说明

本仓库文档和脚本默认遵循以下边界：

- 不写入 API Key
- 不写入 Token
- 不写入 Cookie / Session
- 不写入生产密码
- 不把个人机器特有路径当成公开默认值
- 示例路径统一使用占位符或 `~/.codex/...`

## 详细文档

- 中文总览：`README.zh-CN.md`
- Codex Hook 配置：`docs/codex-hook-setup.md`
- 标准提示词：`resources/skill-sedimentation-standard-prompt.md`
- Stop Hook 脚本：`scripts/codex-claudeception-stop-hook.py`

## License

MIT
