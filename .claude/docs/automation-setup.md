# 自动化配置说明（2026-11-24 重建）

> 背景：本机 **Git Bash 与 WSL 均无法启动**（WSL 报 `WSL_E_ACCESS_DENIED`，Git Bash 报 `couldn't create signal pipe`）。
> 因此 `.claude/settings.json` 里所有 `bash .claude/hooks/*.sh` 都**从未真正执行过**，之前的「自动记忆 / 自动日志 / 提交校验」实际上全靠手动。

---

## 现在的两套配置

| 文件 | 面向 | 状态 |
|------|------|------|
| `.claude/settings.json` | Claude Code（旧） | 保留原样，但在本机不生效 |
| `.claude/settings.dsh.json` | DeepSeek Harness（新） | **当前生效的配置** |

DSH 使用 `settings.dsh.json`，只启用了 3 个 hook，全部是 PowerShell：

| 事件 | 脚本 | 作用 |
|------|------|------|
| `SessionStart` | `hooks/session-start.ps1` | 输出分支、最近提交、`active.md` 摘要、游戏项目未提交文件数 |
| `PreToolUse`（Bash/PowerShell） | `hooks/validate-git.ps1` | `git commit` 前查硬编码凭据 + Conventional Commits；`git push` 前拦 `--force` |
| `SessionEnd` | `hooks/session-end.ps1` | 归档 `active.md` 到 `session-log.md`（统一 UTF-8），记录本次提交与未提交文件 |

旧的 14 个 bash 脚本保留在 `hooks/` 下作为参考，不再执行。

> ⚠️ `settings.dsh.json` 不在 `.claude/docs/` 或 `.claude/hooks/` 下，**默认被 `.gitignore` 忽略**（`.claude/*` + 例外白名单）。
> 它只影响谁在跑 hook，不影响公司知识本身，因此**故意不入库**；换机器时需要重新创建（内容见上表）。

---

## 编码与换行约定

- `session-log.md` 的写入一律 UTF-8（`session-end.ps1` 已强制）。
- 历史日志（2026-06-26 ~ 06-30）在终端里显示过乱码，2026-11-24 已做字节级核验：文件本身无乱码、无替换字符（`0xEFBFBD`），是终端解码问题。
- 读取中文文件一律 `Get-Content -Encoding UTF8`，写入用 `[System.IO.File]::WriteAllText(path, text, New-Object System.Text.UTF8Encoding($false))`。
- `.gitattributes` 已为 `*.ps1` 指定 `text eol=crlf`：PowerShell 脚本必须是 CRLF + 无 BOM。

---

## 已知问题

1. **PowerShell 解析陷阱**：文件必须是 CRLF + 无 BOM。行内混用中英文字符串时，PS 5.1 解析器可能误判引号边界或把中文字符吃掉。
   写完 hook 后必须用 `[System.Management.Automation.Language.Parser]::ParseFile` 校验；
   报错时**先排除文件损坏**（对比 `Get-Content` 与原始写入内容），再看逻辑。
2. **游戏项目文本编码**：`新建游戏项目` 里的 `.gd` / `.json` / `.md` 均为 UTF-8 无 BOM。用 PowerShell 写这些文件时**不能**用 `Set-Content -Value`（会加 BOM 或按 GBK 写）。
3. **verify 脚本的编码假设**：`verify-phase8.ps1` 假定 `data/` 与 `scripts/data/` 下的 JSON 为 UTF-8 无 BOM、`scripts/` 为 UTF-8。若手工用记事本另存过，脚本会报「无 BOM」或乱码。

---

**维护者**：Claude（协调者）
**创建**：2026-11-24
