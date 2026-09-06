#!/usr/bin/env python3
"""Validate Ultrapack's Claude and Codex packaging without external dependencies."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SHARED_REFERENCES = {
    "commands/make.md": ("../skills/_brevity.md", "../skills/_principles.md"),
    "skills/make/SKILL.md": ("../_brevity.md", "../_principles.md"),
    "skills/udesign/SKILL.md": ("../_brevity.md", "../_principles.md"),
    "skills/uexecute/SKILL.md": ("../_brevity.md",),
    "skills/uplan/SKILL.md": ("../_brevity.md", "../_principles.md"),
    "skills/ureview/SKILL.md": ("../_brevity.md",),
    "skills/uverify/SKILL.md": ("../_brevity.md",),
}


def load_json(path: Path, errors: list[str]) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON ({error})")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path.relative_to(ROOT)}: expected a JSON object")
        return {}
    return value


def frontmatter(path: Path, errors: list[str]) -> dict[str, str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        errors.append(f"{path.relative_to(ROOT)}: unreadable ({error})")
        return {}
    if not lines or lines[0] != "---":
        errors.append(f"{path.relative_to(ROOT)}: missing YAML frontmatter")
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        errors.append(f"{path.relative_to(ROOT)}: unclosed YAML frontmatter")
        return {}
    fields: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line:
            errors.append(f"{path.relative_to(ROOT)}: malformed frontmatter line")
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def main() -> int:
    errors: list[str] = []
    claude_marketplace = load_json(ROOT / ".claude-plugin/marketplace.json", errors)
    codex_marketplace = load_json(ROOT / ".agents/plugins/marketplace.json", errors)
    claude_plugin = load_json(ROOT / ".claude-plugin/plugin.json", errors)
    codex_plugin = load_json(ROOT / ".codex-plugin/plugin.json", errors)
    pi_package = load_json(ROOT / "package.json", errors)
    pi_lock = load_json(ROOT / "package-lock.json", errors)

    if claude_marketplace.get("plugins") != [{
        "name": "up",
        "description": "ultrapack — lean, opinionated skill pack for spec-driven, git-centered development",
        "source": ".",
    }]:
        errors.append(".claude-plugin/marketplace.json: expected the up plugin at the repository root")

    entries = codex_marketplace.get("plugins")
    if not isinstance(entries, list) or len(entries) != 1:
        errors.append(".agents/plugins/marketplace.json: expected exactly one plugin entry")
    else:
        entry = entries[0]
        if not isinstance(entry, dict) or entry.get("name") != "up":
            errors.append(".agents/plugins/marketplace.json: expected the up plugin entry")
        elif entry.get("source") != {"source": "url", "url": "./"}:
            errors.append(".agents/plugins/marketplace.json: expected Git URL source ./")
        elif entry.get("policy") != {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}:
            errors.append(".agents/plugins/marketplace.json: expected install and authentication policy")
        elif entry.get("category") != "Developer Tools":
            errors.append(".agents/plugins/marketplace.json: expected Developer Tools category")

    lock_root = pi_lock.get("packages", {}).get("", {})
    versions = [
        claude_plugin.get("version"),
        codex_plugin.get("version"),
        pi_package.get("version"),
        pi_lock.get("version"),
        lock_root.get("version"),
    ]
    if len(set(versions)) != 1 or not isinstance(versions[0], str) or not SEMVER.fullmatch(versions[0]):
        errors.append("plugin manifests: expected matching strict-semver versions")
    if claude_plugin.get("name") != "up" or codex_plugin.get("name") != "up":
        errors.append("plugin manifests: expected name up")
    if codex_plugin.get("skills") != "./skills/":
        errors.append("Codex manifest: expected skills path ./skills/")
    if pi_package.get("keywords") != ["pi-package"]:
        errors.append("Pi package: expected pi-package keyword")
    if pi_package.get("pi") != {"skills": ["./skills"], "prompts": ["./commands"]}:
        errors.append("Pi package: expected shared skills and command prompts")
    interface = codex_plugin.get("interface")
    required_interface = {"displayName", "shortDescription", "longDescription", "developerName", "category", "capabilities", "defaultPrompt"}
    if not isinstance(interface, dict) or not required_interface.issubset(interface):
        errors.append("Codex manifest: missing required interface metadata")

    for relative_path, references in SHARED_REFERENCES.items():
        path = ROOT / relative_path
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as error:
            errors.append(f"{relative_path}: unreadable ({error})")
            continue
        for reference in references:
            if reference not in text:
                errors.append(f"{relative_path}: missing shared reference {reference}")
            elif not (path.parent / reference).is_file():
                errors.append(f"{relative_path}: broken shared reference {reference}")

    for skill_dir in sorted((ROOT / "skills").iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith("_") or skill_dir.name.startswith("."):
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            errors.append(f"skills/{skill_dir.name}: missing SKILL.md")
            continue
        fields = frontmatter(skill_file, errors)
        name, description = fields.get("name"), fields.get("description")
        if name != skill_dir.name or not name or not SKILL_NAME.fullmatch(name):
            errors.append(f"{skill_file.relative_to(ROOT)}: name must equal its hyphen-case directory")
        if not description:
            errors.append(f"{skill_file.relative_to(ROOT)}: missing description")

    if errors:
        print("Ultrapack validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("Ultrapack packaging validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
