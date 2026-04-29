#!/usr/bin/env python3
"""Generate .codex/agents/up-<n>.toml from plugins/up/agents/<n>.md.

Codex subagents are TOML files; Claude agents are YAML+markdown. The
'up-' prefix avoids collision with Codex built-ins like `explorer`.
"""
from pathlib import Path
import re, sys

ROOT = Path(__file__).resolve().parent.parent
SRC, DST = ROOT / "plugins/up/agents", ROOT / ".codex/agents"
DST.mkdir(parents=True, exist_ok=True)
esc = lambda s: s.replace("\\", "\\\\").replace('"', '\\"')

for src in sorted(SRC.glob("*.md")):
    m = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", src.read_text(), re.DOTALL)
    if not m:
        sys.exit(f"{src}: no frontmatter")
    fm = dict(re.findall(r"^(\w+):\s*(.*)$", m.group(1), re.M))
    body = m.group(2).strip()
    if "'''" in body:
        sys.exit(f"{src}: body contains ''', breaks TOML literal string")
    name = f"up-{fm.get('name', src.stem)}"
    out = [f'name = "{esc(name)}"',
           f'description = "{esc(fm.get("description", ""))}"']
    if "model" in fm:
        out.append(f'# model = "{fm["model"]}"  # was Claude model')
    out.append(f"developer_instructions = '''\n{body}\n'''")
    (DST / f"{name}.toml").write_text("\n".join(out) + "\n")
