from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from skillfoundry.campaign import FrameworkCampaignRunner
from skillfoundry.codex_exec import CodexExecRunner
from skillfoundry import SkillAutomationFramework


ROOT = Path(__file__).resolve().parents[2]


def write_fake_codex(path: Path) -> None:
    script = "\n".join(
        [
            "#!/usr/bin/env python3",
            "from __future__ import annotations",
            "",
            "import json",
            "import re",
            "import sys",
            "import time",
            "from pathlib import Path",
            "",
            "",
            "def value_after(flag: str) -> str | None:",
            "    if flag not in sys.argv:",
            "        return None",
            "    index = sys.argv.index(flag)",
            "    if index + 1 >= len(sys.argv):",
            "        return None",
            "    return sys.argv[index + 1]",
            "",
            "",
            "def values_after(flag: str) -> list[str]:",
            "    values = []",
            "    for index, value in enumerate(sys.argv[:-1]):",
            "        if value == flag:",
            "            values.append(sys.argv[index + 1])",
            "    return values",
            "",
            "",
            "def extract_field(prompt: str, field: str) -> str:",
            "    prefix = f\"{field}:\"",
            "    for line in prompt.splitlines():",
            "        if line.startswith(prefix):",
            "            return line.split(\":\", 1)[1].strip()",
            "    return \"unknown\"",
            "",
            "",
            "def extract_skill_slug(prompt: str) -> str:",
            "    for line in prompt.splitlines():",
            "        stripped = line.strip()",
            "        if stripped.startswith('\"slug\":'):",
            "            return stripped.split(\":\", 1)[1].strip().strip('\",')",
            "        if stripped.startswith('\"skill_slug\":'):",
            "            return stripped.split(\":\", 1)[1].strip().strip('\",')",
            "    return \"unknown-skill\"",
            "",
            "",
            "def extract_topic_slug(prompt: str) -> str:",
            "    found = []",
            "    for line in prompt.splitlines():",
            "        stripped = line.strip()",
            "        if stripped.startswith('\"topic_slug\":'):",
            "            found.append(stripped.split(\":\", 1)[1].strip().strip('\",'))",
            "    return found[-1] if found else \"unknown-topic\"",
            "",
            "",
            "def safe_dash(value: str) -> str:",
            "    value = re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')",
            "    return value or 'unknown-topic'",
            "",
            "",
            "def safe_snake(value: str) -> str:",
            "    value = re.sub(r'[^a-z0-9]+', '_', value.lower()).strip('_')",
            "    return value or 'unknown_topic'",
            "",
            "",
            "def main() -> int:",
            "    if len(sys.argv) < 2 or sys.argv[1] != \"exec\":",
            "        print(\"fake codex only supports `exec`\", file=sys.stderr)",
            "        return 2",
            "    prompt = sys.stdin.read()",
            "    stage = extract_field(prompt, \"STAGE\")",
            "    skill_slug = extract_skill_slug(prompt)",
            "    topic_slug = extract_topic_slug(prompt)",
            "    topic_dash = safe_dash(topic_slug)",
            "    topic_snake = safe_snake(topic_slug)",
            "    repo_root = Path.cwd()",
            "    model = value_after('-m')",
            "    config_values = values_after('-c')",
            "    log_path = __import__('os').environ.get('FAKE_CODEX_LOG_PATH')",
            "    if log_path:",
            "        with Path(log_path).open('a', encoding='utf-8') as handle:",
            "            handle.write(json.dumps({'stage': stage, 'skill_slug': skill_slug, 'topic_slug': topic_slug, 'model': model, 'configs': config_values}) + '\\n')",
            "    sleep_seconds = float(Path.cwd().joinpath('.').expanduser() and 0)",
            "    try:",
            "        sleep_seconds = float(__import__('os').environ.get('FAKE_CODEX_SLEEP_SECONDS', '0'))",
            "    except ValueError:",
            "        sleep_seconds = 0.0",
            "    if sleep_seconds > 0:",
            "        time.sleep(sleep_seconds)",
            "    if stage == \"layer1_fix\":",
            "        (repo_root / \".fake-layer1-fixed\").write_text(\"fixed\\n\", encoding=\"utf-8\")",
            "        payload = {",
            "            \"stage\": stage,",
            "            \"skill_slug\": skill_slug,",
            "            \"summary\": \"applied targeted correctness fix\",",
            "            \"debug_findings\": [\"initial smoke target failed\"],",
            "            \"fixes_applied\": [\"repaired layer1 smoke path\"],",
            "            \"tests_run\": [\"make smoke-openalex\"],",
            "            \"repo_changes\": [\"skills/scientific-knowledge/openalex-literature-search/scripts/search_openalex.py\"],",
            "            \"blockers\": [],",
            "            \"next_steps\": [\"rerun correctness check\"],",
            "        }",
            "    elif stage == \"layer2_benchmark\":",
            "        optimized = (repo_root / \".fake-layer2-optimized\").exists()",
            "        payload = {",
            "            \"stage\": stage,",
            "            \"skill_slug\": skill_slug,",
            "            \"summary\": \"ran skill-vs-baseline benchmark\",",
            "            \"benchmark_cases\": [\"canonical-task\", \"edge-case\"],",
            "            \"with_skill_score\": 0.95 if optimized else 0.55,",
            "            \"without_skill_score\": 0.4,",
            "            \"advantage_score\": 0.55 if optimized else 0.15,",
            "            \"meets_expectation\": optimized,",
            "            \"optimization_targets\": [] if optimized else [\"improve output contract\", \"tighten examples\"],",
            "            \"tests_run\": [\"skill-benchmark-case-1\", \"skill-benchmark-case-2\"],",
            "            \"repo_changes\": [],",
            "            \"blockers\": [] if optimized else [\"skill path not clearly better than baseline yet\"],",
            "            \"next_steps\": [\"retain benchmark artifact\"] if optimized else [\"optimize the skill and rerun benchmark\"],",
            "        }",
            "    elif stage == \"layer2_optimize\":",
            "        (repo_root / \".fake-layer2-optimized\").write_text(\"optimized\\n\", encoding=\"utf-8\")",
            "        payload = {",
            "            \"stage\": stage,",
            "            \"skill_slug\": skill_slug,",
            "            \"summary\": \"optimized the skill for benchmark advantage\",",
            "            \"optimization_findings\": [\"baseline was too close on deliverable completeness\"],",
            "            \"optimizations_applied\": [\"improved benchmark-facing contract\"],",
            "            \"tests_run\": [\"make smoke-openalex\"],",
            "            \"repo_changes\": [\"skills/scientific-knowledge/openalex-literature-search/SKILL.md\"],",
            "            \"blockers\": [],",
            "            \"next_steps\": [\"rerun benchmark\"],",
            "        }",
            "    elif stage == \"novelty_check\":",
            "        payload = {",
            "            \"stage\": stage,",
            "            \"skill_slug\": skill_slug,",
            "            \"summary\": \"checked overlap against local registry and ToolUniverse\",",
            "            \"novelty_score\": 3.7,",
            "            \"local_overlap_slugs\": [\"europepmc-method-triage\"],",
            "            \"external_overlap_titles\": [\"ToolUniverse literature search capabilities\"],",
            "            \"web_sources\": [\"https://github.com/mims-harvard/ToolUniverse\"],",
            "            \"needs_merge_review\": False,",
            "            \"blockers\": [],",
            "            \"next_steps\": [\"keep the skill separate but monitor overlap\"],",
            "        }",
            "    elif \"MODE: parallel_leaf_stage\" in prompt:",
            "        skill_dir = repo_root / 'skills' / 'parallel-test' / topic_dash",
            "        skill_dir.mkdir(parents=True, exist_ok=True)",
            "        (skill_dir / 'SKILL.md').write_text(f'# {topic_dash}\\n\\n{stage}\\n', encoding='utf-8')",
            "        test_dir = repo_root / 'tests' / 'smoke'",
            "        test_dir.mkdir(parents=True, exist_ok=True)",
            "        (test_dir / f'test_{topic_snake}.py').write_text('def test_placeholder():\\n    assert True\\n', encoding='utf-8')",
            "        payload = {",
            "            \"stage\": stage,",
            "            \"summary\": f\"parallel worker handled {topic_slug}\",",
            "            \"selected_topics\": [topic_slug],",
            "            \"skills_touched\": [f\"{topic_dash}-starter\"],",
            "            \"resources_touched\": [f\"{topic_slug}-resource\"],",
            "            \"tests_run\": [f\"test_{topic_snake}\"],",
            "            \"slurm_jobs\": [],",
            "            \"repo_changes\": [f\"skills/parallel-test/{topic_dash}/SKILL.md\", f\"tests/smoke/test_{topic_snake}.py\"],",
            "            \"blockers\": [],",
            "            \"next_steps\": [\"run refresh\"],",
            "        }",
            "    else:",
            "        payload = {",
            "            \"stage\": stage,",
            "            \"summary\": f\"fake handled {stage}\",",
            "            \"selected_topics\": [stage],",
            "            \"skills_touched\": [\"example-skill\"] if stage in {\"skill_build\", \"skill_test\", \"design_skill\"} else [],",
            "            \"resources_touched\": [\"example-resource\"] if stage in {\"resource_search\", \"design_skill\"} else [],",
            "            \"tests_run\": [\"make validate\"] if stage in {\"skill_test\", \"design_skill\"} else [],",
            "            \"slurm_jobs\": [],",
            "            \"repo_changes\": [],",
            "            \"blockers\": [],",
            "            \"next_steps\": [\"continue\"],",
            "        }",
            "    output_path = value_after(\"-o\") or value_after(\"--output-last-message\")",
            "    if output_path is not None:",
            "        Path(output_path).write_text(json.dumps(payload), encoding=\"utf-8\")",
            "    print(json.dumps({\"stage\": stage, \"ok\": True}))",
            "    return 0",
            "",
            "",
            "if __name__ == \"__main__\":",
            "    raise SystemExit(main())",
        ]
    ) + "\n"
    path.write_text(script, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)


def write_fake_make(path: Path) -> None:
    script = "\n".join(
        [
            "#!/usr/bin/env python3",
            "from __future__ import annotations",
            "",
            "import sys",
            "from pathlib import Path",
            "",
            "",
            "def main() -> int:",
            "    target = sys.argv[1] if len(sys.argv) > 1 else \"\"",
            "    repo_root = Path.cwd()",
            "    if target == \"smoke-openalex\":",
            "        if (repo_root / \".fake-layer1-fixed\").exists():",
            "            print(\"smoke-openalex passed after repair\")",
            "            return 0",
            "        print(\"simulated openalex smoke failure\", file=sys.stderr)",
            "        return 1",
            "    if target.startswith(\"smoke-\"):",
            "        print(f\"{target} passed\")",
            "        return 0",
            "    print(f\"unsupported fake make target: {target}\", file=sys.stderr)",
            "    return 2",
            "",
            "",
            "if __name__ == \"__main__\":",
            "    raise SystemExit(main())",
        ]
    ) + "\n"
    path.write_text(script, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)


def write_flaky_fake_codex(path: Path) -> None:
    script = "\n".join(
        [
            "#!/usr/bin/env python3",
            "from __future__ import annotations",
            "",
            "import json",
            "import os",
            "import sys",
            "from pathlib import Path",
            "",
            "",
            "def value_after(flag: str) -> str | None:",
            "    if flag not in sys.argv:",
            "        return None",
            "    index = sys.argv.index(flag)",
            "    if index + 1 >= len(sys.argv):",
            "        return None",
            "    return sys.argv[index + 1]",
            "",
            "",
            "def main() -> int:",
            "    output_path = value_after('-o') or value_after('--output-last-message')",
            "    state_path = Path(os.environ['FAKE_CODEX_RETRY_STATE'])",
            "    attempts = 0",
            "    if state_path.exists():",
            "        attempts = int(state_path.read_text(encoding='utf-8').strip() or '0')",
            "    attempts += 1",
            "    state_path.write_text(str(attempts), encoding='utf-8')",
            "    if attempts == 1:",
            "        print('ERROR: stream disconnected before completion: error sending request for url (https://chatgpt.com/backend-api/codex/responses)', file=sys.stderr)",
            "        print('failed to queue rollout items: channel closed', file=sys.stderr)",
            "        return 0",
            "    payload = {",
            "        'stage': 'design_skill',",
            "        'summary': 'retry succeeded',",
            "        'skills_touched': ['annotation'],",
            "        'resources_touched': ['cellxgene-census'],",
            "        'tests_run': ['make validate'],",
            "        'slurm_jobs': [],",
            "        'repo_changes': ['experiments/sc_skills/annotation/SKILL.md'],",
            "        'blockers': [],",
            "        'next_steps': ['validate outputs'],",
            "    }",
            "    if output_path:",
            "        Path(output_path).write_text(json.dumps(payload), encoding='utf-8')",
            "    print(json.dumps(payload))",
            "    return 0",
            "",
            "",
            "if __name__ == '__main__':",
            "    raise SystemExit(main())",
        ]
    ) + "\n"
    path.write_text(script, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)


class SkillAutomationFrameworkIntegrationTest(unittest.TestCase):
    def setUp(self) -> None:
        for marker in [".fake-layer1-fixed", ".fake-layer2-optimized"]:
            (ROOT / marker).unlink(missing_ok=True)

    def tearDown(self) -> None:
        for marker in [".fake-layer1-fixed", ".fake-layer2-optimized"]:
            (ROOT / marker).unlink(missing_ok=True)

    def copy_repo(self, tmpdir: Path) -> Path:
        repo_copy = tmpdir / "repo"

        def ignore(dirpath: str, names: list[str]) -> set[str]:
            ignored = {name for name in names if name == "__pycache__" or name.endswith(".pyc")}
            relative = Path(dirpath).resolve().relative_to(ROOT)
            if relative == Path("."):
                ignored.update({name for name in names if name in {".git", "scratch", "reports", "output", ".nextflow", ".nextflow.log", ".nextflow.log.1"}})
            if relative == Path("slurm"):
                ignored.update({name for name in names if name in {"envs", "logs"}})
            return ignored

        shutil.copytree(ROOT, repo_copy, ignore=ignore)
        for required in [
            repo_copy / "scratch",
            repo_copy / "reports",
            repo_copy / "slurm" / "envs",
            repo_copy / "slurm" / "logs",
        ]:
            required.mkdir(parents=True, exist_ok=True)
        return repo_copy

    def make_framework(self, tmpdir: Path) -> tuple[SkillAutomationFramework, Path]:
        fake_codex = tmpdir / "fake_codex.py"
        write_fake_codex(fake_codex)
        repo_copy = self.copy_repo(tmpdir)
        framework = SkillAutomationFramework(
            repo_copy,
            codex_bin=str(fake_codex),
            state_dir=tmpdir / "state",
            reports_dir=tmpdir / "reports",
            stage_timeout=60,
            verification_timeout=300,
        )
        return framework, repo_copy

    def test_status_returns_current_repository_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            framework, _ = self.make_framework(Path(tmpdir))
            payload = framework.status(focus_limit=5)
            self.assertGreater(payload["summary"]["resource_count"], 0)
            self.assertGreater(payload["summary"]["skill_count"], 0)
            self.assertEqual(len(payload["focus_leaves"]), 5)

    def test_status_can_filter_focus_terms(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            framework, _ = self.make_framework(Path(tmpdir))
            payload = framework.status(focus_limit=6, focus_terms=["single cell"])
            self.assertGreater(len(payload["focus_leaves"]), 0)
            for leaf in payload["focus_leaves"]:
                joined = " ".join(
                    [
                        leaf["domain_slug"],
                        leaf["domain_name"],
                        leaf["leaf_name"],
                        leaf["topic_slug"],
                    ]
                ).lower()
                self.assertIn("single", joined)

    def test_codex_exec_runner_retries_transient_disconnects(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            flaky_codex = tmp / "flaky_codex.py"
            state_path = tmp / "retry_state.txt"
            artifact_dir = tmp / "artifacts"
            write_flaky_fake_codex(flaky_codex)
            runner = CodexExecRunner(
                codex_bin=str(flaky_codex),
                model="gpt-5.4",
                reasoning_effort="xhigh",
            )
            with patch.dict(os.environ, {"FAKE_CODEX_RETRY_STATE": str(state_path)}, clear=False):
                result = runner.run(
                    prompt="STAGE: design_skill\nSummarize a retryable task.\n",
                    output_schema={},
                    working_dir=ROOT,
                    artifact_dir=artifact_dir,
                    timeout=60,
                    max_retries=2,
                )
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.parsed_message["stage"], "design_skill")
            attempts = json.loads((artifact_dir / "attempts.json").read_text(encoding="utf-8"))["attempts"]
            self.assertEqual(len(attempts), 2)
            self.assertTrue(attempts[0]["retryable_disconnect"])
            self.assertFalse(attempts[1]["retryable_disconnect"])

    def test_cycle_records_stage_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            framework, _ = self.make_framework(tmp)
            payload = framework.run_cycle(
                loops=1,
                stages=["tree_check", "resource_search"],
                focus_limit=3,
                verification_mode="none",
                run_label="framework-test",
            )
            manifest_path = Path(payload["run_dir"]) / "manifest.json"
            self.assertTrue(manifest_path.exists())
            self.assertEqual(len(payload["stage_results"]), 2)
            first_stage_dir = Path(payload["run_dir"]) / "stages" / "01-tree_check"
            self.assertTrue((first_stage_dir / "prompt.md").exists())
            self.assertTrue((first_stage_dir / "schema.json").exists())
            self.assertTrue((first_stage_dir / "result.json").exists())
            latest_run = tmp / "state" / "latest_run.json"
            self.assertTrue(latest_run.exists())

    def test_design_skill_can_run_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            framework, _ = self.make_framework(Path(tmpdir))
            payload = framework.design_skill(
                task_prompt="Design a skill for ranking pathway-enrichment papers.",
                focus_limit=2,
                verification_mode="validate",
                run_label="design-validation-test",
            )
            self.assertEqual(payload["stage_result"]["codex"]["parsed_message"]["stage"], "design_skill")
            self.assertEqual(len(payload["verification"]), 1)
            self.assertEqual(payload["verification"][0]["label"], "validate")
            self.assertEqual(payload["verification"][0]["returncode"], 0)

    def test_stage_model_routing_uses_expected_models_and_efforts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            log_path = tmp / "codex-log.jsonl"
            fake_make = tmp / "make"
            write_fake_make(fake_make)
            framework, _ = self.make_framework(tmp)
            env = {"PATH": f"{tmp}:{os.environ['PATH']}", "FAKE_CODEX_LOG_PATH": str(log_path)}
            with patch.dict(os.environ, env, clear=False):
                cycle_payload = framework.run_cycle(
                    loops=1,
                    stages=["tree_check", "resource_search", "skill_build", "skill_test", "refresh"],
                    focus_limit=1,
                    verification_mode="none",
                    run_label="routing-cycle-test",
                )
                design_payload = framework.design_skill(
                    task_prompt="Design a skill for pathway triage.",
                    focus_limit=1,
                    verification_mode="none",
                    run_label="routing-design-test",
                )
                eval_payload = framework.evaluate_skills(
                    skill_slugs=["openalex-literature-search"],
                    verification_mode="none",
                    layer1_fix_attempts=1,
                    layer2_optimize_attempts=1,
                )
            cycle_commands = {
                record["stage"]: record["codex"]["command"]
                for record in cycle_payload["stage_results"]
            }
            self.assertIn('-m', cycle_commands["tree_check"])
            self.assertIn('gpt-5.4', cycle_commands["tree_check"])
            self.assertIn('model_reasoning_effort="medium"', cycle_commands["tree_check"])
            self.assertIn('gpt-5.4', cycle_commands["resource_search"])
            self.assertIn('model_reasoning_effort="high"', cycle_commands["resource_search"])
            self.assertIn('gpt-5.4', cycle_commands["skill_build"])
            self.assertIn('model_reasoning_effort="medium"', cycle_commands["skill_build"])
            self.assertIn('gpt-5.4-mini', cycle_commands["skill_test"])
            self.assertIn('model_reasoning_effort="medium"', cycle_commands["skill_test"])
            self.assertIn('gpt-5.4', cycle_commands["refresh"])
            self.assertIn('model_reasoning_effort="medium"', cycle_commands["refresh"])
            self.assertIn('gpt-5.4', design_payload["stage_result"]["codex"]["command"])
            self.assertIn('model_reasoning_effort="medium"', design_payload["stage_result"]["codex"]["command"])
            self.assertIn('gpt-5.4-mini', eval_payload["layer1"][0]["fix_attempts"][0]["fix"]["command"])
            self.assertIn('model_reasoning_effort="medium"', eval_payload["layer1"][0]["fix_attempts"][0]["fix"]["command"])
            self.assertIn('gpt-5.4-mini', eval_payload["layer2"][0]["final_benchmark"]["command"])
            self.assertIn('gpt-5.4-mini', eval_payload["novelty"][0]["novelty"]["command"])

    def test_explicit_global_codex_options_override_stage_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            log_path = tmp / "codex-log.jsonl"
            fake_make = tmp / "make"
            write_fake_make(fake_make)
            fake_codex = tmp / "fake_codex.py"
            write_fake_codex(fake_codex)
            repo_copy = self.copy_repo(tmp)
            framework = SkillAutomationFramework(
                repo_copy,
                codex_bin=str(fake_codex),
                state_dir=tmp / "state",
                reports_dir=tmp / "reports",
                model="gpt-5.4",
                reasoning_effort="xhigh",
                stage_timeout=60,
                verification_timeout=300,
            )
            env = {"PATH": f"{tmp}:{os.environ['PATH']}", "FAKE_CODEX_LOG_PATH": str(log_path)}
            with patch.dict(os.environ, env, clear=False):
                framework.run_cycle(
                    loops=1,
                    stages=["tree_check", "resource_search", "skill_build", "skill_test", "refresh"],
                    focus_limit=1,
                    verification_mode="none",
                    run_label="override-cycle-test",
                )
                framework.design_skill(
                    task_prompt="Design a skill for pathway triage.",
                    focus_limit=1,
                    verification_mode="none",
                    run_label="override-design-test",
                )
                framework.evaluate_skills(
                    skill_slugs=["openalex-literature-search"],
                    verification_mode="none",
                    layer1_fix_attempts=1,
                    layer2_optimize_attempts=1,
                )
            entries = [
                json.loads(line)
                for line in log_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertGreater(len(entries), 0)
            for entry in entries:
                self.assertEqual(entry["model"], "gpt-5.4")
                self.assertIn('model_reasoning_effort="xhigh"', entry["configs"])

    def test_codex_config_overrides_are_forwarded_to_exec(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            log_path = tmp / "codex-log.jsonl"
            fake_make = tmp / "make"
            write_fake_make(fake_make)
            fake_codex = tmp / "fake_codex.py"
            write_fake_codex(fake_codex)
            repo_copy = self.copy_repo(tmp)
            framework = SkillAutomationFramework(
                repo_copy,
                codex_bin=str(fake_codex),
                state_dir=tmp / "state",
                reports_dir=tmp / "reports",
                codex_config_overrides=["features.apps=false"],
                stage_timeout=60,
                verification_timeout=300,
            )
            env = {"PATH": f"{tmp}:{os.environ['PATH']}", "FAKE_CODEX_LOG_PATH": str(log_path)}
            with patch.dict(os.environ, env, clear=False):
                framework.design_skill(
                    task_prompt="Design a skill for pathway triage.",
                    focus_limit=1,
                    verification_mode="none",
                    run_label="config-override-test",
                )
            entries = [
                json.loads(line)
                for line in log_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertGreater(len(entries), 0)
            self.assertIn("features.apps=false", entries[0]["configs"])

    def test_evaluate_skills_runs_layered_feedback_loops(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            fake_make = tmp / "make"
            write_fake_make(fake_make)
            framework, _ = self.make_framework(tmp)
            env = {"PATH": f"{tmp}:{os.environ['PATH']}"}
            with patch.dict(os.environ, env, clear=False):
                payload = framework.evaluate_skills(
                    skill_slugs=["openalex-literature-search"],
                    verification_mode="none",
                    layer1_fix_attempts=1,
                    layer2_optimize_attempts=1,
                )
            self.assertEqual(payload["mode"], "evaluate_skills")
            self.assertEqual(payload["evaluation_summary"]["selected_skill_count"], 1)
            self.assertEqual(payload["evaluation_summary"]["layer1_passed"], 1)
            self.assertEqual(payload["evaluation_summary"]["layer2_advantage_passed"], 1)
            self.assertEqual(payload["evaluation_summary"]["novelty_checked"], 1)
            self.assertTrue(payload["layer1"][0]["fix_attempts"])
            self.assertTrue(payload["layer2"][0]["optimize_attempts"])
            self.assertTrue(payload["layer2"][0]["meets_expectation"])
            self.assertEqual(payload["novelty"][0]["novelty"]["parsed_message"]["stage"], "novelty_check")
            latest_eval = tmp / "state" / "latest_evaluation.json"
            self.assertTrue(latest_eval.exists())

    def test_evaluate_skills_resumes_partial_run_without_repeating_finished_layers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            fake_make = tmp / "make"
            log_path = tmp / "resume-log.jsonl"
            write_fake_make(fake_make)
            framework, _ = self.make_framework(tmp)
            env = {"PATH": f"{tmp}:{os.environ['PATH']}", "FAKE_CODEX_LOG_PATH": str(log_path)}
            run_dir = tmp / "reports" / "resume-eval"
            with patch.dict(os.environ, env, clear=False):
                payload = framework.evaluate_skills(
                    skill_slugs=["openalex-literature-search", "europepmc-method-triage"],
                    workers=2,
                    verification_mode="none",
                    layer1_fix_attempts=1,
                    layer2_optimize_attempts=1,
                    run_dir=run_dir,
                )
            self.assertEqual(payload["evaluation_summary"]["selected_skill_count"], 2)
            (run_dir / "manifest.json").unlink()
            (run_dir / "skills" / "europepmc-method-triage" / "novelty" / "novelty_record.json").unlink()
            log_path.write_text("", encoding="utf-8")
            with patch.dict(os.environ, env, clear=False):
                resumed = framework.evaluate_skills(
                    skill_slugs=["openalex-literature-search", "europepmc-method-triage"],
                    workers=2,
                    verification_mode="none",
                    layer1_fix_attempts=1,
                    layer2_optimize_attempts=1,
                    run_dir=run_dir,
                )
            entries = [
                json.loads(line)
                for line in log_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(resumed["evaluation_summary"]["selected_skill_count"], 2)
            self.assertEqual([entry["stage"] for entry in entries], ["novelty_check"])
            self.assertEqual(entries[0]["skill_slug"], "europepmc-method-triage")

    def test_cli_evaluate_skills_emits_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_copy = self.copy_repo(tmp)
            fake_codex = tmp / "fake_codex.py"
            fake_make = tmp / "make"
            write_fake_codex(fake_codex)
            write_fake_make(fake_make)
            env = os.environ.copy()
            env["PATH"] = f"{tmp}:{env['PATH']}"
            completed = subprocess.run(
                [
                    "python3",
                    "scripts/sciskill_framework.py",
                    "--codex-bin",
                    str(fake_codex),
                    "--state-dir",
                    str(tmp / "state"),
                    "--reports-dir",
                    str(tmp / "reports"),
                    "--json",
                    "evaluate-skills",
                    "--skill-slug",
                    "openalex-literature-search",
                    "--verification-mode",
                    "none",
                ],
                cwd=repo_copy,
                env=env,
                check=True,
                capture_output=True,
                text=True,
                timeout=180,
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["evaluation_summary"]["selected_skill_count"], 1)
            self.assertEqual(payload["evaluation_summary"]["layer1_passed"], 1)
            self.assertEqual(payload["evaluation_summary"]["layer2_advantage_passed"], 1)

    def test_cli_status_emits_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_copy = self.copy_repo(Path(tmpdir))
            completed = subprocess.run(
                [
                    "python3",
                    "scripts/sciskill_framework.py",
                    "--state-dir",
                    str(Path(tmpdir) / "state"),
                    "--reports-dir",
                    str(Path(tmpdir) / "reports"),
                    "--json",
                    "status",
                    "--focus-limit",
                    "2",
                ],
                cwd=repo_copy,
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(len(payload["focus_leaves"]), 2)

    def test_cycle_parallel_workers_sync_and_background_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            fake_make = tmp / "make"
            write_fake_make(fake_make)
            framework, repo_copy = self.make_framework(tmp)
            env = {"PATH": f"{tmp}:{os.environ['PATH']}", "FAKE_CODEX_SLEEP_SECONDS": "0.1"}
            with patch.dict(os.environ, env, clear=False):
                payload = framework.run_cycle(
                    loops=1,
                    stages=["tree_check", "resource_search", "refresh"],
                    focus_limit=2,
                    stage_workers=2,
                    background_validation_limit=2,
                    background_validation_workers=2,
                    verification_mode="none",
                    run_label="parallel-cycle-test",
                )
            parallel_stage = next(record for record in payload["stage_results"] if record["stage"] == "resource_search")
            self.assertTrue(parallel_stage["parallel"])
            self.assertEqual(len(parallel_stage["worker_results"]), 2)
            self.assertIsNotNone(payload["background_validation"])
            self.assertEqual(payload["background_validation"]["selected_skill_count"], 2)
            self.assertIsNotNone(payload["workspace_sync"])
            self.assertGreaterEqual(len(payload["workspace_sync"]["synced_paths"]), 2)
            self.assertTrue((repo_copy / "tests" / "smoke" / "test_precision_agriculture_sensing.py").exists())

    def test_evaluate_skills_supports_parallel_workers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            fake_make = tmp / "make"
            write_fake_make(fake_make)
            framework, _ = self.make_framework(tmp)
            env = {"PATH": f"{tmp}:{os.environ['PATH']}"}
            with patch.dict(os.environ, env, clear=False):
                payload = framework.evaluate_skills(
                    skill_slugs=["openalex-literature-search", "europepmc-method-triage"],
                    workers=2,
                    verification_mode="none",
                    layer1_fix_attempts=1,
                    layer2_optimize_attempts=1,
                )
            self.assertEqual(payload["evaluation_summary"]["selected_skill_count"], 2)
            self.assertEqual(len(payload["layer1"]), 2)
            self.assertEqual(len(payload["novelty"]), 2)

    def test_campaign_runner_checkpoints_and_resumes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            fake_make = tmp / "make"
            write_fake_make(fake_make)
            framework, _ = self.make_framework(tmp)
            runner = FrameworkCampaignRunner(framework)
            env = {"PATH": f"{tmp}:{os.environ['PATH']}", "FAKE_CODEX_SLEEP_SECONDS": "0.05"}
            with patch.dict(os.environ, env, clear=False):
                first = runner.run_campaign(
                    label="campaign-test",
                    focus_terms=["precision agriculture", "cut run"],
                    cycle_focus_limit=2,
                    cycle_stage_workers=2,
                    background_validation_limit=1,
                    background_validation_workers=1,
                    evaluation_batch_size=1,
                    evaluation_workers=1,
                    layer1_fix_attempts=1,
                    layer2_optimize_attempts=1,
                    verification_mode="none",
                    max_iterations=1,
                    max_runtime_minutes=10,
                    stop_buffer_minutes=0,
                )
                first_count = first["campaign_summary"]["evaluated_skill_count"]
                second = runner.run_campaign(
                    label="campaign-test",
                    focus_terms=["precision agriculture", "cut run"],
                    cycle_focus_limit=2,
                    cycle_stage_workers=2,
                    background_validation_limit=1,
                    background_validation_workers=1,
                    evaluation_batch_size=1,
                    evaluation_workers=1,
                    layer1_fix_attempts=1,
                    layer2_optimize_attempts=1,
                    verification_mode="none",
                    max_iterations=2,
                    max_runtime_minutes=10,
                    stop_buffer_minutes=0,
                )
            self.assertEqual(first["label"], "campaign-test")
            self.assertTrue(Path(first["state_path"]).exists())
            self.assertTrue(Path(first["summary_path"]).exists())
            self.assertGreaterEqual(first_count, 1)
            self.assertGreaterEqual(second["campaign_summary"]["evaluated_skill_count"], first_count + 1)

    def test_campaign_runner_reconciles_partial_evaluation_before_starting_new_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            fake_make = tmp / "make"
            log_path = tmp / "campaign-resume-log.jsonl"
            write_fake_make(fake_make)
            framework, _ = self.make_framework(tmp)
            runner = FrameworkCampaignRunner(framework)
            env = {"PATH": f"{tmp}:{os.environ['PATH']}", "FAKE_CODEX_LOG_PATH": str(log_path)}
            with patch.dict(os.environ, env, clear=False):
                first = runner.run_campaign(
                    label="campaign-resume-test",
                    focus_terms=["precision agriculture", "cut run"],
                    cycle_focus_limit=2,
                    cycle_stage_workers=2,
                    background_validation_limit=1,
                    background_validation_workers=1,
                    evaluation_batch_size=2,
                    evaluation_workers=2,
                    layer1_fix_attempts=1,
                    layer2_optimize_attempts=1,
                    verification_mode="none",
                    max_iterations=1,
                    max_runtime_minutes=10,
                    stop_buffer_minutes=0,
                )
            state_path = Path(first["state_path"])
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["cycle_runs"] = []
            state["evaluation_runs"] = []
            state["completed_evaluations"] = {}
            state["designed_skill_slugs"] = []
            state["new_skill_slugs"] = []
            state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            eval_run_dir = sorted((tmp / "reports").glob("*-campaign-resume-test-eval-*"))[0]
            (eval_run_dir / "manifest.json").unlink()
            missing_novelty = sorted((eval_run_dir / "skills").iterdir())[0] / "novelty" / "novelty_record.json"
            missing_novelty.unlink()
            log_path.write_text("", encoding="utf-8")
            with patch.dict(os.environ, env, clear=False):
                resumed = runner.run_campaign(
                    label="campaign-resume-test",
                    focus_terms=["precision agriculture", "cut run"],
                    cycle_focus_limit=2,
                    cycle_stage_workers=2,
                    background_validation_limit=1,
                    background_validation_workers=1,
                    evaluation_batch_size=2,
                    evaluation_workers=2,
                    layer1_fix_attempts=1,
                    layer2_optimize_attempts=1,
                    verification_mode="none",
                    max_iterations=1,
                    max_runtime_minutes=10,
                    stop_buffer_minutes=0,
                )
            entries = [
                json.loads(line)
                for line in log_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual([entry["stage"] for entry in entries], ["novelty_check"])
            self.assertEqual(resumed["campaign_summary"]["cycle_runs_completed"], 1)
            self.assertGreaterEqual(resumed["campaign_summary"]["evaluated_skill_count"], 2)


if __name__ == "__main__":
    unittest.main()
