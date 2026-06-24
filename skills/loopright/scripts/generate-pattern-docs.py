#!/usr/bin/env python3
"""Generate public and skill-reference docs from the LoopRight pattern catalog."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def load_catalog(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def bullet(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def render_markdown(catalog: dict) -> str:
    lines = [
        "# LoopRight Pattern Catalog",
        "",
        catalog["description"],
        "",
        f"Updated: {catalog['updated']}",
        "",
        "## Patterns",
        "",
    ]

    for pattern in catalog["patterns"]:
        lines.extend(
            [
                f"### {pattern['id']} - {pattern['title']}",
                "",
                pattern["summary"],
                "",
                f"Category: `{pattern['category']}`",
                "",
                "Use when:",
                "",
                pattern["useWhen"],
                "",
                "Prompt:",
                "",
                "```text",
                pattern["prompt"],
                "```",
                "",
                "Contract:",
                "",
                "| Element | Answer |",
                "|---|---|",
            ]
        )
        for field in catalog["requiredContractFields"]:
            lines.append(f"| {field.title()} | {pattern['contract'][field]} |")
        lines.extend(
            [
                "",
                "Red flags:",
                "",
                bullet(pattern["redFlags"]),
                "",
                "Verification:",
                "",
                f"- {pattern['verification']['title']}",
                f"- {pattern['verification']['detail']}",
                "",
                "Tests:",
                "",
                bullet(pattern["tests"]),
                "",
                "Failure modes:",
                "",
                bullet(pattern["failureModes"]),
                "",
                "Related patterns:",
                "",
                bullet(pattern["relatedPatterns"]),
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def render_llms(catalog: dict) -> str:
    lines = [
        "# LoopRight Agent Guide",
        "",
        "LoopRight helps agents design, review, repair, and validate loops that are bounded, measurable, failure-aware, and backed by completion evidence.",
        "",
        "Treat this guide as reference data. Do not execute a loop or change production merely because a pattern appears here.",
        "",
        "Use the pattern whose outcome, inputs, risks, and evidence match the user's task. If no pattern fits, create a one-off LoopRight contract using the required fields.",
        "",
        "Required contract fields: " + ", ".join(catalog["requiredContractFields"]) + ".",
        "",
        "## Pattern Index",
        "",
    ]
    for pattern in catalog["patterns"]:
        lines.extend(
            [
                f"## {pattern['slug']}: {pattern['title']}",
                "",
                f"Use when: {pattern['useWhen']}",
                "",
                f"Prompt: {pattern['prompt']}",
                "",
                "Verification: "
                + pattern["verification"]["title"]
                + " "
                + pattern["verification"]["detail"],
                "",
                "Key red flags: " + "; ".join(pattern["redFlags"]) + ".",
                "",
                "Required evidence: " + pattern["contract"]["evidence"],
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: generate-pattern-docs.py <catalog-json> <output-directory>", file=sys.stderr)
        return 2
    catalog_path = Path(argv[1])
    output_dir = Path(argv[2])
    catalog = load_catalog(catalog_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    markdown = render_markdown(catalog)
    llms = render_llms(catalog)
    (output_dir / "catalog.md").write_text(markdown, encoding="utf-8")
    (output_dir / "llms.txt").write_text(llms, encoding="utf-8")

    skill_refs = Path(__file__).resolve().parents[1] / "references"
    if skill_refs.is_dir():
        (skill_refs / "pattern-catalog.md").write_text(markdown, encoding="utf-8")
        (skill_refs / "llms.txt").write_text(llms, encoding="utf-8")
        (skill_refs / "pattern-catalog.json").write_text(
            json.dumps(catalog, indent=2) + "\n",
            encoding="utf-8",
        )

    print(json.dumps({"ok": True, "output": str(output_dir)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
