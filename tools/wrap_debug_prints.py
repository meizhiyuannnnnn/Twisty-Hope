#!/usr/bin/env python3
"""把 GDScript 中的裸 print(...) 包进 if OS.is_debug_build() 守卫。

用法:
    python tools/wrap_debug_prints.py <项目根目录> [--dry-run]

规则:
- 只处理整行形如 `\\t*print(` 的多行语句（行为以 `))` 或 `])` 结尾）
- 已经处于 debug 守卫内的语句跳过
- 遇到换行但括号未闭合的情况继续累积，直到括号平衡
- 保持原有制表符缩进，守卫行用相同缩进，语句整体缩进一级（一个制表符）

说明: 只处理单行调用写法的上下文之外的多行语句；单行 `print("...")` 也一并处理。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PRINT_RE = re.compile(r"^(\t*)print\(")
GUARD = "OS.is_debug_build()"


def balanced(text: str) -> bool:
    """粗略判断括号是否闭合（GDScript 字符串里不含未转义括号的情形满足本项目）。"""
    depth = 0
    in_str = False
    quote = ""
    i = 0
    while i < len(text):
        ch = text[i]
        if in_str:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                in_str = False
        else:
            if ch in ('"', "'"):
                in_str = True
                quote = ch
            elif ch in "([":
                depth += 1
            elif ch in ")]":
                depth -= 1
        i += 1
    return depth <= 0


def process(path: Path, dry_run: bool) -> bool:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    out: list[str] = []
    i = 0
    changed = 0
    while i < len(lines):
        line = lines[i]
        guard_line = line[:-1] + "\n" if line.strip() == f"if {GUARD}:" else None

        # 情况 A: 已存在守卫行，但语句缩进过深（修复上一版脚本的双缩进）
        if guard_line and i + 1 < len(lines):
            nxt = lines[i + 1]
            if nxt.startswith("\t") and not nxt.startswith("\t\t") and nxt.lstrip().startswith("print("):
                pass
            elif nxt.startswith("\t\t") and nxt.lstrip().startswith("print("):
                stmt_lines = [nxt]
                j = i + 1
                while not balanced("".join(stmt_lines)) and j + 1 < len(lines):
                    j += 1
                    stmt_lines.append(lines[j])
                stmt_lines = [s[1:] if s.startswith("\t") else s for s in stmt_lines]
                out.append(guard_line)
                out.extend(stmt_lines)
                changed += len(stmt_lines)
                i = j + 1
                continue

        m = PRINT_RE.match(line)
        if not m:
            out.append(line)
            i += 1
            continue

        # 收集完整语句（可能跨行）
        stmt_lines = [line]
        j = i
        while not balanced("".join(stmt_lines)) and j + 1 < len(lines):
            j += 1
            stmt_lines.append(lines[j])

        indent = m.group(1)
        guard_line = f"{indent}if {GUARD}:\n"
        body = [indent + "\t" + s for s in stmt_lines]
        # 保证最后一行有换行
        if not body[-1].endswith("\n"):
            body[-1] = body[-1] + "\n"
        # 语句本身不带尾随空白/多余换行（多行语句拼接时可能带上）
        body[-1] = body[-1].rstrip("\n") + "\n"

        already = bool(out) and out[-1].strip() == f"if {GUARD}:"
        if already:
            out.extend(stmt_lines)
        else:
            out.append(guard_line)
            out.extend(body)
            changed += len(stmt_lines)

        i = j + 1

    if changed and not dry_run:
        path.write_text("".join(out), encoding="utf-8", newline="")
    return bool(changed)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    root = Path(sys.argv[1])
    dry_run = "--dry-run" in sys.argv
    files = sorted(root.rglob("*.gd"))
    touched = 0
    for f in files:
        if process(f, dry_run):
            touched += 1
            print(f"{'[dry] ' if dry_run else ''}wrapped: {f.relative_to(root)}")
    print(f"done: {touched} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
