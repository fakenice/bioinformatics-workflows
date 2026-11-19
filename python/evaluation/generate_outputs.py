"""Generate Skill-output files for the evaluation harness — one command, both arms.

Until this script existed, results/outputs_qwen3_14b*.json were produced by
ad-hoc calls, which made the README Evaluation numbers impossible to re-derive
from the repo alone. This script closes that gap: the same model settings the
README documents (qwen3:14b, think=False, temperature=0.3) are encoded here,
and every run writes a sidecar meta file (model, arm, system-prompt sha256,
case count, timestamp) next to the outputs.

Protocol (recorded in the meta, not hard-coded into any report):
  - skill arm   : system prompt = verbatim SKILL.md (the shipped Skill);
  - noskill arm : neutral system prompt defined below — the ablation
    difference between arms therefore comes ONLY from SKILL.md text;
  - one call per test case, query verbatim, stream=False, no retrieval,
    no internet: the model may only use what its weights and the system
    prompt contain;
  - outputs are saved incrementally after every case (a mid-run failure
    keeps completed cases); rerunning skips case ids already present
    unless --restart is given.

Usage:
    python generate_outputs.py --arm skill   --out results/outputs_ext30_skill.json
    python generate_outputs.py --arm noskill --out results/outputs_ext30_noskill.json
Then:
    python runner.py results/outputs_ext30_skill.json
    python runner.py results/outputs_ext30_skill.json -b results/outputs_ext30_noskill.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_MD = ROOT.parent.parent / "SKILL.md"
OLLAMA = "http://localhost:11434/api/generate"

NEUTRAL_SYSTEM = (
    "You are a helpful bioinformatics assistant. Answer the user's question "
    "thoroughly, with concrete tools, parameters and references where you can. "
    "回答用户的生物信息学问题。"
)


def call(model: str, system: str, prompt: str, temperature: float, think: bool,
         timeout: int = 600, retries: int = 1) -> str:
    body = json.dumps({
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False,
        "think": think,
        "options": {"temperature": temperature},
    }).encode("utf-8")
    last_err: Exception | None = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(OLLAMA, data=body,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if "response" not in data:
                raise RuntimeError(f"ollama reply has no 'response' key: {list(data)}")
            return data["response"]
        except (urllib.error.URLError, TimeoutError, RuntimeError) as e:
            last_err = e
            if attempt < retries:
                time.sleep(5)
    raise RuntimeError(f"Ollama call failed after {retries + 1} attempts: {last_err}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["skill", "noskill"], required=True)
    ap.add_argument("--model", default="qwen3:14b")
    ap.add_argument("--temperature", type=float, default=0.3)
    ap.add_argument("--think", action="store_true",
                    help="enable thinking mode (default off, as the README protocol states)")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--cases", type=Path, default=ROOT / "benchmarks" / "test_cases.json")
    ap.add_argument("--restart", action="store_true", help="regenerate cases already in --out")
    args = ap.parse_args()

    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    if args.arm == "skill":
        system = SKILL_MD.read_text(encoding="utf-8")
    else:
        system = NEUTRAL_SYSTEM

    out_path: Path = args.out
    meta_path = out_path.with_name(out_path.stem + "_meta.json")
    outputs: dict[str, str] = {}
    if out_path.exists() and not args.restart:
        outputs = json.loads(out_path.read_text(encoding="utf-8"))
        print(f"[info] resuming: {len(outputs)} cases already in {out_path.name}")

    t_start = time.time()
    for i, c in enumerate(cases, 1):
        cid = c["id"]
        if cid in outputs:
            continue
        print(f"[{i:2d}/{len(cases)}] {cid} ...", end=" ", flush=True)
        t0 = time.time()
        reply = call(args.model, system, c["query"], args.temperature, args.think)
        outputs[cid] = reply
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(outputs, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{len(reply)} chars, {time.time() - t0:.1f}s")

    meta = {
        "model": args.model,
        "arm": args.arm,
        "system_prompt_sha256": hashlib.sha256(system.encode("utf-8")).hexdigest(),
        "system_prompt_chars": len(system),
        "temperature": args.temperature,
        "think": args.think,
        "n_cases": len(cases),
        "cases_file": str(args.cases.relative_to(ROOT.parent.parent)),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "wall_seconds_total_this_invocation": round(time.time() - t_start, 1),
        "endpoint": OLLAMA,
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nwrote {out_path} ({len(outputs)} cases) and {meta_path}")
    if len(outputs) != len(cases):
        print(f"[WARN] {len(cases) - len(outputs)} cases missing — rerun to resume", file=sys.stderr)


if __name__ == "__main__":
    main()
