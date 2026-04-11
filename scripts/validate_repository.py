#!/usr/bin/env python3
"""Validate the core SciSkillUniverse repository invariants."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"

RESOURCE_STATUSES = {
    "discovered",
    "screened",
    "useful",
    "high_value",
    "duplicate",
    "rejected",
    "stale",
}

SKILL_STATUSES = {
    "idea",
    "draft",
    "implemented",
    "sandbox_verified",
    "slurm_verified",
    "partially_broken",
    "stale",
    "deprecated",
    "merged",
}


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(path)
    records: list[dict] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        records.append(json.loads(line))
    return records


def load_yaml_compatible_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_structure(errors: list[str]) -> None:
    required_paths = [
        ROOT / "registry",
        ROOT / "skills",
        ROOT / "tests" / "smoke",
        ROOT / "tests" / "regression",
        ROOT / "tests" / "integration",
        ROOT / "site",
        ROOT / "scripts",
    ]
    # Runtime directories that are gitignored — auto-create if missing.
    autocreate_paths = [
        ROOT / "tests" / "slurm",
        ROOT / "slurm" / "envs",
        ROOT / "slurm" / "jobs",
        ROOT / "slurm" / "logs",
        ROOT / "slurm" / "reports",
        ROOT / "scratch",
        ROOT / "reports",
    ]
    for path in required_paths:
        require(path.exists(), f"Missing required path: {path.relative_to(ROOT)}", errors)
    for path in autocreate_paths:
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"Created missing runtime directory: {path.relative_to(ROOT)}")


def validate_resources(errors: list[str]) -> dict[str, dict]:
    resources = load_jsonl(REGISTRY / "resources.jsonl")
    deduped = load_jsonl(REGISTRY / "resources_dedup.jsonl")
    resource_ids = set()

    for resource in resources:
        resource_id = resource["resource_id"]
        require(resource_id not in resource_ids, f"Duplicate resource_id in resources.jsonl: {resource_id}", errors)
        resource_ids.add(resource_id)
        require(resource["status"] in RESOURCE_STATUSES, f"Invalid resource status: {resource_id}", errors)
        require(isinstance(resource["topic_path"], list) and resource["topic_path"], f"Missing topic_path: {resource_id}", errors)
        require(resource["resource_type"] in {"package", "repo", "paper", "workflow", "notebook", "docs", "benchmark", "tutorial"}, f"Invalid resource_type: {resource_id}", errors)

    deduped_ids = set()
    for resource in deduped:
        resource_id = resource["resource_id"]
        require(resource_id not in deduped_ids, f"Duplicate resource_id in resources_dedup.jsonl: {resource_id}", errors)
        deduped_ids.add(resource_id)
        require(resource["status"] in RESOURCE_STATUSES, f"Invalid resource status: {resource_id}", errors)
        require(isinstance(resource["topic_path"], list) and resource["topic_path"], f"Missing topic_path: {resource_id}", errors)
        require(resource["resource_type"] in {"package", "repo", "paper", "workflow", "notebook", "docs", "benchmark", "tutorial"}, f"Invalid resource_type: {resource_id}", errors)

    return {resource["resource_id"]: resource for resource in deduped}


def validate_skills(resources: dict[str, dict], errors: list[str]) -> list[dict]:
    skills = load_jsonl(REGISTRY / "skills.jsonl")
    slugs = set()

    for skill in skills:
        slug = skill["slug"]
        path = ROOT / skill["path"]
        require(slug not in slugs, f"Duplicate skill slug: {slug}", errors)
        slugs.add(slug)
        require(skill["status"] in SKILL_STATUSES, f"Invalid skill status: {slug}", errors)
        require(path.exists(), f"Missing skill path: {skill['path']}", errors)
        for required_name in ["SKILL.md", "metadata.yaml", "refs.md", "scripts", "examples", "tests", "assets"]:
            require((path / required_name).exists(), f"{slug} missing {required_name}", errors)

        metadata = load_yaml_compatible_json(path / "metadata.yaml")
        require(metadata["slug"] == slug, f"{slug} metadata slug mismatch", errors)
        require(metadata["name"] == skill["name"], f"{slug} metadata name mismatch", errors)
        require(metadata["status"] == skill["status"], f"{slug} metadata status mismatch", errors)

        for resource_id in skill["source_resource_ids"]:
            require(resource_id in resources, f"{slug} references unknown resource_id {resource_id}", errors)

    return skills


def main() -> int:
    errors: list[str] = []
    validate_structure(errors)
    resources = validate_resources(errors)
    skills = validate_skills(resources, errors)

    if errors:
        for message in errors:
            print(f"ERROR: {message}", file=sys.stderr)
        return 1

    print(f"Repository validation passed: {len(resources)} resources, {len(skills)} skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
