#!/usr/bin/env python3
"""Orchestrator: run the full SERP content-teardown pipeline end to end.

Runs the 8 step scripts in dependency order, threading the shared
--semrush-dir / --out-dir / --topics / --brand-names / --top flags through to
each. Each step is its own subprocess (same Python interpreter) so a failure is
reported with the failing step name and stops the run.

Pipeline order (data dependencies):
    1. parse_serp        -> url_pool.json
    2. fetch_competitors -> html/, fetch_manifest.json      (curl only, no paid APIs)
    3. analyze_structure -> results.json, prose_dump.txt
    4. classify_archetypes -> classified.json
    5. keyword_analysis  -> keywords.json
    6. backlink_analysis -> backlinks.json
    7. geo_analysis      -> (console; reads keywords.json + classified.json)
    8. onpage_analysis   -> onpage.json

Usage:
    python3 run_all.py --semrush-dir DIR --out-dir DIR --topics topic-clusters.yaml \
                       [--brand-names brand-names.json] [--top 30]

Arguments:
    --semrush-dir   Directory of SEMrush xlsx exports
    --out-dir       Output dir for all artifacts (created if missing)
    --topics        topic-clusters.yaml (see templates/)
    --brand-names   Optional domain->[variants] JSON (see templates/brand-names.json)
    --top           Articles to fetch, capped 2/domain (default: 30)
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def step(name, *script_args):
    """Run one pipeline script as a subprocess; abort the run if it fails."""
    script = os.path.join(HERE, name)
    cmd = [sys.executable, script, *script_args]
    print("\n" + "#" * 78)
    print(f"# {name}  {' '.join(script_args)}")
    print("#" * 78)
    r = subprocess.run(cmd)
    if r.returncode != 0:
        print(f"\n!! step failed: {name} (exit {r.returncode}) — stopping pipeline",
              file=sys.stderr)
        sys.exit(r.returncode)


def main():
    ap = argparse.ArgumentParser(
        description="Run the full SERP content-teardown pipeline (8 steps)")
    ap.add_argument("--semrush-dir", required=True,
                    help="Directory of SEMrush xlsx exports")
    ap.add_argument("--out-dir", required=True, help="Output dir for all artifacts")
    ap.add_argument("--topics", required=True, help="topic-clusters.yaml")
    ap.add_argument("--brand-names", metavar="FILE",
                    help="Optional domain->[variants] JSON")
    ap.add_argument("--top", type=int, default=30,
                    help="Articles to fetch, capped 2/domain (default: 30)")
    args = ap.parse_args()

    sem = os.path.expanduser(args.semrush_dir)
    out = args.out_dir
    os.makedirs(out, exist_ok=True)

    step("parse_serp.py", "--semrush-dir", sem, "--out-dir", out, "--topics", args.topics)
    step("fetch_competitors.py", "--out-dir", out, "--top", str(args.top))

    analyze_args = ["--out-dir", out]
    if args.brand_names:
        analyze_args += ["--brand-names", args.brand_names]
    step("analyze_structure.py", *analyze_args)

    step("classify_archetypes.py", "--out-dir", out)
    step("keyword_analysis.py", "--semrush-dir", sem, "--out-dir", out, "--topics", args.topics)
    step("backlink_analysis.py", "--semrush-dir", sem, "--out-dir", out, "--topics", args.topics)
    step("geo_analysis.py", "--semrush-dir", sem, "--out-dir", out)
    step("onpage_analysis.py", "--out-dir", out)

    print("\n" + "=" * 78)
    print(f"pipeline complete -> {out}")
    print("artifacts: url_pool.json, html/, fetch_manifest.json, results.json,")
    print("           prose_dump.txt, classified.json, keywords.json, backlinks.json, onpage.json")


if __name__ == "__main__":
    main()
