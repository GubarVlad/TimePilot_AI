#!/usr/bin/env python3
"""TimePilot AI - Hackathon Entry Point.

Supports:
  1. CLI execution:
     python run.py --input input_examples/example_1.json [--output output.json]
  2. Programmatic API Server (for judges & web UI):
     python run.py --serve --port 8000
     (Or default `python run.py` which starts the HTTP server on port 8000)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.adapters.nightshift_adapter import NightshiftAIAdapter
from app.adapters.zetaris_adapter import ZetarisUSLAdapter
from app.agents.orchestrator import MultiAgentOrchestrator
from app.engines.hmem_engine import HMemEngine
from app.tracer import AgentTracer


def run_cli(input_path: str, output_path: str | None = None) -> int:
    """Run agent against structured JSON input file and output structured JSON."""
    file_path = Path(input_path)
    if not file_path.exists():
        print(f"Error: Input file '{input_path}' not found.", file=sys.stderr)
        return 1

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Error parsing input JSON: {exc}", file=sys.stderr)
        return 1

    message = data.get("message") or data.get("input") or data.get("prompt") or ""
    selected_date = data.get("selected_date") or data.get("date") or "2026-10-27"

    tracer = AgentTracer(echo_stdout=True)
    zetaris_usl = ZetarisUSLAdapter()
    hmem_engine = HMemEngine()
    ai_adapter = NightshiftAIAdapter()
    orchestrator = MultiAgentOrchestrator(
        zetaris_usl=zetaris_usl,
        hmem_engine=hmem_engine,
        ai_adapter=ai_adapter,
        tracer=tracer,
    )

    print(f"\n[TimePilot AI] Processing input: '{message}' on date {selected_date}...")
    result = orchestrator.process_request(message, selected_date)

    formatted_json = json.dumps(result, indent=2, ensure_ascii=False)
    print("\n--- Structured Result ---")
    print(formatted_json)

    if output_path:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(formatted_json, encoding="utf-8")
        print(f"\n[TimePilot AI] Saved output to '{output_path}'")

    return 0


def run_server(port: int = 8000, host: str = "0.0.0.0") -> None:
    """Run HTTP server exposing POST /run and full Web UI."""
    os.environ["PORT"] = str(port)
    os.environ["HOST"] = host
    from backend.app import main
    main()


def main_entry() -> None:
    parser = argparse.ArgumentParser(description="TimePilot AI Runner")
    parser.add_argument("--input", "-i", type=str, help="Path to input JSON file for CLI execution")
    parser.add_argument("--output", "-o", type=str, help="Path to write output JSON")
    parser.add_argument("--serve", "-s", action="store_true", help="Start the HTTP server")
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=int(os.getenv("PORT", "8000")),
        help="Port to bind server (default: 8000)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.getenv("HOST", "0.0.0.0"),
        help="Host to bind server (default: 0.0.0.0)",
    )

    args = parser.parse_args()

    if args.input:
        sys.exit(run_cli(args.input, args.output))
    else:
        run_server(port=args.port, host=args.host)


if __name__ == "__main__":
    main_entry()

