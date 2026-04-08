# hook 中文说明

测试日期：2026-04-08
文档版本：v1.0.0

## 这是什么

这是一个面向 **Codex 优先** 的 Hook / Prompt / 技能沉淀工作流仓库。

它解决的问题是：

- 模型做完任务后直接结束，没有检查这轮是否值得沉淀
- 明明应该沉淀成 skill / workflow / prompt，却只是口头说一句“值得沉淀”
- 团队想统一一个收尾标准，但缺少可执行、可机读、可阻塞的 Hook 方案

## 当前正式仓库

当前请统一使用：

```text
https://github.com/kcd-dev/hook
```

历史文档里出现过的 `blader/Claudeception` 只是旧引用，不再是当前正式入口。

## 仓库里最重要的 3 个文件

### 1. `docs/codex-hook-setup.md`

这是 **Codex 版详细配置文档**，讲清楚：

- 如何配置 `~/.codex/hooks.json`
- 如何把 Stop Hook 接到 Codex
- 如何验证 Hook 是否真的生效
- 如何避免在仓库里泄漏敏感信息

### 2. `scripts/codex-claudeception-stop-hook.py`

这是 **Codex Stop Hook 脚本**。

它负责：

- 读取 Stop 事件输入
- 检查最后一条 assistant 回复
- 判断是否已经包含 `技能沉淀结论：...`
- 如果没有，就返回 `block`，强制模型补做沉淀自检

### 3. `resources/skill-sedimentation-standard-prompt.md`

这是**标准沉淀提示词**。

推荐把它复制到：

```text
~/.codex/prompts/skill-sedimentation-standard-prompt.md
```

这样后续你改规则时，只改 prompt 文件，不改 Python 脚本。

## 推荐用法

### 最短路径

1. clone 当前仓库
2. 按你当前 `~/.codex/hooks.json` 的真实格式，把 Stop Hook 脚本接进去
3. 把标准提示词复制到 `~/.codex/prompts/`
4. 让 Codex 在每次回复结束前执行收尾检查

## 设计原则

### 1）收尾阶段触发，不前置触发

这个 Hook 应该挂在：

- `Stop`
- `final-response`
- `end-of-request`

而不是开头。

因为它本质是“本轮结束前的检查”。

### 2）阻塞优先，不做软提醒

单纯提醒太容易被忽略。

所以这里采用：

- 没有明确结论 → `block`
- 有明确结论 → `continue`

### 3）Prompt 与脚本分离

最容易频繁变化的是文案规则，不是代码。

因此：

- Prompt 放 markdown
- Hook 用稳定脚本读取 prompt
- 团队以后只改 prompt 文件即可

### 4）不泄漏机密

仓库内文档和脚本都不应包含：

- API Key
- Token
- Cookie
- Session
- 生产密码
- 本地私有业务路径

## 适合谁用

- 想把技能沉淀流程标准化的团队
- 想把 prompt / hook / workflow 一起版本化管理的人
- 想给 Codex 加一层“结束前必须复盘”的硬约束的人

## 下一步看哪里

如果你要实际接到 Codex：

> 直接看 `docs/codex-hook-setup.md`


## 配置来源说明

本文档里的 Codex 配置示例，不是重新发明的一套格式，而是按你当前本机 `~/.codex/hooks.json` 的真实结构整理出来的通用化版本：保留 `Stop` / `matcher` / `hooks` / `type=command` / `timeout` / `statusMessage` 这些字段，只把具体机器路径改成不含机密的占位符。
