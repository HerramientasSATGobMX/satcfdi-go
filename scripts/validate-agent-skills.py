#!/usr/bin/env python3
"""Validate the repo-local agent skill contract."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
SKILLS_DIR = ROOT / "skills"
BENCHMARK = ROOT / "testdata" / "agent-skills" / "benchmark.json"

REQUIRED_SECTIONS = [
    "## Propósito",
    "## Cuándo usarla",
    "## No usarla",
    "## Reglas duras",
    "## Workflow recomendado",
    "## Ejemplos correctos",
    "## Errores comunes",
    "## Fuentes de verdad",
    "## Verificación",
]

SKILL_LINK_RE = re.compile(r"\[[^\]]+\]\((skills/[^)#]+/SKILL\.md)\)")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def fail(message: str) -> None:
    print(f"ERROR: {message}")


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter start")

    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("missing YAML frontmatter end")

    frontmatter = text[4:end].splitlines()
    data: dict[str, str] = {}
    for line in frontmatter:
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line {line!r}")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def validate_markdown_links(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    for target in MARKDOWN_LINK_RE.findall(text):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        target = target.split("#", 1)[0]
        if not target:
            continue
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(ROOT)
        except ValueError:
            errors.append(f"{path.relative_to(ROOT)} links outside repo: {target}")
            continue
        if not resolved.exists():
            errors.append(f"{path.relative_to(ROOT)} links to missing path: {target}")
    return errors


def main() -> int:
    errors: list[str] = []

    if not AGENTS.exists():
        fail("AGENTS.md is missing")
        return 1
    if not SKILLS_DIR.exists():
        fail("skills/ directory is missing")
        return 1
    if not BENCHMARK.exists():
        fail("testdata/agent-skills/benchmark.json is missing")
        return 1

    agents_text = AGENTS.read_text(encoding="utf-8")
    errors.extend(validate_markdown_links(AGENTS, agents_text))

    router_skills = {
        Path(match).parts[1] for match in SKILL_LINK_RE.findall(agents_text)
    }
    disk_skills = {
        path.parent.name for path in sorted(SKILLS_DIR.glob("*/SKILL.md"))
    }

    if router_skills != disk_skills:
        missing_in_router = sorted(disk_skills - router_skills)
        missing_on_disk = sorted(router_skills - disk_skills)
        if missing_in_router:
            errors.append(
                f"AGENTS.md is missing skill links for: {', '.join(missing_in_router)}"
            )
        if missing_on_disk:
            errors.append(
                f"AGENTS.md references missing skills: {', '.join(missing_on_disk)}"
            )

    for skill_path in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        text = skill_path.read_text(encoding="utf-8")
        try:
            frontmatter = parse_frontmatter(skill_path)
        except ValueError as exc:
            errors.append(f"{skill_path.relative_to(ROOT)}: {exc}")
            continue

        skill_name = skill_path.parent.name
        if frontmatter.get("name") != skill_name:
            errors.append(
                f"{skill_path.relative_to(ROOT)} frontmatter name must be {skill_name!r}"
            )
        if not frontmatter.get("description"):
            errors.append(f"{skill_path.relative_to(ROOT)} missing description")

        for heading in REQUIRED_SECTIONS:
            if heading not in text:
                errors.append(
                    f"{skill_path.relative_to(ROOT)} missing required section {heading!r}"
                )

        errors.extend(validate_markdown_links(skill_path, text))

    try:
        benchmark = json.loads(BENCHMARK.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{BENCHMARK.relative_to(ROOT)} is not valid JSON: {exc}")
        benchmark = {}

    cases = benchmark.get("cases", [])
    if benchmark.get("version") != 1:
        errors.append("benchmark version must be 1")
    if not isinstance(cases, list) or len(cases) < 6:
        errors.append("benchmark must contain at least 6 cases")
        cases = []

    seen_skills: set[str] = set()
    seen_case_ids: set[str] = set()
    for index, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            errors.append(f"benchmark case #{index} must be an object")
            continue

        case_id = case.get("id", "")
        if not case_id:
            errors.append(f"benchmark case #{index} missing id")
        elif case_id in seen_case_ids:
            errors.append(f"duplicate benchmark case id {case_id!r}")
        else:
            seen_case_ids.add(case_id)

        if not case.get("prompt"):
            errors.append(f"benchmark case {case_id or index!r} missing prompt")

        expected_skills = case.get("expected_skills", [])
        if not isinstance(expected_skills, list) or not expected_skills:
            errors.append(f"benchmark case {case_id or index!r} missing expected_skills")
            expected_skills = []
        for skill in expected_skills:
            if skill not in disk_skills:
                errors.append(
                    f"benchmark case {case_id or index!r} references unknown skill {skill!r}"
                )
            else:
                seen_skills.add(skill)

        success_signals = case.get("success_signals", [])
        if not isinstance(success_signals, list) or not success_signals:
            errors.append(
                f"benchmark case {case_id or index!r} missing success_signals"
            )

        validation = case.get("validation", [])
        if not isinstance(validation, list) or not validation:
            errors.append(f"benchmark case {case_id or index!r} missing validation")

    unused_skills = sorted(disk_skills - seen_skills)
    if unused_skills:
        errors.append(
            f"benchmark does not exercise these skills: {', '.join(unused_skills)}"
        )

    if errors:
        for message in errors:
            fail(message)
        return 1

    print(
        f"Agent skills validation passed for {len(disk_skills)} skills and {len(cases)} benchmark cases."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
