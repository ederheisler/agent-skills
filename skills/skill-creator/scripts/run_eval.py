#!/usr/bin/env python3
"""Run trigger evaluation for a skill description.

Tests whether a skill's description causes OpenCode to trigger (read the skill)
for a set of queries. Outputs results as JSON.
"""

import argparse
import json
import os
import subprocess
import sys
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from scripts.utils import parse_skill_md


def find_project_root() -> Path:
    """Find the project root by walking up from cwd looking for skill dirs.

    This keeps eval runs scoped to the expected project directory.
    """
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".opencode").is_dir() or (parent / ".claude").is_dir():
            return parent
    return current


def run_single_query(
    query: str,
    skill_name: str,
    skill_description: str,
    timeout: int,
    project_root: str,
    model: str | None = None,
) -> dict:
    """Run a single query and return trigger result plus usage metrics.

    Creates a temporary skill in .opencode/skills/ so it appears in OpenCode's
    available skills list, then runs `opencode run --format json` with
    the raw query and inspects tool_use events for that skill.
    """
    unique_id = uuid.uuid4().hex[:8]
    clean_name = f"{skill_name}-skill-{unique_id}"
    skill_dir = Path(project_root) / ".opencode" / "skills" / clean_name
    skill_file = skill_dir / "SKILL.md"

    try:
        skill_dir.mkdir(parents=True, exist_ok=True)
        # Use YAML block scalar to avoid breaking on quotes in description
        indented_desc = "\n  ".join(skill_description.split("\n"))
        skill_content = (
            f"---\nname: {clean_name}\ndescription: |\n  {indented_desc}\n---\n"
        )
        skill_file.write_text(skill_content)

        cmd = [
            "opencode",
            "run",
            "--format",
            "json",
            query,
        ]
        if model:
            cmd.extend(["--model", model])

        env = dict(os.environ)

        try:
            completed = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=project_root,
                env=env,
            )
        except subprocess.TimeoutExpired:
            return {
                "triggered": False,
                "tokens": {"total": 0, "input": 0, "output": 0, "reasoning": 0},
                "cost": 0.0,
            }

        usage_totals = {"total": 0, "input": 0, "output": 0, "reasoning": 0}
        total_cost = 0.0
        triggered = False
        session_id = None

        for line in completed.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            if session_id is None:
                sid = event.get("sessionID")
                if isinstance(sid, str) and sid:
                    session_id = sid

            event_type = event.get("type")

            if event_type == "step_finish":
                part = event.get("part", {})
                tokens = part.get("tokens", {})
                for key in usage_totals:
                    value = tokens.get(key, 0)
                    if isinstance(value, int):
                        usage_totals[key] += value
                cost = part.get("cost", 0)
                if isinstance(cost, (int, float)):
                    total_cost += float(cost)
                continue

            if event_type != "tool_use":
                continue

            part = event.get("part", {})
            tool_name = str(part.get("tool", "")).lower()
            if tool_name not in ("skill", "read"):
                continue

            part_json = json.dumps(part)
            if clean_name in part_json:
                triggered = True

        return {
            "triggered": triggered,
            "tokens": usage_totals,
            "cost": total_cost,
            "session_id": session_id,
        }
    finally:
        if skill_file.exists():
            skill_file.unlink()
        if skill_dir.exists() and not any(skill_dir.iterdir()):
            skill_dir.rmdir()


def run_eval(
    eval_set: list[dict],
    skill_name: str,
    description: str,
    num_workers: int,
    timeout: int,
    project_root: Path,
    runs_per_query: int = 1,
    trigger_threshold: float = 0.5,
    model: str | None = None,
) -> dict:
    """Run the full eval set and return results."""
    results = []

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        future_to_info = {}
        for item in eval_set:
            for run_idx in range(runs_per_query):
                future = executor.submit(
                    run_single_query,
                    item["query"],
                    skill_name,
                    description,
                    timeout,
                    str(project_root),
                    model,
                )
                future_to_info[future] = (item, run_idx)

        query_runs: dict[str, list[dict]] = {}
        query_items: dict[str, dict] = {}
        for future in as_completed(future_to_info):
            item, _ = future_to_info[future]
            query = item["query"]
            query_items[query] = item
            if query not in query_runs:
                query_runs[query] = []
            try:
                query_runs[query].append(future.result())
            except Exception as e:
                print(f"Warning: query failed: {e}", file=sys.stderr)
                query_runs[query].append(
                    {
                        "triggered": False,
                        "tokens": {"total": 0, "input": 0, "output": 0, "reasoning": 0},
                        "cost": 0.0,
                    }
                )

    total_tokens = {"total": 0, "input": 0, "output": 0, "reasoning": 0}
    total_cost = 0.0

    for query, run_stats in query_runs.items():
        item = query_items[query]
        trigger_bools = [bool(r.get("triggered", False)) for r in run_stats]
        trigger_rate = sum(trigger_bools) / len(trigger_bools)
        should_trigger = item["should_trigger"]
        if should_trigger:
            did_pass = trigger_rate >= trigger_threshold
        else:
            did_pass = trigger_rate < trigger_threshold

        query_tokens = {"total": 0, "input": 0, "output": 0, "reasoning": 0}
        query_cost = 0.0
        query_session_ids: list[str] = []
        for r in run_stats:
            tokens = r.get("tokens", {})
            for key in query_tokens:
                value = tokens.get(key, 0)
                if isinstance(value, int):
                    query_tokens[key] += value
            cost = r.get("cost", 0)
            if isinstance(cost, (int, float)):
                query_cost += float(cost)
            session_id = r.get("session_id")
            if isinstance(session_id, str) and session_id:
                query_session_ids.append(session_id)

        for key in total_tokens:
            total_tokens[key] += query_tokens[key]
        total_cost += query_cost

        results.append(
            {
                "query": query,
                "should_trigger": should_trigger,
                "trigger_rate": trigger_rate,
                "triggers": sum(trigger_bools),
                "runs": len(trigger_bools),
                "pass": did_pass,
                "token_usage": query_tokens,
                "cost": query_cost,
                "session_ids": query_session_ids,
            }
        )

    passed = sum(1 for r in results if r["pass"])
    total = len(results)

    return {
        "skill_name": skill_name,
        "description": description,
        "results": results,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "token_usage": total_tokens,
            "cost": total_cost,
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Run trigger evaluation for a skill description"
    )
    parser.add_argument("--eval-set", required=True, help="Path to eval set JSON file")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument(
        "--description", default=None, help="Override description to test"
    )
    parser.add_argument(
        "--num-workers", type=int, default=10, help="Number of parallel workers"
    )
    parser.add_argument(
        "--timeout", type=int, default=30, help="Timeout per query in seconds"
    )
    parser.add_argument(
        "--runs-per-query", type=int, default=3, help="Number of runs per query"
    )
    parser.add_argument(
        "--trigger-threshold", type=float, default=0.5, help="Trigger rate threshold"
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Model to use for opencode run (default: user's configured model)",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print progress to stderr"
    )
    args = parser.parse_args()

    eval_set = json.loads(Path(args.eval_set).read_text())
    skill_path = Path(args.skill_path)

    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    name, original_description, content = parse_skill_md(skill_path)
    description = args.description or original_description
    project_root = find_project_root()

    if args.verbose:
        print(f"Evaluating: {description}", file=sys.stderr)

    output = run_eval(
        eval_set=eval_set,
        skill_name=name,
        description=description,
        num_workers=args.num_workers,
        timeout=args.timeout,
        project_root=project_root,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        model=args.model,
    )

    if args.verbose:
        summary = output["summary"]
        print(
            f"Results: {summary['passed']}/{summary['total']} passed", file=sys.stderr
        )
        for r in output["results"]:
            status = "PASS" if r["pass"] else "FAIL"
            rate_str = f"{r['triggers']}/{r['runs']}"
            print(
                f"  [{status}] rate={rate_str} expected={r['should_trigger']}: {r['query'][:70]}",
                file=sys.stderr,
            )

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
